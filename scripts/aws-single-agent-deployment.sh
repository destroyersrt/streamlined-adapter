#!/bin/bash

# CONFIGURABLE AWS EC2 + NANDA Agent Deployment Script
# This script creates an EC2 instance and deploys a fully configurable modular NANDA agent
# Usage: bash aws-ec2-deploy-simple.sh <AGENT_ID> <ANTHROPIC_API_KEY> <AGENT_NAME> <DOMAIN> <SPECIALIZATION> <DESCRIPTION> <CAPABILITIES> [REGISTRY_URL] [PORT] [REGION] [INSTANCE_TYPE]

set -e

# Parse arguments
AGENT_ID="$1"
ANTHROPIC_API_KEY="$2"
AGENT_NAME="$3"
DOMAIN="$4"
SPECIALIZATION="$5"
DESCRIPTION="$6"
CAPABILITIES="$7"
REGISTRY_URL="${8:-}"
PORT="${9:-6000}"
REGION="${10:-us-east-1}"
INSTANCE_TYPE="${11:-t3.micro}"

# Validate inputs
if [ -z "$AGENT_ID" ] || [ -z "$ANTHROPIC_API_KEY" ] || [ -z "$AGENT_NAME" ] || [ -z "$DOMAIN" ] || [ -z "$SPECIALIZATION" ] || [ -z "$DESCRIPTION" ] || [ -z "$CAPABILITIES" ]; then
    echo "❌ Usage: $0 <AGENT_ID> <ANTHROPIC_API_KEY> <AGENT_NAME> <DOMAIN> <SPECIALIZATION> <DESCRIPTION> <CAPABILITIES> [REGISTRY_URL] [PORT] [REGION] [INSTANCE_TYPE]"
    echo ""
    echo "Example:"
    echo "  $0 data-scientist sk-ant-xxxxx \"Data Scientist\" \"data analysis\" \"analytical and precise AI assistant\" \"I specialize in data analysis, statistics, and machine learning.\" \"data analysis,statistics,machine learning,Python,R\" \"https://registry.example.com\" 6000 us-east-1 t3.micro"
    echo ""
    echo "Parameters:"
    echo "  AGENT_ID: Unique identifier for the agent"
    echo "  ANTHROPIC_API_KEY: Your Anthropic API key"
    echo "  AGENT_NAME: Display name for the agent"
    echo "  DOMAIN: Primary domain/field of expertise"
    echo "  SPECIALIZATION: Brief description of agent's role"
    echo "  DESCRIPTION: Detailed description of the agent"
    echo "  CAPABILITIES: Comma-separated list of capabilities"
    echo "  REGISTRY_URL: Optional registry URL for agent discovery"
    exit 1
fi

echo "🚀 Configurable AWS EC2 + NANDA Agent Deployment"
echo "================================================="
echo "Agent ID: $AGENT_ID"
echo "Agent Name: $AGENT_NAME"
echo "Domain: $DOMAIN"
echo "Specialization: $SPECIALIZATION"
echo "Capabilities: $CAPABILITIES"
echo "Registry URL: ${REGISTRY_URL:-"None"}"
echo "Port: $PORT"
echo "Region: $REGION"
echo "Instance Type: $INSTANCE_TYPE"
echo ""

# Configuration
SECURITY_GROUP_NAME="nanda-streamlined-agents"
KEY_NAME="nanda-agent-key-a1b2"
AMI_ID="ami-0866a3c8686eaeeba"  # Ubuntu 22.04 LTS

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
        --description "Security group for NANDA streamlined agents" \
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

# Open agent port
aws ec2 authorize-security-group-ingress \
    --group-id "$SECURITY_GROUP_ID" \
    --protocol tcp \
    --port "$PORT" \
    --cidr 0.0.0.0/0 \
    --region "$REGION" 2>/dev/null || echo "Port $PORT already open"

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

# Create user data script - SIMPLE!
echo "[4/6] Creating user data script..."
cat > "user_data_${AGENT_ID}.sh" << EOF
#!/bin/bash
exec > /var/log/user-data.log 2>&1

echo "=== NANDA Agent Setup Started: $AGENT_ID ==="
date

