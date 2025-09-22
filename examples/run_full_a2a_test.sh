#!/bin/bash

echo "🚀 Full A2A Communication Test with Public IP"
echo "============================================="
echo ""

# Check if we're in the right directory
if [[ ! -f "examples/setup_agents_with_public_ip.py" ]]; then
    echo "❌ Please run this script from the streamlined_adapter directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: examples/setup_agents_with_public_ip.py"
    exit 1
fi

echo "📍 Step 1: Setup Instructions"
echo "-----------------------------"
echo "To test full A2A communication:"
echo ""
echo "1️⃣ Terminal 1 - Start agents with public IP:"
echo "   python examples/setup_agents_with_public_ip.py"
echo ""
echo "2️⃣ Terminal 2 - Run this test once agents are started:"
echo "   python examples/test_public_ip_a2a.py"
echo ""
echo "OR for automated testing:"
echo "3️⃣ bash examples/run_full_a2a_test.sh auto"
echo ""

if [[ "$1" == "auto" ]]; then
    echo "🤖 Running automated test..."
    echo ""

    # Start agents in background
    echo "🚀 Starting agents with public IP..."
    python examples/setup_agents_with_public_ip.py &
    AGENTS_PID=$!

    # Wait for agents to start
    echo "⏳ Waiting for agents to start (10 seconds)..."
    sleep 10

    # Run the test
    echo "🧪 Running A2A communication test..."
    python examples/test_public_ip_a2a.py

    # Stop agents
    echo ""
    echo "🛑 Stopping agents..."
    kill $AGENTS_PID 2>/dev/null
    sleep 2

    echo "✅ Automated test complete!"
else
    echo "📋 Manual Testing Steps:"
    echo "----------------------"
    echo ""
    echo "1. Open Terminal 1 and run:"
    echo "   cd $(pwd)"
    echo "   python examples/setup_agents_with_public_ip.py"
    echo ""
    echo "2. Wait for agents to start (you'll see startup messages)"
    echo ""
    echo "3. Open Terminal 2 and run:"
    echo "   cd $(pwd)"
    echo "   python examples/test_public_ip_a2a.py"
    echo ""
    echo "4. Watch the comprehensive logging in both terminals"
    echo ""
    echo "🎯 What to Look For:"
    echo "  ✅ Agent startup with public IP detection"
    echo "  ✅ A2A endpoint URLs with your IP address"
    echo "  ✅ Message routing logs with 'Looking up agent...'"
    echo "  ✅ External message formatting and delivery"
    echo "  ✅ Responses from both agents with personalities"
    echo "  ✅ No message improvement (streamlined goal)"
    echo ""
    echo "To run automated test instead: bash $0 auto"
fi