#!/bin/bash

# Multi-Agent AWS EC2 Deployment Script
# This script creates an EC2 instance and deploys multiple NANDA agents on a single instance
# Usage: bash aws-ec2-deploy-multi-agent.sh <ANTHROPIC_API_KEY> <AGENT_CONFIG_JSON> [REGISTRY_URL] [REGION] [INSTANCE_TYPE]

set -e

# Parse arguments
ANTHROPIC_API_KEY="$1"
AGENT_CONFIG_JSON="$2"
REGISTRY_URL="${3:-}"
REGION="${4:-us-east-1}"
INSTANCE_TYPE="${5:-t3.small}"

# Validate inputs
if [ -z "$ANTHROPIC_API_KEY" ] || [ -z "$AGENT_CONFIG_JSON" ]; then
    echo "❌ Usage: $0 <ANTHROPIC_API_KEY> <AGENT_CONFIG_JSON> [REGISTRY_URL] [REGION] [INSTANCE_TYPE]"
    echo ""
    echo "Example agent config JSON:"
    echo '['
    echo '  {'
    echo '    "agent_id": "data-scientist-001",'
    echo '    "agent_name": "Dr. Data",'
    echo '    "domain": "data analysis",'
    echo '    "specialization": "analytical and precise AI assistant",'
    echo '    "description": "I specialize in data analysis and statistics.",'
    echo '    "capabilities": "data analysis,statistics,machine learning,Python,R",'
    echo '    "port": 6000'
    echo '  },'
    echo '  {'
    echo '    "agent_id": "tech-support-001",'
    echo '    "agent_name": "TechWiz",'
    echo '    "domain": "technical support",'
    echo '    "specialization": "patient and knowledgeable tech specialist",'
    echo '    "description": "I help with troubleshooting and technical issues.",'
    echo '    "capabilities": "troubleshooting,software installation,network configuration",'
    echo '    "port": 6001'
    echo '  }'
    echo ']'
    echo ""
    echo "Parameters:"
    echo "  ANTHROPIC_API_KEY: Your Anthropic API key"
    echo "  AGENT_CONFIG_JSON: JSON string or file path containing agent configurations"
    echo "  REGISTRY_URL: Optional registry URL for agent discovery"
    echo "  REGION: AWS region (default: us-east-1)"
    echo "  INSTANCE_TYPE: EC2 instance type (default: t3.small for multiple agents)"
    exit 1
fi

echo "🚀 Multi-Agent AWS EC2 Deployment"
echo "=================================="
echo "Registry URL: ${REGISTRY_URL:-"None"}"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo ""

# Parse agent config (either JSON string or file)
if [ -f "$AGENT_CONFIG_JSON" ]; then
    echo "Reading agent config from file: $AGENT_CONFIG_JSON"
    AGENTS_JSON=$(cat "$AGENT_CONFIG_JSON")
else
    echo "Using agent config from command line"
    AGENTS_JSON="$AGENT_CONFIG_JSON"
fi

# Validate JSON and extract agent info
echo "Validating agent configuration..."
if ! echo "$AGENTS_JSON" | python3 -m json.tool >/dev/null 2>&1; then
    echo "❌ Invalid JSON format in agent configuration"
    exit 1
fi

