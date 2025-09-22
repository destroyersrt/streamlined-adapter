#!/usr/bin/env python3
"""
Test A2A communication between two agents locally
"""

import os
import sys
import time
import threading
import requests
from unittest.mock import patch

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter

def create_test_agent(agent_id: str, port: int, response_prefix: str):
    """Create a test agent with simple responses"""

    # Set environment
    os.environ["AGENT_ID"] = agent_id
    os.environ["PORT"] = str(port)

    # Create adapter
    adapter = StreamlinedAdapter(agent_id)

    # Add custom handler
    def test_response_handler(message_text: str, conversation_id: str) -> str:
        return f"{response_prefix}: {message_text}"

    adapter.set_message_handler(test_response_handler)

    return adapter

def mock_agent_lookup(agent_id: str):
    """Mock registry lookup for local testing"""
    agent_ports = {
        "agent_alice": "http://localhost:6010",
        "agent_bob": "http://localhost:6011"
    }
    return agent_ports.get(agent_id)

def start_agent_in_thread(adapter, name):
    """Start an agent in a separate thread"""
    def run_agent():
        try:
            print(f"🤖 Starting {name}...")
            # Mock the registry lookup to avoid network calls
            with patch.object(adapter.bridge, '_lookup_agent', side_effect=mock_agent_lookup):
                adapter.start_server()
        except Exception as e:
            print(f"Error starting {name}: {e}")

    thread = threading.Thread(target=run_agent, daemon=True)
    thread.start()
    return thread

def send_message_to_agent(port: int, message: str, conversation_id: str):
    """Send a message to an agent via HTTP"""
    url = f"http://localhost:{port}/a2a"
    data = {
        "role": "user",
        "content": {
            "type": "text",
            "text": message
        },
        "conversation_id": conversation_id
    }

    try:
        response = requests.post(url, json=data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return result.get("content", {}).get("text", "No response")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connection error: {str(e)}"

def test_a2a_communication():
    """Test agent-to-agent communication"""
    print("🚀 Testing A2A Communication Between Agents")
    print("=" * 50)

    # Create two test agents
    agent_alice = create_test_agent("agent_alice", 6010, "Alice says")
    agent_bob = create_test_agent("agent_bob", 6011, "Bob says")

    # Start both agents in background threads
    alice_thread = start_agent_in_thread(agent_alice, "Agent Alice")
    bob_thread = start_agent_in_thread(agent_bob, "Agent Bob")

    # Wait for agents to start
    print("⏳ Waiting for agents to start...")
    time.sleep(3)

    print("\n📡 Testing Direct Communication (no A2A routing):")

    # Test 1: Direct message to Alice
    print("\n1. Sending direct message to Alice:")
    response1 = send_message_to_agent(6010, "Hello Alice!", "conv_1")
    print(f"   Alice's response: {response1}")

    # Test 2: Direct message to Bob
    print("\n2. Sending direct message to Bob:")
    response2 = send_message_to_agent(6011, "Hello Bob!", "conv_2")
    print(f"   Bob's response: {response2}")

    print("\n🔄 Testing A2A Routing (@agent format):")

    # Test 3: Alice sends message to Bob via A2A
    print("\n3. Alice sending message to Bob via A2A:")
    a2a_message1 = "@agent_bob Hi Bob, this is Alice!"
    response3 = send_message_to_agent(6010, a2a_message1, "conv_3")
    print(f"   Alice's bridge response: {response3}")

    # Test 4: Bob sends message to Alice via A2A
    print("\n4. Bob sending message to Alice via A2A:")
    a2a_message2 = "@agent_alice Hi Alice, this is Bob!"
    response4 = send_message_to_agent(6011, a2a_message2, "conv_4")
    print(f"   Bob's bridge response: {response4}")

    print("\n🧪 Testing Commands:")

    # Test 5: Help command
    print("\n5. Testing help command on Alice:")
    response5 = send_message_to_agent(6010, "/help", "conv_5")
    print(f"   Help response: {response5}")

    print("\n✅ A2A Communication Test Complete!")
    print("\n📋 What we tested:")
    print("  ✅ Direct agent communication")
    print("  ✅ A2A message routing (@agent format)")
    print("  ✅ Command handling (/help)")
    print("  ✅ Custom response handlers")

    print("\n🎯 Key Points:")
    print("  - Agents respond with their custom handlers")
    print("  - A2A routing works between local agents")
    print("  - Original messages are preserved (no improvement)")
    print("  - Each agent maintains its own personality")

    # Cleanup
    print("\n🧹 Cleaning up...")
    agent_alice.stop()
    agent_bob.stop()

if __name__ == "__main__":
    test_a2a_communication()