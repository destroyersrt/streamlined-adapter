#!/bin/bash

# 60-Domain Agents Deployment Script
# Replica of aws-multi-agent-deployment.sh for domain testing
# Deploys 60 agents (4 topics × 3 structures × 5 agents) on single EC2 instance

set -e

# Parse arguments
ANTHROPIC_API_KEY="$1"
AGENT_CONFIG_JSON="${2:-scripts/domain_agents_config.json}"
REGISTRY_URL="${3:-http://capregistry.duckdns.org:6900}"
REGION="${4:-us-east-1}"
INSTANCE_TYPE="${5:-t3.xlarge}"  # Large instance for 60 agents

# Validation
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "❌ Usage: $0 <ANTHROPIC_API_KEY> [AGENT_CONFIG_JSON] [REGISTRY_URL] [REGION] [INSTANCE_TYPE]"
    echo ""
    echo "Example:"
    echo "  $0 sk-ant-api03-... scripts/domain_agents_config.json http://capregistry.duckdns.org:6900 us-east-1 t3.xlarge"
    echo ""
    echo "Default config: scripts/domain_agents_config.json"
    echo "Default registry: http://capregistry.duckdns.org:6900"
    echo "Default instance: t3.xlarge (recommended for 60 agents)"
    exit 1
fi

echo "🚀 60-Domain Agents Deployment"
echo "=============================="
echo "Config: $AGENT_CONFIG_JSON"
echo "Registry: $REGISTRY_URL"
echo "Region: $REGION"
echo "Instance: $INSTANCE_TYPE"
echo ""

# Parse and validate agent config
if [ -f "$AGENT_CONFIG_JSON" ]; then
    AGENTS_JSON=$(cat "$AGENT_CONFIG_JSON")
else
    echo "❌ Config file not found: $AGENT_CONFIG_JSON"
    exit 1
fi

AGENT_COUNT=$(echo "$AGENTS_JSON" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))")
echo "📊 Agents to deploy: $AGENT_COUNT"

# Validate expected count
if [ "$AGENT_COUNT" -ne 60 ]; then
    echo "⚠️  WARNING: Expected 60 agents, found $AGENT_COUNT"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Validate instance type for agent count
if [ "$AGENT_COUNT" -gt 30 ] && [ "$INSTANCE_TYPE" = "t3.large" ]; then
    echo "⚠️  WARNING: t3.large may be insufficient for $AGENT_COUNT agents. Consider t3.xlarge or larger."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Validate port uniqueness
