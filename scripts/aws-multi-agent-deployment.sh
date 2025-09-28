#!/bin/bash

# Improved Single Instance Multi-Agent Deployment Script
# This version addresses the critical issues in the original script

set -e

# Parse arguments (same as original)
ANTHROPIC_API_KEY="$1"
AGENT_CONFIG_JSON="$2"
REGISTRY_URL="${3:-http://registry.chat39.com:6900}"
REGION="${4:-us-east-1}"
INSTANCE_TYPE="${5:-t3.large}"  # Upgraded for 10 agents

# Validation (same as original)
if [ -z "$ANTHROPIC_API_KEY" ] || [ -z "$AGENT_CONFIG_JSON" ]; then
    echo "❌ Usage: $0 <ANTHROPIC_API_KEY> <AGENT_CONFIG_JSON> [REGISTRY_URL] [REGION] [INSTANCE_TYPE]"
    exit 1
fi

# Parse and validate agent config (same as original)
if [ -f "$AGENT_CONFIG_JSON" ]; then
    AGENTS_JSON=$(cat "$AGENT_CONFIG_JSON")
else
    AGENTS_JSON="$AGENT_CONFIG_JSON"
fi

AGENT_COUNT=$(echo "$AGENTS_JSON" | python3 -c "import json, sys; print(len(json.load(sys.stdin)))")
echo "Agents to deploy: $AGENT_COUNT"

# Validate instance type for agent count
if [ "$AGENT_COUNT" -gt 5 ] && [ "$INSTANCE_TYPE" = "t3.medium" ]; then
    echo "⚠️  WARNING: t3.medium may be insufficient for $AGENT_COUNT agents. Consider t3.large or larger."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Validate port uniqueness
echo "Validating port configuration..."
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

# Configuration
SECURITY_GROUP_NAME="nanda-single-multi-agents"
KEY_NAME="nanda-single-multi-agent-key"
AMI_ID="ami-0866a3c8686eaeeba"
DEPLOYMENT_ID=$(date +%Y%m%d-%H%M%S)

# AWS setup (same as original but with improved error handling)
echo "[1/6] Checking AWS credentials..."
if ! aws sts get-caller-identity >/dev/null 2>&1; then
    echo "❌ AWS credentials not configured. Run 'aws configure' first."
    exit 1
fi

# Security group setup (improved with better error handling)
echo "[2/6] Setting up security group..."
if ! aws ec2 describe-security-groups --group-names "$SECURITY_GROUP_NAME" --region "$REGION" >/dev/null 2>&1; then
    echo "Creating security group..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group \
        --group-name "$SECURITY_GROUP_NAME" \
        --description "Security group for single-instance multi-agent deployment" \
        --region "$REGION" \
        --query 'GroupId' \
        --output text)
    
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