# Extract ports and agent IDs for security group setup
AGENT_PORTS=$(echo "$AGENTS_JSON" | python3 -c "
import json, sys
agents = json.load(sys.stdin)
ports = [str(agent['port']) for agent in agents]
print(' '.join(ports))
")

AGENT_IDS=$(echo "$AGENTS_JSON" | python3 -c "
import json, sys
agents = json.load(sys.stdin)
ids = [agent['agent_id'] for agent in agents]
print(' '.join(ids))
")

echo "Agents to deploy: $AGENT_IDS"
echo "Ports to open: $AGENT_PORTS"

# Configuration
SECURITY_GROUP_NAME="nanda-multi-agents"
KEY_NAME="nanda-multi-agent-key"
AMI_ID="ami-0866a3c8686eaeeba"  # Ubuntu 22.04 LTS
DEPLOYMENT_ID=$(date +%Y%m%d-%H%M%S)

# Check AWS credentials
echo "[1/6] Checking AWS credentials..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi
echo "✅ AWS credentials valid"

# Setup security group
echo "[2/6] Setting up security group..."
if ! aws ec2 describe-security-groups --group-names "$SECURITY_GROUP_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "Creating security group..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for NANDA multi-agent deployment" \
        --region "$REGION" \
        --query 'GroupId' \
        --output text)
    
    # Open SSH port
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

# Open all agent ports
echo "Opening ports for agents..."
for PORT in $AGENT_PORTS; do
    aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port "$PORT" \
        --cidr 0.0.0.0/0 \
        --region "$REGION" 2>/dev/null || echo "Port $PORT already open"
done

echo "✅ Security group: $SECURITY_GROUP_ID"

# Setup key pair
echo "[3/6] Setting up key pair..."
if [ ! -f "${KEY_NAME}.pem" ]; then
    echo "Creating key pair..."
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --region "$REGION" \
        --query 'KeyMaterial' \
        --output text > "${KEY_NAME}.pem"
    chmod 600 "${KEY_NAME}.pem"
fi
echo "✅ Key pair: $KEY_NAME"

# Create user data script for multi-agent deployment
echo "[4/6] Creating user data script..."
cat > "user_data_multi_agent_${DEPLOYMENT_ID}.sh" << EOF
#!/bin/bash
exec > /var/log/user-data.log 2>&1

echo "=== Multi-Agent NANDA Setup Started: $DEPLOYMENT_ID ==="
date

# Update system and install dependencies
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git curl jq supervisor

# Setup project as ubuntu user
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/destroyersrt/streamlined-adapter.git nanda-multi-agents
cd nanda-multi-agents

# Create virtual environment and install
sudo -u ubuntu python3 -m venv env
sudo -u ubuntu bash -c "source env/bin/activate && pip install --upgrade pip && pip install -e . && pip install anthropic"

# Get public IP using IMDSv2 (AWS metadata service v2)
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

# Parse agent configuration and create individual agent scripts
echo '$AGENTS_JSON' > /tmp/agents_config.json

# Create supervisor configuration directory
mkdir -p /etc/supervisor/conf.d

# Generate supervisor configs and start scripts for each agent
python3 << 'PYTHON_SCRIPT'
import json
import os

with open('/tmp/agents_config.json', 'r') as f:
    agents = json.load(f)

for agent in agents:
    agent_id = agent['agent_id']
    agent_name = agent['agent_name']
    domain = agent['domain']
    specialization = agent['specialization']
    description = agent['description']
    capabilities = agent['capabilities']
    port = agent['port']
    
    # Create individual start script for this agent
    start_script = "/home/ubuntu/start_agent_{}.sh".format(agent_id.replace('-', '_'))
    with open(start_script, 'w') as f:
        f.write("""#!/bin/bash
cd /home/ubuntu/nanda-multi-agents
source env/bin/activate

export PUBLIC_IP=\$(curl -s -H "X-aws-ec2-metadata-token: \$(curl -s -X PUT 'http://169.254.169.254/latest/api/token' -H 'X-aws-ec2-metadata-token-ttl-seconds: 21600')" http://169.254.169.254/latest/meta-data/public-ipv4)
export PUBLIC_URL="http://\$PUBLIC_IP:{port}"
export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'
export AGENT_ID='{agent_id}'
export AGENT_NAME='{agent_name}'
export AGENT_DOMAIN='{domain}'
export AGENT_SPECIALIZATION='{specialization}'
export AGENT_DESCRIPTION='{description}'
export AGENT_CAPABILITIES='{capabilities}'
export REGISTRY_URL='$REGISTRY_URL'

echo "Starting agent {agent_id} on port {port}"
echo "Public URL: \$PUBLIC_URL"

python3 examples/modular_agent.py
""".format(port=port, agent_id=agent_id, agent_name=agent_name, domain=domain, specialization=specialization, description=description, capabilities=capabilities))
    
    # Make script executable
    os.chmod(start_script, 0o755)
    
    # Create supervisor configuration for this agent
    supervisor_conf = "/etc/supervisor/conf.d/nanda_agent_{}.conf".format(agent_id.replace('-', '_'))
    with open(supervisor_conf, 'w') as f:
        f.write("""[program:nanda_agent_{safe_id}]
command={start_script}
user=ubuntu
directory=/home/ubuntu/nanda-multi-agents
autostart=true
autorestart=true
stderr_logfile=/home/ubuntu/nanda-multi-agents/agent_{agent_id}_error.log
stdout_logfile=/home/ubuntu/nanda-multi-agents/agent_{agent_id}_output.log
environment=HOME="/home/ubuntu",USER="ubuntu"
""".format(safe_id=agent_id.replace('-', '_'), start_script=start_script, agent_id=agent_id))

print("Created configurations for all agents")
PYTHON_SCRIPT

# Change ownership of all agent scripts to ubuntu
chown ubuntu:ubuntu /home/ubuntu/start_agent_*.sh

# Reload supervisor and start all agents
supervisorctl reread
supervisorctl update
supervisorctl start all

# Wait a moment for agents to start
sleep 10

# Show status
echo "=== Agent Status ==="
supervisorctl status

echo "=== Multi-Agent NANDA Setup Complete: $DEPLOYMENT_ID ==="
echo "All agents should be running. Check logs in /home/ubuntu/nanda-multi-agents/"

# Display agent URLs
python3 << 'PYTHON_SCRIPT'
import json

with open('/tmp/agents_config.json', 'r') as f:
    agents = json.load(f)

print("\\n=== Agent URLs ===")
for agent in agents:
    public_ip = "\$(curl -s -H 'X-aws-ec2-metadata-token: \$(curl -s -X PUT \"http://169.254.169.254/latest/api/token\" -H \"X-aws-ec2-metadata-token-ttl-seconds: 21600\")' http://169.254.169.254/latest/meta-data/public-ipv4)"
    print("Agent {}: http://{}:{}/a2a".format(agent['agent_id'], public_ip, agent['port']))
PYTHON_SCRIPT

EOF

# Launch EC2 instance
echo "[5/6] Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --count 1 \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SECURITY_GROUP_ID" \
    --region "$REGION" \
    --user-data "file://user_data_multi_agent_${DEPLOYMENT_ID}.sh" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=nanda-multi-agents-$DEPLOYMENT_ID},{Key=Project,Value=NANDA-Multi-Agent},{Key=DeploymentId,Value=$DEPLOYMENT_ID}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance
echo "[6/6] Waiting for instance to be ready..."
aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
PUBLIC_IP=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "Waiting for multi-agent deployment (3-4 minutes)..."
sleep 180

# Cleanup
rm "user_data_multi_agent_${DEPLOYMENT_ID}.sh"

echo ""
echo "🎉 Multi-Agent NANDA Deployment Complete!"
echo "=========================================="
echo "Deployment ID: $DEPLOYMENT_ID"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo ""

# Display all agent URLs
echo "🤖 Agent URLs:"
echo "$AGENTS_JSON" | python3 -c "
import json, sys
agents = json.load(sys.stdin)
for agent in agents:
    print(f\"  {agent['agent_id']}: http://$PUBLIC_IP:{agent['port']}/a2a\")
"

echo ""
echo "🧪 Test any agent (example with first agent):"
FIRST_PORT=$(echo "$AGENTS_JSON" | python3 -c "
import json, sys
agents = json.load(sys.stdin)
print(agents[0]['port'])
")

echo "curl -X POST http://$PUBLIC_IP:$FIRST_PORT/a2a \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"content\":{\"text\":\"hello\",\"type\":\"text\"},\"role\":\"user\",\"conversation_id\":\"test123\"}'"

echo ""
echo "🔐 SSH Access:"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"

echo ""
echo "📊 Monitor agents:"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo supervisorctl status'"

echo ""
echo "📋 View agent logs:"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'cd nanda-multi-agents && ls -la *.log'"

echo ""
echo "🛑 To terminate:"
echo "aws ec2 terminate-instances --region $REGION --instance-ids $INSTANCE_ID"

echo ""
echo "📝 Agent Configuration Used:"
echo "$AGENTS_JSON" | python3 -m json.tool

