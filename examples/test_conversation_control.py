#!/usr/bin/env python3
"""
Test script for conversation control mechanisms
Demonstrates how agents stop A2A conversations
"""

import os
import sys
import time
import requests
import json

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def send_message(port: int, message: str, conversation_id: str) -> dict:
    """Send a message to an agent"""
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
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

def check_agent_running(port: int) -> bool:
    """Check if agent is running"""
    try:
        response = requests.get(f"http://localhost:{port}/a2a", timeout=3)
        return response.status_code in [200, 405]
    except Exception:
        return False

def test_exchange_limit():
    """Test the exchange limit functionality"""
    print("📊 Test 1: Exchange Limit (Limited Agent)")
    print("-" * 40)

    if not check_agent_running(6004):
        print("❌ Limited agent not running on port 6004")
        return

    conversation_id = "exchange_limit_test"

    # Send multiple messages to trigger the limit
    for i in range(5):
        print(f"\n📤 Message {i+1}:")
        response = send_message(6004, f"Message {i+1} to test limit", conversation_id)

        if "error" in response:
            print(f"   ❌ Error: {response['error']}")
        else:
            content = response.get("content", {})
            text = content.get("text", "No response")
            print(f"   📨 Response: {text}")

        time.sleep(1)

    print("\n🎯 Expected: Agent should stop responding after 3 exchanges")

def test_keyword_stopping():
    """Test the keyword stopping functionality"""
    print("\n📊 Test 2: Keyword Stopping (Keyword Agent)")
    print("-" * 40)

    if not check_agent_running(6005):
        print("❌ Keyword agent not running on port 6005")
        return

    conversation_id = "keyword_test"

    # Send normal messages
    messages = [
        "Hello keyword agent!",
        "How are you doing?",
        "This is a test message",
        "bye"  # This should trigger stop
    ]

    for i, message in enumerate(messages, 1):
        print(f"\n📤 Message {i}: '{message}'")
        response = send_message(6005, message, conversation_id)

        if "error" in response:
            print(f"   ❌ Error: {response['error']}")
        else:
            content = response.get("content", {})
            text = content.get("text", "No response")
            print(f"   📨 Response: {text}")

        time.sleep(1)

    print("\n🎯 Expected: Agent should stop responding after 'bye' keyword")

def test_combined_control():
    """Test combined exchange limit and keyword stopping"""
    print("\n📊 Test 3: Combined Control (Combined Agent)")
    print("-" * 40)

    if not check_agent_running(6006):
        print("❌ Combined agent not running on port 6006")
        return

    # Test keyword stopping first
    print("\n🔤 Testing keyword stopping:")
    conversation_id = "combined_keyword_test"

    response = send_message(6006, "Testing combined agent", conversation_id)
    print(f"   📨 Response 1: {response.get('content', {}).get('text', 'No response')}")

    response = send_message(6006, "stop", conversation_id)  # Should trigger stop
    print(f"   📨 Response 2: {response.get('content', {}).get('text', 'No response')}")

    # Test exchange limit
    print("\n🔢 Testing exchange limit:")
    conversation_id = "combined_limit_test"

    for i in range(7):  # Try to exceed the 5 exchange limit
        response = send_message(6006, f"Exchange {i+1}", conversation_id)
        text = response.get("content", {}).get("text", "No response")
        print(f"   📨 Response {i+1}: {text}")
        time.sleep(0.5)

    print("\n🎯 Expected: Agent stops on 'stop' keyword OR after 5 exchanges")

def test_unlimited_agent():
    """Test unlimited agent (no stopping logic)"""
    print("\n📊 Test 4: Unlimited Agent (No Control)")
    print("-" * 40)

    if not check_agent_running(6007):
        print("❌ Unlimited agent not running on port 6007")
        return

    conversation_id = "unlimited_test"

    # Send a few messages to show it never stops
    for i in range(3):
        print(f"\n📤 Message {i+1}:")
        response = send_message(6007, f"Message {i+1} - unlimited test", conversation_id)

        if "error" in response:
            print(f"   ❌ Error: {response['error']}")
        else:
            content = response.get("content", {})
            text = content.get("text", "No response")
            print(f"   📨 Response: {text}")

        time.sleep(1)

    print("\n🎯 Expected: Agent responds to every message indefinitely")

def test_a2a_conversation_control():
    """Test A2A conversation between controlled agents"""
    print("\n📊 Test 5: A2A Conversation Control")
    print("-" * 40)

    # Test limited agent sending to keyword agent
    print("\n🔄 Limited agent → Keyword agent:")
    conversation_id = "a2a_control_test"

    # This should create a conversation that stops due to limited agent's 3-exchange limit
    response = send_message(6004, "@keyword_agent Hello from limited agent!", conversation_id)
    text = response.get("content", {}).get("text", "No response")
    print(f"   📨 Initial response: {text}")

    time.sleep(2)

    # Check if the conversation continued (it should have stopped)
    print("\n   🔍 Checking if conversation stopped naturally...")
    print("   🎯 Limited agent should stop after 3 exchanges")

def main():
    """Run all conversation control tests"""
    print("🛑 Conversation Control Testing Suite")
    print("=" * 50)

    print("\n📋 Prerequisites:")
    print("  1. Run: python examples/controlled_agents.py")
    print("  2. Wait for all agents to start")
    print("  3. Run this test script")

    # Check if agents are running
    agents = [
        (6004, "Limited Agent"),
        (6005, "Keyword Agent"),
        (6006, "Combined Agent"),
        (6007, "Unlimited Agent")
    ]

    print(f"\n🔍 Checking agent availability:")
    missing_agents = []
    for port, name in agents:
        if check_agent_running(port):
            print(f"   ✅ {name} (port {port})")
        else:
            print(f"   ❌ {name} (port {port}) - NOT RUNNING")
            missing_agents.append(name)

    if missing_agents:
        print(f"\n❌ Missing agents: {', '.join(missing_agents)}")
        print("   Please start controlled_agents.py first")
        return

    print(f"\n🚀 Starting conversation control tests...")

    # Run all tests
    test_exchange_limit()
    test_keyword_stopping()
    test_combined_control()
    test_unlimited_agent()
    test_a2a_conversation_control()

    print(f"\n✅ Conversation Control Tests Complete!")
    print(f"\n📋 Summary:")
    print(f"  🛑 Exchange limits prevent infinite loops")
    print(f"  🔤 Keywords provide natural conversation endings")
    print(f"  🔄 Combined controls offer flexible stopping")
    print(f"  ⚠️  Unlimited agents risk infinite conversations")
    print(f"  🎯 Choose appropriate control for your use case")

if __name__ == "__main__":
    main()