echo "🔍 Validating port configuration..."
DUPLICATE_PORTS=$(echo "$AGENTS_JSON" | python3 -c "
import json, sys
from collections import Counter
agents = json.load(sys.stdin)
ports = [agent['port'] for agent in agents]
duplicates = [port for port, count in Counter(ports).items() if count > 1]
if duplicates:
    print(' '.join(map(str, duplicates)))
    sys.exit(1)
")

if [ $? -eq 1 ]; then
    echo "❌ Duplicate ports found: $DUPLICATE_PORTS"
    exit 1
fi

# Validate port range (6000-6059)
echo "🔍 Validating port range (6000-6059)..."
INVALID_PORTS=$(echo "$AGENTS_JSON" | python3 -c "
import json, sys
agents = json.load(sys.stdin)
invalid = [agent['port'] for agent in agents if agent['port'] < 6000 or agent['port'] > 6059]
if invalid:
    print(' '.join(map(str, invalid)))
    sys.exit(1)
")

if [ $? -eq 1 ]; then
    echo "❌ Invalid ports (must be 6000-6059): $INVALID_PORTS"
    exit 1
fi

echo "✅ Port configuration valid"

# Configuration
SECURITY_GROUP_NAME="nanda-60-domain-agents"
KEY_NAME="nanda-60-domain-agents-key"
AMI_ID="ami-0866a3c8686eaeeba"  # Ubuntu 24.04 LTS
DEPLOYMENT_ID=$(date +%Y%m%d-%H%M%S)

echo ""
echo "🔧 Deployment Configuration:"
echo "Security Group: $SECURITY_GROUP_NAME"
echo "Key Name: $KEY_NAME"
echo "AMI ID: $AMI_ID"
echo "Deployment ID: $DEPLOYMENT_ID"
echo ""

# AWS setup
echo "[1/6] Checking AWS credentials..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

# Verify we're using nanda-manager profile
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
if [ "$ACCOUNT_ID" != "339712887618" ]; then
    echo "❌ Wrong AWS account: $ACCOUNT_ID (expected: 339712887618)"
    echo "Set AWS_PROFILE=nanda-manager or run: aws configure --profile nanda-manager"
    exit 1
fi

echo "✅ Using nanda-manager account: $ACCOUNT_ID"

# Security group setup
echo "[2/6] Setting up security group..."
if ! aws ec2 describe-security-groups --group-names "$SECURITY_GROUP_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "Creating security group..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for 60-domain-agents deployment" \
        --region "$REGION" \
        --query 'GroupId' \
        --output text)
    
    # SSH access
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port 22 \
        --cidr 0.0.0.0/0 \
        --region "$REGION"
else
    SECURITY_GROUP_ID=$(aws ec2 describe-security-groups \
        --group-names "$SECURITY_GROUP_NAME" \
        --region "$REGION" \
        --query 'SecurityGroups[0].GroupId' \
        --output text)
fi

# Open agent ports (6000-6059)
echo "🔓 Opening ports for 60 agents (6000-6059)..."
for PORT in {6000..6059}; do
    if ! aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port "$PORT" \
        --cidr 0.0.0.0/0 \
        --region "$REGION" 2>/dev/null; then
        # Port already open, continue silently
        :
    fi
done

echo "✅ All agent ports opened"

# Key pair setup
echo "[3/6] Setting up key pair..."
if [ ! -f "${KEY_NAME}.pem" ]; then
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --region "$REGION" \
        --query 'KeyMaterial' \
        --output text > "${KEY_NAME}.pem"
    chmod 600 "${KEY_NAME}.pem"
    echo "✅ Created new key pair: ${KEY_NAME}.pem"
else
    echo "✅ Using existing key pair: ${KEY_NAME}.pem"
fi

# Create user data script for 60 domain agents
echo "[4/6] Creating user data script for 60 domain agents..."
cat > "user_data_60_domain_${DEPLOYMENT_ID}.sh" << EOF
#!/bin/bash
exec > /var/log/user-data.log 2>&1

echo "=== 60-Domain Agents Setup Started: $DEPLOYMENT_ID ==="
date

# Update system and install dependencies
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git curl jq supervisor htop

# Setup project
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/destroyersrt/NEST.git nanda-60-domain-agents
cd nanda-60-domain-agents

# Setup Python environment
sudo -u ubuntu python3 -m venv env
sudo -u ubuntu bash -c "source env/bin/activate && pip install --upgrade pip"
sudo -u ubuntu bash -c "source env/bin/activate && pip install -e ."
sudo -u ubuntu bash -c "source env/bin/activate && pip install anthropic pymongo python-dotenv psutil transformers torch"

# Get public IP using IMDSv2
echo "Getting public IP address using IMDSv2..."
for attempt in {1..5}; do
    TOKEN=\$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" --connect-timeout 5 --max-time 10)
    if [ -n "\$TOKEN" ]; then
        PUBLIC_IP=\$(curl -s -H "X-aws-ec2-metadata-token: \$TOKEN" --connect-timeout 5 --max-time 10 http://169.254.169.254/latest/meta-data/public-ipv4)
        if [ -n "\$PUBLIC_IP" ] && [[ \$PUBLIC_IP =~ ^[0-9]+\\.[0-9]+\\.[0-9]+\\.[0-9]+\$ ]]; then
            echo "Retrieved public IP: \$PUBLIC_IP"
            break
        fi
    fi
    echo "Attempt \$attempt failed, retrying..."
    sleep 3
done

if [ -z "\$PUBLIC_IP" ]; then
    echo "ERROR: Could not retrieve public IP"
    exit 1
fi

# Agent configuration will be uploaded separately via SCP
echo "Agent configuration will be uploaded via SCP after instance launch"

# Create environment file for agents
cat > /home/ubuntu/nanda-60-domain-agents/.env << 'ENV_EOF'
ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
REGISTRY_URL=$REGISTRY_URL
MONGODB_AGENTFACTS_URI=mongodb+srv://adityasharmasrt_db_user:V4036f6X0xO4qJ0W@nanda.wui3ygq.mongodb.net/
MONGODB_TELEMETRY_URI=mongodb+srv://adityasharmasrt_db_user:V4036f6X0xO4qJ0W@nanda.wui3ygq.mongodb.net/
ENV_EOF

sudo chown ubuntu:ubuntu /home/ubuntu/nanda-60-domain-agents/.env

# Prepare supervisor (agents will be configured via SSH after launch)
echo "Preparing supervisor for 60 domain agents..."
systemctl enable supervisor
systemctl start supervisor

echo "=== 60-Domain Agents Setup Complete: $DEPLOYMENT_ID ==="
echo "All 60 domain agents managed by supervisor on: \$PUBLIC_IP"
echo "Ports: 6000-6059"

EOF

# Launch instance
echo "[5/6] Launching EC2 instance ($INSTANCE_TYPE)..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --count 1 \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SECURITY_GROUP_ID" \
    --region "$REGION" \
    --user-data "file://user_data_60_domain_${DEPLOYMENT_ID}.sh" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=nanda-60-domain-$DEPLOYMENT_ID},{Key=Project,Value=NANDA-60-Domain-Agents},{Key=DeploymentId,Value=$DEPLOYMENT_ID}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance
echo "[6/6] Waiting for instance and deployment..."
aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
PUBLIC_IP=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "✅ Instance running at: $PUBLIC_IP"
echo ""
echo "⏳ Waiting for 60-agent deployment (8 minutes for proper startup)..."
echo "   This includes: git clone, pip install, supervisor setup, and agent registration"

# Show progress dots
for i in {1..48}; do
    sleep 10
    echo -n "."
done
echo ""

# Upload agent configuration and create supervisor configs
echo ""
echo "📤 Uploading agent configuration and setting up supervisor..."

# Upload agent config
scp -i "${KEY_NAME}.pem" -o StrictHostKeyChecking=no \
    "$AGENT_CONFIG_JSON" ubuntu@$PUBLIC_IP:/tmp/agents_config.json

# Create supervisor configurations remotely
ssh -i "${KEY_NAME}.pem" -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP << 'REMOTE_SETUP'
# Create supervisor configurations for each agent
while IFS= read -r agent_config; do
    AGENT_ID=$(echo "$agent_config" | jq -r '.agent_id')
    AGENT_NAME=$(echo "$agent_config" | jq -r '.agent_name')
    DOMAIN=$(echo "$agent_config" | jq -r '.domain')
    STRUCTURE_TYPE=$(echo "$agent_config" | jq -r '.structure_type')
    SPECIALIZATION=$(echo "$agent_config" | jq -r '.specialization')
    DESCRIPTION=$(echo "$agent_config" | jq -r '.description')
    CAPABILITIES=$(echo "$agent_config" | jq -r '.capabilities | join(",")')
    SYSTEM_PROMPT=$(echo "$agent_config" | jq -r '.system_prompt')
    QUESTIONS=$(echo "$agent_config" | jq -c '.questions')
    PORT=$(echo "$agent_config" | jq -r '.port')
    
    echo "Creating supervisor config for: $AGENT_ID ($DOMAIN/$STRUCTURE_TYPE)"
    
    # Create supervisor configuration file
    sudo tee "/etc/supervisor/conf.d/agent_$AGENT_ID.conf" > /dev/null << SUPERVISOR_EOF
[program:agent_$AGENT_ID]
command=/home/ubuntu/nanda-60-domain-agents/env/bin/python examples/enhanced_nanda_agent.py
directory=/home/ubuntu/nanda-60-domain-agents
user=ubuntu
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/agent_$AGENT_ID.err.log
stdout_logfile=/var/log/agent_$AGENT_ID.out.log
environment=
    ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY",
    AGENT_ID="$AGENT_ID",
    AGENT_NAME="$AGENT_NAME",
    AGENT_DOMAIN="$DOMAIN",
    AGENT_STRUCTURE_TYPE="$STRUCTURE_TYPE",
    AGENT_SPECIALIZATION="$SPECIALIZATION",
    AGENT_DESCRIPTION="$DESCRIPTION",
    AGENT_CAPABILITIES="$CAPABILITIES",
    AGENT_SYSTEM_PROMPT="$SYSTEM_PROMPT",
    AGENT_QUESTIONS='$QUESTIONS',
    REGISTRY_URL="$REGISTRY_URL",
    PUBLIC_URL="http://$PUBLIC_IP:$PORT",
    PORT="$PORT",
    MONGODB_AGENTFACTS_URI="mongodb+srv://adityasharmasrt_db_user:V4036f6X0xO4qJ0W@nanda.wui3ygq.mongodb.net/",
    MONGODB_TELEMETRY_URI="mongodb+srv://adityasharmasrt_db_user:V4036f6X0xO4qJ0W@nanda.wui3ygq.mongodb.net/"

SUPERVISOR_EOF
    
done < <(cat /tmp/agents_config.json | jq -c '.[]')

# Reload supervisor and start all agents
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start all

echo "✅ All 60 agents configured and starting"
REMOTE_SETUP

# Cleanup
rm "user_data_60_domain_${DEPLOYMENT_ID}.sh"

# Health check sample agents
echo ""
echo "🔍 Performing health checks on sample agents..."
SAMPLE_PORTS="6000 6015 6030 6045"  # One from each domain
for PORT in $SAMPLE_PORTS; do
    echo -n "Checking port $PORT... "
    if curl -s --connect-timeout 5 "http://$PUBLIC_IP:$PORT/health" >/dev/null 2>&1; then
        echo "✅ Healthy"
    else
        echo "⚠️  Not responding"
    fi
done

echo ""
echo "🎉 60-Domain Agents Deployment Complete!"
echo "========================================"
echo "Deployment ID: $DEPLOYMENT_ID"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Instance Type: $INSTANCE_TYPE"
echo ""

# Display agent summary by domain and structure
echo "📊 Agent Summary:"
echo "$AGENTS_JSON" | python3 -c "
import json, sys
from collections import defaultdict
agents = json.load(sys.stdin)

by_domain = defaultdict(lambda: defaultdict(list))
for agent in agents:
    domain = agent['domain']
    structure = agent['structure_type']
    by_domain[domain][structure].append(agent['port'])

for domain, structures in by_domain.items():
    print(f'{domain.replace(\"_\", \" \").title()}:')
    for structure, ports in structures.items():
        print(f'  {structure}: {len(ports)} agents (ports {min(ports)}-{max(ports)})')
    print()
"

echo "🤖 Sample Agent URLs (one per domain):"
echo "  Data Science:    http://$PUBLIC_IP:6000/a2a"
echo "  Web Development: http://$PUBLIC_IP:6015/a2a"
echo "  Healthcare:      http://$PUBLIC_IP:6030/a2a"
echo "  Finance:         http://$PUBLIC_IP:6045/a2a"
echo ""

echo "🔍 Test semantic search:"
echo "  curl -X POST http://$PUBLIC_IP:6000/a2a -H 'Content-Type: application/json' -d '{\"content\":{\"text\":\"? data analysis expert\",\"type\":\"text\"},\"role\":\"user\",\"conversation_id\":\"test\"}'"
echo ""

echo "📊 Monitor all agents:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo supervisorctl status'"
echo ""

echo "🔄 Restart all agents:"
echo "  ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo supervisorctl restart all'"
echo ""

echo "🛑 To terminate:"
echo "  aws ec2 terminate-instances --region $REGION --instance-ids $INSTANCE_ID"
echo ""

echo "🎯 Next Steps:"
echo "1. Wait 2-3 more minutes for all agents to fully register"
echo "2. Test agent discovery with different structure types:"
echo "   - ?keywords data science"
echo "   - ?description web development" 
echo "   - ?embedding healthcare"
echo "3. Run domain-specific testing flow"
echo ""

echo "✨ Your 60-domain agent network is ready for capability structure testing!"