# Open agent ports with better error handling
echo "Opening ports for agents..."
AGENT_PORTS=$(echo "$AGENTS_JSON" | python3 -c "
import json, sys
agents = json.load(sys.stdin)
ports = [str(agent['port']) for agent in agents]
print(' '.join(ports))
")

for PORT in $AGENT_PORTS; do
    if ! aws ec2 authorize-security-group-ingress \
        --group-id "$SECURITY_GROUP_ID" \
        --protocol tcp \
        --port "$PORT" \
        --cidr 0.0.0.0/0 \
        --region "$REGION" 2>/dev/null; then
        echo "Port $PORT already open or failed to open"
    else
        echo "✅ Opened port $PORT"
    fi
done

# Key pair setup (same as original)
echo "[3/6] Setting up key pair..."
if [ ! -f "${KEY_NAME}.pem" ]; then
    aws ec2 create-key-pair \
        --key-name "$KEY_NAME" \
        --region "$REGION" \
        --query 'KeyMaterial' \
        --output text > "${KEY_NAME}.pem"
    chmod 600 "${KEY_NAME}.pem"
fi

# IMPROVED: Create user data script with proper supervisor configuration
echo "[4/6] Creating improved user data script..."
cat > "user_data_single_multi_${DEPLOYMENT_ID}.sh" << EOF
#!/bin/bash
exec > /var/log/user-data.log 2>&1

echo "=== Improved Multi-Agent Setup Started: $DEPLOYMENT_ID ==="
date

# Update system and install dependencies
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git curl jq supervisor

# Setup project
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/destroyersrt/streamlined-adapter.git nanda-multi-agents
cd nanda-multi-agents
sudo -u ubuntu python3 -m venv env
sudo -u ubuntu bash -c "source env/bin/activate && pip install --upgrade pip && pip install -e . && pip install anthropic"

# Get public IP (same reliable method)
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

# Save agent configuration
cat > /tmp/agents_config.json << 'AGENTS_EOF'
$AGENTS_JSON
AGENTS_EOF

# IMPROVED: Create supervisor configuration for each agent
echo "Creating supervisor configurations..."
mkdir -p /etc/supervisor/conf.d

while IFS= read -r agent_config; do
    AGENT_ID=\$(echo "\$agent_config" | jq -r '.agent_id')
    AGENT_NAME=\$(echo "\$agent_config" | jq -r '.agent_name')
    DOMAIN=\$(echo "\$agent_config" | jq -r '.domain')
    SPECIALIZATION=\$(echo "\$agent_config" | jq -r '.specialization')
    DESCRIPTION=\$(echo "\$agent_config" | jq -r '.description')
    CAPABILITIES=\$(echo "\$agent_config" | jq -r '.capabilities')
    PORT=\$(echo "\$agent_config" | jq -r '.port')
    
    echo "Configuring supervisor for agent: \$AGENT_ID"
    
    # Create supervisor configuration file
    cat > "/etc/supervisor/conf.d/agent_\$AGENT_ID.conf" << SUPERVISOR_EOF
[program:agent_\$AGENT_ID]
command=/home/ubuntu/nanda-multi-agents/env/bin/python examples/nanda_agent.py
directory=/home/ubuntu/nanda-multi-agents
user=ubuntu
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/agent_\$AGENT_ID.err.log
stdout_logfile=/var/log/agent_\$AGENT_ID.out.log
environment=
    ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY",
    AGENT_ID="\$AGENT_ID",
    AGENT_NAME="\$AGENT_NAME",
    AGENT_DOMAIN="\$DOMAIN",
    AGENT_SPECIALIZATION="\$SPECIALIZATION",
    AGENT_DESCRIPTION="\$DESCRIPTION",
    AGENT_CAPABILITIES="\$CAPABILITIES",
    REGISTRY_URL="$REGISTRY_URL",
    PUBLIC_URL="http://\$PUBLIC_IP:\$PORT",
    PORT="\$PORT"

SUPERVISOR_EOF

    echo "✅ Supervisor config created for agent \$AGENT_ID on port \$PORT"
    
done < <(cat /tmp/agents_config.json | jq -c '.[]')

# IMPROVED: Start supervisor and wait for all agents
echo "Starting supervisor..."
systemctl enable supervisor
systemctl start supervisor
supervisorctl reread
supervisorctl update

# Wait for all agents to start
echo "Waiting for all agents to start..."
sleep 30

# IMPROVED: Verify all agents are running
echo "Verifying agent status..."
supervisorctl status

echo "=== Multi-Agent Setup Complete: $DEPLOYMENT_ID ==="
echo "All agents managed by supervisor on: \$PUBLIC_IP"

EOF

# Launch instance (same as original)
echo "[5/6] Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id "$AMI_ID" \
    --count 1 \
    --instance-type "$INSTANCE_TYPE" \
    --key-name "$KEY_NAME" \
    --security-group-ids "$SECURITY_GROUP_ID" \
    --region "$REGION" \
    --user-data "file://user_data_single_multi_${DEPLOYMENT_ID}.sh" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=nanda-single-multi-$DEPLOYMENT_ID},{Key=Project,Value=NANDA-Single-Multi-Agent},{Key=DeploymentId,Value=$DEPLOYMENT_ID}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance (improved timing)
echo "[6/6] Waiting for instance and deployment..."
aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
PUBLIC_IP=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "Waiting for multi-agent deployment (5 minutes for proper startup)..."
sleep 300

# Cleanup
rm "user_data_single_multi_${DEPLOYMENT_ID}.sh"

# IMPROVED: Health check all agents
echo ""
echo "🔍 Performing health checks..."
echo "$AGENTS_JSON" | python3 -c "
import json, sys, requests, time
agents = json.load(sys.stdin)
for agent in agents:
    url = f'http://$PUBLIC_IP:{agent[\"port\"]}/health'
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f'✅ {agent[\"agent_id\"]}: Healthy')
        else:
            print(f'⚠️  {agent[\"agent_id\"]}: HTTP {response.status_code}')
    except Exception as e:
        print(f'❌ {agent[\"agent_id\"]}: {str(e)}')
" 2>/dev/null || echo "Health check skipped (requests not available)"

echo ""
echo "🎉 Improved Multi-Agent Deployment Complete!"
echo "============================================="
echo "Deployment ID: $DEPLOYMENT_ID"
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"

# Display agent URLs (same as original)
# Get actual agent IDs with hex suffixes from logs
echo "Getting actual agent IDs (with hex suffixes)..."
ACTUAL_AGENT_IDS=""
sleep 10
for attempt in {1..3}; do
    ACTUAL_AGENT_IDS=$(ssh -i "${KEY_NAME}.pem" -o StrictHostKeyChecking=no ubuntu@$PUBLIC_IP \
        "grep 'Generated agent_id:' /var/log/agent_*.out.log 2>/dev/null | cut -d':' -f3 | tr -d ' '" 2>/dev/null || echo "")
    if [ -n "$ACTUAL_AGENT_IDS" ]; then
        break
    fi
    echo "Attempt $attempt: Waiting for agent logs..."
    sleep 5
done

echo ""
echo "🤖 Agent URLs:"
echo "$AGENTS_JSON" | python3 -c "
import json, sys
agents = json.load(sys.stdin)
for agent in agents:
    print(f\"  {agent['agent_id']}: http://$PUBLIC_IP:{agent['port']}/a2a\")
"

if [ -n "$ACTUAL_AGENT_IDS" ]; then
    echo ""
    echo "🤖 Actual Agent IDs for A2A Communication:"
    echo "$ACTUAL_AGENT_IDS" | while read -r agent_id; do
        if [ -n "$agent_id" ]; then
            echo "  @$agent_id"
        fi
    done
    echo ""
    echo "📞 Use these in A2A messages:"
    echo "  Example: @[agent-id] your message here"
else
    echo ""
    echo "⚠️  Could not retrieve actual agent IDs from logs."
    echo "📞 Agent IDs will be: [base-id]-[6-char-hex]"
fi

echo ""
echo "📊 Monitor agents:"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo supervisorctl status'"

echo ""
echo "🔄 Restart all agents:"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP 'sudo supervisorctl restart all'"

echo ""
echo "🛑 To terminate:"
echo "aws ec2 terminate-instances --region $REGION --instance-ids $INSTANCE_ID"