# Update system and install dependencies
apt-get update -y
apt-get install -y python3 python3-venv python3-pip git curl

# Setup project as ubuntu user
cd /home/ubuntu
sudo -u ubuntu git clone https://github.com/destroyersrt/streamlined-adapter.git nanda-agent-$AGENT_ID
cd nanda-agent-$AGENT_ID

# Create virtual environment and install
sudo -u ubuntu python3 -m venv env
sudo -u ubuntu bash -c "source env/bin/activate && pip install --upgrade pip && pip install -e . && pip install anthropic"

# Configure the modular agent with all environment variables
sudo -u ubuntu sed -i "s/PORT = 6000/PORT = $PORT/" examples/modular_agent.py

# Get public IP using IMDSv2 (AWS metadata service v2)
echo "Getting public IP address using IMDSv2..."
for attempt in {1..5}; do
    # Get token for IMDSv2
    TOKEN=\$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" --connect-timeout 5 --max-time 10)
    if [ -n "\$TOKEN" ]; then
        # Use token to get public IP
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
    echo "ERROR: Could not retrieve public IP after 10 attempts"
    exit 1
fi

# Start the agent with all configuration
echo "Starting NANDA agent with PUBLIC_URL: http://\$PUBLIC_IP:$PORT"
sudo -u ubuntu bash -c "
    cd /home/ubuntu/nanda-agent-$AGENT_ID
    source env/bin/activate
    export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY'
    export AGENT_ID='$AGENT_ID'
    export AGENT_NAME='$AGENT_NAME'
    export AGENT_DOMAIN='$DOMAIN'
    export AGENT_SPECIALIZATION='$SPECIALIZATION'
    export AGENT_DESCRIPTION='$DESCRIPTION'
    export AGENT_CAPABILITIES='$CAPABILITIES'
    export REGISTRY_URL='$REGISTRY_URL'
    export PUBLIC_URL='http://\$PUBLIC_IP:$PORT'
    export PORT='$PORT'
    nohup python3 examples/enhanced_nanda_agent.py > agent.log 2>&1 &
"

echo "=== NANDA Agent Setup Complete: $AGENT_ID ==="
echo "Agent URL: http://\$PUBLIC_IP:$PORT/a2a"
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
    --user-data "file://user_data_${AGENT_ID}.sh" \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=nanda-agent-$AGENT_ID},{Key=Project,Value=NANDA-Streamlined}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance
aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"
PUBLIC_IP=$(aws ec2 describe-instances --region "$REGION" --instance-ids "$INSTANCE_ID" --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)

echo "[6/6] Waiting for agent deployment (2-3 minutes)..."
sleep 120


# Cleanup
rm "user_data_${AGENT_ID}.sh"

echo ""
echo "🎉 NANDA Agent Deployment Complete!"
echo "=================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Agent URL: http://$PUBLIC_IP:$PORT/a2a"
echo ""
echo "🤖 Agent ID for A2A Communication: ${AGENT_ID}-[6-char-hex]"
echo ""
echo "📞 Use this agent in A2A messages:"
echo "   @${AGENT_ID}-[hex] your message here"
echo "   (The actual hex suffix is generated at runtime)"

echo ""
echo "🧪 Test your agent (direct communication):"
echo "curl -X POST http://$PUBLIC_IP:$PORT/a2a \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"content\":{\"text\":\"Hello! What can you help me with?\",\"type\":\"text\"},\"role\":\"user\",\"conversation_id\":\"test123\"}'"

echo ""
echo "🧪 Test A2A communication (example with another agent):"
echo "curl -X POST http://{IP_ADDRESS}:{PORT}/a2a \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"content\":{\"text\":\"@{AGENT_ID} What can you help me with?\",\"type\":\"text\"},\"role\":\"user\",\"conversation_id\":\"test123\"}'"
echo ""
echo "🔐 SSH Access:"
echo "ssh -i ${KEY_NAME}.pem ubuntu@$PUBLIC_IP"
echo ""
echo "🛑 To terminate:"
echo "aws ec2 terminate-instances --region $REGION --instance-ids $INSTANCE_ID"
