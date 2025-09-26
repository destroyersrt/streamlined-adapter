#!/bin/bash

# Complete AWS EC2 + NANDA Agent Deployment Script
# Creates EC2 instance and deploys NANDA agent in one command

set -e

echo "🚀 Complete AWS EC2 + NANDA Agent Deployment"
echo "============================================="

# Check for required arguments
if [ $# -lt 3 ]; then
    echo ""
    echo "Usage: bash aws-ec2-deploy.sh <AGENT_TYPE> <AGENT_ID> <ANTHROPIC_API_KEY> [PORT] [REGION] [INSTANCE_TYPE]"
    echo ""
    echo "Agent Types:"
    echo "  • helpful    - General helpful agent"
    echo "  • pirate     - Pirate personality agent"
    echo "  • echo       - Simple echo agent"
    echo "  • analyst    - LangChain document analyst (requires LangChain)"
    echo ""
    echo "Examples:"
    echo "  bash aws-ec2-deploy.sh helpful my_agent sk-ant-xxxxx"
    echo "  bash aws-ec2-deploy.sh analyst doc_analyzer sk-ant-xxxxx 6020 us-west-2 t3.small"
    echo ""
    echo "Prerequisites:"
    echo "  • AWS CLI configured (aws configure)"
    echo "  • Valid Anthropic API key"
    echo "  • EC2 permissions in AWS account"
    echo ""
    exit 1
fi

# Parse arguments
AGENT_TYPE=$1
AGENT_ID=$2
ANTHROPIC_API_KEY=$3
PORT=${4:-6000}
REGION=${5:-us-east-1}
INSTANCE_TYPE=${6:-t3.micro}

# Configuration
SECURITY_GROUP_NAME="nanda-streamlined-agents"
KEY_NAME="nanda-agent-key"
AMI_ID="ami-0c94855ba95b798c7"  # Amazon Linux 2023 in us-east-1

echo "Configuration:"
echo "  Agent Type: $AGENT_TYPE"
echo "  Agent ID: $AGENT_ID"
echo "  Port: $PORT"
echo "  Region: $REGION"
echo "  Instance Type: $INSTANCE_TYPE"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install and configure AWS CLI first."
    echo "   Install: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    echo "   Configure: aws configure"
    exit 1
fi

# Test AWS credentials
echo "[1/8] Checking AWS credentials..."
if ! aws sts get-caller-identity --region $REGION > /dev/null 2>&1; then
    echo "❌ AWS credentials not configured or invalid."
    echo "   Run: aws configure"
    exit 1
fi
echo "✅ AWS credentials valid"

# Create or get security group
echo "[2/8] Setting up security group..."
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --region $REGION --group-names $SECURITY_GROUP_NAME --query 'SecurityGroups[0].GroupId' --output text 2>/dev/null || echo "")

if [ "$SECURITY_GROUP_ID" = "None" ] || [ -z "$SECURITY_GROUP_ID" ]; then
    echo "Creating security group $SECURITY_GROUP_NAME..."
    SECURITY_GROUP_ID=$(aws ec2 create-security-group --region $REGION --group-name $SECURITY_GROUP_NAME --description "NANDA Streamlined Agents Security Group" --query 'GroupId' --output text)
    
    # Add rules for NANDA agents
    aws ec2 authorize-security-group-ingress --region $REGION --group-id $SECURITY_GROUP_ID --protocol tcp --port $PORT --cidr 0.0.0.0/0
    aws ec2 authorize-security-group-ingress --region $REGION --group-id $SECURITY_GROUP_ID --protocol tcp --port 22 --cidr 0.0.0.0/0
    
    echo "✅ Security group created: $SECURITY_GROUP_ID"
else
    echo "✅ Using existing security group: $SECURITY_GROUP_ID"
fi

