# A2A Communication Testing Guide

This guide explains how to test agent-to-agent (A2A) communication using public IP addresses with the streamlined adapter.

## Quick Start

### 1. Check Your IP Address
```bash
python examples/check_ip.py
```
This will show you the IP address that will be used for testing.

### 2. Start Agents with Public IP
```bash
python examples/setup_agents_with_public_ip.py
```
This starts both agents (sarcastic and helpful) using your public IP address.

### 3. Test A2A Communication
```bash
python examples/test_public_ip_a2a.py
```
This runs comprehensive tests of the A2A communication flow.

## Automated Testing

For automated testing, use:
```bash
bash examples/run_full_a2a_test.sh auto
```

## Manual Testing Steps

### Terminal 1: Start Agents
```bash
cd streamlined_adapter
python examples/setup_agents_with_public_ip.py
```

Wait for the startup messages showing agents are running.

### Terminal 2: Run Tests
```bash
cd streamlined_adapter
python examples/test_public_ip_a2a.py
```

## Test Phases

### Phase 1: Direct Messages
- Tests basic agent functionality
- No A2A routing involved
- Verifies agents respond with their personalities

### Phase 2: A2A Routing
- Tests `@agent_id message` format
- Verifies agent lookup using public IP
- Shows comprehensive logging of message routing

### Phase 3: Conversation Flow
- Tests multi-message conversations
- Demonstrates back-and-forth communication
- Shows conversation ID tracking

## Expected Behavior

### ✅ What Should Work
- Agents start with public IP endpoints
- Direct messages get personality responses
- A2A messages are properly routed
- Comprehensive logging shows message flow
- No message improvement (streamlined goal)

### 📋 Logging to Watch For

**Agent Startup:**
```
🚀 Starting sarcastic_agent on 10.189.72.201:6002
   PUBLIC_URL: http://10.189.72.201:6002
   API_URL: http://10.189.72.201:6102
```

**Message Reception:**
```
📨 [AGENT sarcastic_agent] Received message:
🆔 Message ID: msg_xxx
💬 Conversation ID: test_a2a_1
📝 Content Type: <class 'python_a2a.message.TextContent'>
📝 Message text: '@helpful_agent Hello from sarcastic!'
```

**Agent Lookup:**
```
🔄 [AGENT sarcastic_agent] Attempting to send message to helpful_agent
📝 Message: 'Hello from sarcastic!'
🔍 Looking up helpful_agent...
💡 Using base IP: 10.189.72.201 for local agent lookup
🏠 Found helpful_agent in local testing registry: http://10.189.72.201:6003
```

**Message Delivery:**
```
📤 Sending to URL: http://10.189.72.201:6003/a2a
📋 Formatted message: __EXTERNAL_MESSAGE__...
🚀 Creating A2A client for http://10.189.72.201:6003/a2a
✅ Message successfully sent to helpful_agent
```

## Manual curl Testing

Direct message:
```bash
curl -X POST http://YOUR_IP:6002/a2a \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": {"type": "text", "text": "hello"}, "conversation_id": "test"}'
```

A2A message:
```bash
curl -X POST http://YOUR_IP:6002/a2a \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": {"type": "text", "text": "@helpful_agent Hello!"}, "conversation_id": "test_a2a"}'
```

## Troubleshooting

### Agents Not Starting
- Check if ports 6002/6003 are available
- Verify Python path and dependencies
- Check for firewall blocking ports

### A2A Messages Not Routing
- Verify agents are running on expected IP
- Check agent lookup logs
- Ensure PUBLIC_IP environment variable is set

### No Response from Target Agent
- Check if target agent is receiving external messages
- Verify external message format in logs
- Check A2A client connection logs

## Key Features Demonstrated

1. **Public IP Support**: Agents can use any IP address, not just localhost
2. **Dynamic Agent Lookup**: IP detection and environment variable support
3. **Comprehensive Logging**: Full visibility into message flow
4. **No Message Improvement**: Original streamlined goal maintained
5. **Custom Agent Personalities**: Handlers work without modification
6. **External Message Handling**: Proper A2A protocol implementation

## Files Involved

- `setup_agents_with_public_ip.py` - Starts agents with public IP
- `test_public_ip_a2a.py` - Comprehensive A2A testing
- `run_full_a2a_test.sh` - Automated test runner
- `check_ip.py` - IP address detection utility
- `agent_bridge.py` - Core A2A implementation with logging
- `sarcastic_agent.py` / `helpful_agent.py` - Example agents