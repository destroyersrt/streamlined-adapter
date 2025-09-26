#!/bin/bash

# Simple NANDA Agent Deployment Script
# Usage: bash deploy-agent.sh <AGENT_TYPE> <AGENT_ID> <ANTHROPIC_API_KEY> [PORT] [REGISTRY_URL]

set -e

AGENT_TYPE=$1
AGENT_ID=$2
ANTHROPIC_API_KEY=$3
PORT=${4:-6000}
REGISTRY_URL=${5:-""}

if [ -z "$AGENT_TYPE" ] || [ -z "$AGENT_ID" ] || [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "🤖 Simple NANDA Agent Deployment"
  echo "================================="
  echo ""
  echo "Usage: bash deploy-agent.sh <AGENT_TYPE> <AGENT_ID> <ANTHROPIC_API_KEY> [PORT] [REGISTRY_URL]"
  echo ""
  echo "Agent Types:"
  echo "  • helpful    - General helpful agent"
  echo "  • pirate     - Pirate personality agent"
  echo "  • echo       - Simple echo agent"
  echo "  • analyst    - LangChain document analyst (requires LangChain)"
  echo ""
  echo "Examples:"
  echo "  bash deploy-agent.sh helpful my_agent sk-ant-xxxxx"
  echo "  bash deploy-agent.sh analyst doc_analyzer sk-ant-xxxxx 6020"
  echo "  bash deploy-agent.sh pirate captain_jack sk-ant-xxxxx 6000 https://registry.example.com"
  echo ""
  exit 1
fi

echo "🚀 Deploying NANDA Agent"
echo "========================"
echo "Agent Type: $AGENT_TYPE"
echo "Agent ID: $AGENT_ID"
echo "Port: $PORT"
echo "Registry: ${REGISTRY_URL:-"None (local only)"}"
echo ""

echo "[1/6] Updating system and installing Python..."
# Works on both Ubuntu and Amazon Linux
if command -v apt &> /dev/null; then
    # Ubuntu/Debian
    sudo apt update -y
    sudo apt install -y python3 python3-pip python3-venv git curl
else
    # Amazon Linux/CentOS/RHEL
    sudo dnf update -y
    sudo dnf install -y python3.11 python3.11-pip git curl
    # Create python3 symlink if needed
    if ! command -v python3 &> /dev/null; then
        sudo ln -s /usr/bin/python3.11 /usr/bin/python3
    fi
fi

echo "[2/6] Setting up project directory..."
cd "$HOME"
PROJECT_DIR="nanda-agent-$AGENT_ID"

# Remove existing directory if it exists
if [ -d "$PROJECT_DIR" ]; then
    echo "Removing existing directory..."
    rm -rf "$PROJECT_DIR"
fi

# Clone streamlined adapter
echo "Cloning streamlined adapter..."
git clone https://github.com/destroyersrt/streamlined-adapter.git "$PROJECT_DIR"
cd "$PROJECT_DIR"

echo "[3/6] Creating Python virtual environment..."
python3 -m venv env
source env/bin/activate

echo "[4/6] Installing Python dependencies..."
pip install --upgrade pip

# Install core dependencies
pip install anthropic python-a2a requests

# Install agent-specific dependencies
case $AGENT_TYPE in
    "analyst")
        echo "Installing LangChain dependencies for analyst agent..."
        pip install langchain-core langchain-anthropic
        ;;
    "helpful"|"pirate"|"echo")
        echo "Using built-in agent type (no extra dependencies)"
        ;;
    *)
        echo "⚠️ Unknown agent type: $AGENT_TYPE. Proceeding with basic installation..."
        ;;
esac

echo "[5/6] Creating agent startup script..."
cat > run_agent.py << EOF
#!/usr/bin/env python3
"""
Auto-generated NANDA Agent
Agent Type: $AGENT_TYPE
Agent ID: $AGENT_ID
Port: $PORT
"""

import os
import sys

# Set API key
os.environ["ANTHROPIC_API_KEY"] = "$ANTHROPIC_API_KEY"

# Add project to path
sys.path.append(os.path.dirname(__file__))

from nanda_core.core.adapter import NANDA, helpful_agent, pirate_agent, echo_agent

def main():
    print("🤖 Starting NANDA Agent: $AGENT_ID")
    print("Agent Type: $AGENT_TYPE")
    print("Port: $PORT")
    print("")
    
    # Select agent logic based on type
    agent_logic = helpful_agent  # default
    
    if "$AGENT_TYPE" == "pirate":
        agent_logic = pirate_agent
    elif "$AGENT_TYPE" == "echo":
        agent_logic = echo_agent
    elif "$AGENT_TYPE" == "analyst":
        try:
            from examples.langchain_analyst_agent import DocumentAnalyst, create_analyst_agent_logic
            analyst = DocumentAnalyst()
            agent_logic = create_analyst_agent_logic(analyst)
            print("📊 LangChain Document Analyst loaded")
        except ImportError:
            print("⚠️ LangChain dependencies not available, using helpful agent")
            agent_logic = helpful_agent
    
    # Create NANDA agent
    nanda = NANDA(
        agent_id="$AGENT_ID",
        agent_logic=agent_logic,
        port=$PORT,
        registry_url="${REGISTRY_URL}" if "${REGISTRY_URL}" else None,
        public_url="http://\$(curl -s ifconfig.me):$PORT" if "${REGISTRY_URL}" else None
    )
    
    print("🚀 Agent ready! Send messages to http://localhost:$PORT/a2a")
    if "${REGISTRY_URL}":
        print("🌐 Will attempt to register with registry: ${REGISTRY_URL}")
    
    try:
        nanda.start(register=bool("${REGISTRY_URL}"))
    except KeyboardInterrupt:
        print("\\n🛑 Agent stopped")

if __name__ == "__main__":
    main()
EOF

chmod +x run_agent.py

echo "[6/6] Starting agent..."
echo ""
echo "🎉 NANDA Agent Deployment Complete!"
echo "===================================="
echo "Agent ID: $AGENT_ID"
echo "Type: $AGENT_TYPE"
echo "Port: $PORT"
echo "Directory: $HOME/$PROJECT_DIR"
echo ""
echo "🚀 Starting agent in background..."

# Start agent in background
nohup python3 run_agent.py > agent.log 2>&1 &
AGENT_PID=$!

sleep 3

# Check if agent is running
if ps -p $AGENT_PID > /dev/null; then
    echo "✅ Agent started successfully (PID: $AGENT_PID)"
    echo ""
    echo "📋 Useful commands:"
    echo "  • View logs: tail -f $HOME/$PROJECT_DIR/agent.log"
    echo "  • Stop agent: kill $AGENT_PID"
    echo "  • Test agent: curl -X POST http://localhost:$PORT/a2a -H 'Content-Type: application/json' -d '{\"content\":{\"text\":\"hello\"}}'"
    echo ""
    echo "🔗 Agent URL: http://\$(curl -s ifconfig.me):$PORT/a2a"
    echo ""
    echo "📄 View logs:"
    tail -10 agent.log
else
    echo "❌ Agent failed to start. Check logs:"
    cat agent.log
    exit 1
fi