# Create or get key pair
echo "[3/8] Setting up key pair..."
if ! aws ec2 describe-key-pairs --region $REGION --key-names $KEY_NAME > /dev/null 2>&1; then
    echo "Creating key pair $KEY_NAME..."
    aws ec2 create-key-pair --region $REGION --key-name $KEY_NAME --query 'KeyMaterial' --output text > ${KEY_NAME}.pem
    chmod 400 ${KEY_NAME}.pem
    echo "✅ Key pair created and saved as ${KEY_NAME}.pem"
else
    echo "✅ Using existing key pair: $KEY_NAME"
    if [ ! -f "${KEY_NAME}.pem" ]; then
        echo "⚠️  Warning: ${KEY_NAME}.pem not found locally. You may need it for SSH access."
    fi
fi

# Create user data script
echo "[4/8] Generating user data script..."
cat > user_data_${AGENT_ID}.sh << EOF
#!/bin/bash
exec > /var/log/user-data.log 2>&1
set -e

echo "=== NANDA Agent Setup Started: $AGENT_ID ==="
date

# Update system and install Python
echo "Installing system dependencies..."
dnf update -y
dnf install -y python3.11 python3.11-pip git

# Create project directory
cd /home/ec2-user
PROJECT_DIR="nanda-agent-$AGENT_ID"
sudo -u ec2-user mkdir -p \$PROJECT_DIR
cd \$PROJECT_DIR

# Clone streamlined adapter
echo "Cloning NANDA Streamlined Adapter..."
sudo -u ec2-user git clone https://github.com/destroyersrt/streamlined-adapter.git .

# Create virtual environment and install dependencies
echo "Setting up Python environment..."
sudo -u ec2-user python3.11 -m venv env
source env/bin/activate

# Install core dependencies
pip install --upgrade pip
pip install -e .

# Install additional dependencies for specific agent types
if [ "$AGENT_TYPE" = "analyst" ]; then
    pip install langchain-core langchain-anthropic
fi

# Generate agent script
echo "Generating agent script..."
EOF

# Add agent-specific script generation to user data
if [ "$AGENT_TYPE" = "helpful" ]; then
    cat >> user_data_${AGENT_ID}.sh << 'EOF'
sudo -u ec2-user cat > agent_script.py << 'AGENT_EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nanda_core.core.adapter import NANDA, helpful_agent

def main():
    print("🤖 Starting NANDA Agent: AGENT_ID_PLACEHOLDER")
    nanda = NANDA(
        agent_id="AGENT_ID_PLACEHOLDER",
        agent_logic=helpful_agent,
        port=PORT_PLACEHOLDER,
        enable_telemetry=False
    )
    print("🚀 Agent URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):PORT_PLACEHOLDER/a2a")
    nanda.start()

if __name__ == "__main__":
    main()
AGENT_EOF
EOF
elif [ "$AGENT_TYPE" = "pirate" ]; then
    cat >> user_data_${AGENT_ID}.sh << 'EOF'
sudo -u ec2-user cat > agent_script.py << 'AGENT_EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nanda_core.core.adapter import NANDA, pirate_agent

def main():
    print("🤖 Starting NANDA Agent: AGENT_ID_PLACEHOLDER")
    nanda = NANDA(
        agent_id="AGENT_ID_PLACEHOLDER",
        agent_logic=pirate_agent,
        port=PORT_PLACEHOLDER,
        enable_telemetry=False
    )
    print("🚀 Agent URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):PORT_PLACEHOLDER/a2a")
    nanda.start()

if __name__ == "__main__":
    main()
AGENT_EOF
EOF
elif [ "$AGENT_TYPE" = "echo" ]; then
    cat >> user_data_${AGENT_ID}.sh << 'EOF'
sudo -u ec2-user cat > agent_script.py << 'AGENT_EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nanda_core.core.adapter import NANDA, echo_agent

def main():
    print("🤖 Starting NANDA Agent: AGENT_ID_PLACEHOLDER")
    nanda = NANDA(
        agent_id="AGENT_ID_PLACEHOLDER",
        agent_logic=echo_agent,
        port=PORT_PLACEHOLDER,
        enable_telemetry=False
    )
    print("🚀 Agent URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):PORT_PLACEHOLDER/a2a")
    nanda.start()

