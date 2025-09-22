#!/bin/bash

echo "🚀 Manual A2A Testing Script"
echo "=============================="
echo ""
echo "Prerequisites:"
echo "1. Start sarcastic_agent: python examples/sarcastic_agent.py (port 6002)"
echo "2. Start helpful_agent: python examples/helpful_agent.py (port 6003)"
echo ""

# Check if agents are running
echo "🔍 Checking if agents are running..."

if curl -s http://localhost:6002/a2a > /dev/null 2>&1; then
    echo "✅ Sarcastic agent (port 6002) is running"
else
    echo "❌ Sarcastic agent (port 6002) is NOT running"
    echo "   Start it with: python examples/sarcastic_agent.py"
    exit 1
fi

if curl -s http://localhost:6003/a2a > /dev/null 2>&1; then
    echo "✅ Helpful agent (port 6003) is running"
else
    echo "❌ Helpful agent (port 6003) is NOT running"
    echo "   Start it with: python examples/helpful_agent.py"
    exit 1
fi

echo ""
echo "🧪 Running A2A Tests..."

# Test 1: Direct message to sarcastic agent
echo ""
echo "1. Testing direct message to sarcastic agent:"
echo "   Command: 'hello'"
curl -s -X POST http://localhost:6002/a2a \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": {"type": "text", "text": "hello"}, "conversation_id": "test1"}' | \
  jq -r '.parts[0].text' | sed 's/^/   Response: /'

# Test 2: Direct message to helpful agent
echo ""
echo "2. Testing direct message to helpful agent:"
echo "   Command: 'what time is it'"
curl -s -X POST http://localhost:6003/a2a \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": {"type": "text", "text": "what time is it"}, "conversation_id": "test2"}' | \
  jq -r '.parts[0].text' | sed 's/^/   Response: /'

# Test 3: A2A message (will fail without registry, but shows the attempt)
echo ""
echo "3. Testing A2A message from sarcastic to helpful (will show registry lookup):"
echo "   Command: '@helpful_agent Hello from sarcastic agent'"
curl -s -X POST http://localhost:6002/a2a \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": {"type": "text", "text": "@helpful_agent Hello from sarcastic agent"}, "conversation_id": "test3"}' | \
  jq -r '.parts[0].text' | sed 's/^/   Response: /'

# Test 4: A2A message (reverse direction)
echo ""
echo "4. Testing A2A message from helpful to sarcastic (will show registry lookup):"
echo "   Command: '@sarcastic_agent Hi there!'"
curl -s -X POST http://localhost:6003/a2a \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": {"type": "text", "text": "@sarcastic_agent Hi there!"}, "conversation_id": "test4"}' | \
  jq -r '.parts[0].text' | sed 's/^/   Response: /'

# Test 5: Custom commands
echo ""
echo "5. Testing custom sarcastic command:"
echo "   Command: '/sarcast this is amazing'"
curl -s -X POST http://localhost:6002/a2a \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": {"type": "text", "text": "/sarcast this is amazing"}, "conversation_id": "test5"}' | \
  jq -r '.parts[0].text' | sed 's/^/   Response: /'

echo ""
echo "✅ A2A Testing Complete!"
echo ""
echo "📋 What you should see:"
echo "  - Tests 1-2: Direct responses from each agent's personality"
echo "  - Tests 3-4: 'Agent not found in registry' (expected without registry)"
echo "  - Test 5: Custom sarcastic command response"
echo ""
echo "🎯 This demonstrates:"
echo "  ✅ Agents work independently with custom handlers"
echo "  ✅ A2A routing mechanism is functional"
echo "  ✅ Registry lookup is attempted (would work with proper registry)"
echo "  ✅ No message improvement (original streamlined goal achieved)"