if __name__ == "__main__":
    main()
AGENT_EOF
EOF
elif [ "$AGENT_TYPE" = "analyst" ]; then
    cat >> user_data_${AGENT_ID}.sh << 'EOF'
sudo -u ec2-user cat > agent_script.py << 'AGENT_EOF'
#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def analyst_logic(message, conversation_id):
    # Simple analyst logic - can be enhanced with LangChain
    if message.lower().startswith("analyze:"):
        return f"Analysis: {message[8:].strip()}"
    elif message.lower().startswith("question:"):
        return f"Answer: {message[9:].strip()}"
    else:
        return "Use 'analyze: <text>' or 'question: <question>'"

from nanda_core.core.adapter import NANDA

def main():
    print("🤖 Starting NANDA Agent: AGENT_ID_PLACEHOLDER")
    nanda = NANDA(
        agent_id="AGENT_ID_PLACEHOLDER",
        agent_logic=analyst_logic,
        port=PORT_PLACEHOLDER,
        enable_telemetry=False
    )
    print("🚀 Agent URL: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):PORT_PLACEHOLDER/a2a")
    nanda.start()

if __name__ == "__main__":
    main()
AGENT_EOF
EOF
fi

# Complete the user data script
cat >> user_data_${AGENT_ID}.sh << EOF

# Replace placeholders
sed -i 's/AGENT_ID_PLACEHOLDER/$AGENT_ID/g' agent_script.py
sed -i 's/PORT_PLACEHOLDER/$PORT/g' agent_script.py

# Make script executable
chmod +x agent_script.py

# Start the agent
echo "Starting NANDA agent..."
sudo -u ec2-user nohup python3 agent_script.py > agent.log 2>&1 &

echo "=== NANDA Agent Setup Complete: $AGENT_ID ==="
echo "Agent is running on port $PORT"
echo "Public IP: \$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "Agent URL: http://\$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):$PORT/a2a"
date
EOF

# Launch EC2 instance
echo "[5/8] Launching EC2 instance..."
INSTANCE_ID=$(aws ec2 run-instances \
    --region $REGION \
    --image-id $AMI_ID \
    --count 1 \
    --instance-type $INSTANCE_TYPE \
    --key-name $KEY_NAME \
    --security-group-ids $SECURITY_GROUP_ID \
    --user-data file://user_data_${AGENT_ID}.sh \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=nanda-agent-$AGENT_ID},{Key=Project,Value=NANDA-Streamlined}]" \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "✅ Instance launched: $INSTANCE_ID"

# Wait for instance to be running
echo "[6/8] Waiting for instance to be running..."
aws ec2 wait instance-running --region $REGION --instance-ids $INSTANCE_ID
echo "✅ Instance is running"

# Get public IP
echo "[7/8] Getting public IP..."
PUBLIC_IP=$(aws ec2 describe-instances --region $REGION --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text)
echo "✅ Public IP: $PUBLIC_IP"

# Wait for agent to be ready (give user data time to execute)
echo "[8/8] Waiting for agent deployment (this may take 2-3 minutes)..."
sleep 120

# Clean up local files
rm -f user_data_${AGENT_ID}.sh

echo ""
echo "🎉 NANDA Agent Deployment Complete!"
echo "=================================="
echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "Agent URL: http://$PUBLIC_IP:$PORT/a2a"
echo ""
echo "🧪 Test your agent:"
echo "curl -X POST http://$PUBLIC_IP:$PORT/a2a \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"content\":{\"text\":\"hello\",\"type\":\"text\"},\"role\":\"user\",\"conversation_id\":\"test123\"}'"
echo ""
echo "🔐 SSH Access:"
echo "ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP"
echo ""
echo "📋 View agent logs:"
echo "ssh -i ${KEY_NAME}.pem ec2-user@$PUBLIC_IP 'cat nanda-agent-$AGENT_ID/agent.log'"
echo ""
echo "🛑 To terminate instance:"
echo "aws ec2 terminate-instances --region $REGION --instance-ids $INSTANCE_ID"
echo ""
