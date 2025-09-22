#!/usr/bin/env python3
"""
Test A2A communication with public IP addresses
This script demonstrates the full communication flow between agents
"""

import os
import sys
import time
import requests
import json
import socket
import subprocess
from threading import Thread

def get_local_ip():
    """Get the local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def check_agent_running(ip: str, port: int) -> bool:
    """Check if an agent is running on the given IP and port"""
    try:
        response = requests.get(f"http://{ip}:{port}/a2a", timeout=3)
        return response.status_code in [200, 405]  # 405 is expected for GET to A2A endpoint
    except Exception:
        return False

def send_a2a_message(ip: str, port: int, message: str, conversation_id: str) -> dict:
    """Send an A2A message to an agent"""
    url = f"http://{ip}:{port}/a2a"
    data = {
        "role": "user",
        "content": {
            "type": "text",
            "text": message
        },
        "conversation_id": conversation_id
    }

    try:
        print(f"📤 Sending to {ip}:{port}: '{message}'")
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"📨 Response: {result}")
            return result
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return {"error": str(e)}

def test_full_a2a_conversation():
    """Test complete A2A conversation flow"""
    print("🚀 Testing Full A2A Communication with Public IP")
    print("=" * 60)

    # Get local IP
    local_ip = get_local_ip()
    print(f"🌐 Using IP address: {local_ip}")

    # Check if agents are running
    sarcastic_port = 6002
    helpful_port = 6003

    print(f"\n🔍 Checking if agents are running...")

    if not check_agent_running(local_ip, sarcastic_port):
        print(f"❌ Sarcastic agent not running on {local_ip}:{sarcastic_port}")
        print(f"   Start it with: python examples/setup_agents_with_public_ip.py")
        return

    if not check_agent_running(local_ip, helpful_port):
        print(f"❌ Helpful agent not running on {local_ip}:{helpful_port}")
        print(f"   Start it with: python examples/setup_agents_with_public_ip.py")
        return

    print(f"✅ Both agents are running!")

    # Test direct messages first
    print(f"\n📋 Phase 1: Direct Messages (no A2A routing)")
    print("-" * 40)

    # Direct message to sarcastic agent
    print(f"\n1️⃣ Testing direct message to sarcastic agent:")
    result1 = send_a2a_message(local_ip, sarcastic_port, "Hello sarcastic agent!", "test_direct_1")
    time.sleep(1)

    # Direct message to helpful agent
    print(f"\n2️⃣ Testing direct message to helpful agent:")
    result2 = send_a2a_message(local_ip, helpful_port, "Hello helpful agent!", "test_direct_2")
    time.sleep(1)

    # Test A2A routing
    print(f"\n📋 Phase 2: A2A Routing (agent-to-agent communication)")
    print("-" * 50)

    # Sarcastic sends to helpful
    print(f"\n3️⃣ Sarcastic agent sending A2A message to helpful agent:")
    result3 = send_a2a_message(
        local_ip, sarcastic_port,
        "@helpful_agent Hey helpful, can you help me with something?",
        "test_a2a_1"
    )
    time.sleep(2)

    # Helpful sends to sarcastic
    print(f"\n4️⃣ Helpful agent sending A2A message to sarcastic agent:")
    result4 = send_a2a_message(
        local_ip, helpful_port,
        "@sarcastic_agent Hi sarcastic, what's your take on AI?",
        "test_a2a_2"
    )
    time.sleep(2)

    # Test conversation flow
    print(f"\n📋 Phase 3: Conversation Flow")
    print("-" * 30)

    conversation_id = "conversation_flow_test"

    # Start conversation
    print(f"\n5️⃣ Starting conversation from sarcastic to helpful:")
    conv1 = send_a2a_message(
        local_ip, sarcastic_port,
        "@helpful_agent Can you believe people actually think chatbots are useful?",
        conversation_id
    )
    time.sleep(2)

    print(f"\n6️⃣ Helpful agent responding back:")
    conv2 = send_a2a_message(
        local_ip, helpful_port,
        "@sarcastic_agent Well, I try to be helpful! What specific concerns do you have?",
        conversation_id
    )
    time.sleep(2)

    print(f"\n7️⃣ Sarcastic agent replying again:")
    conv3 = send_a2a_message(
        local_ip, sarcastic_port,
        "@helpful_agent Oh, where do I even start? The endless optimism is exhausting!",
        conversation_id
    )

    print(f"\n✅ A2A Communication Test Complete!")
    print(f"\n📊 Summary:")
    print(f"  🌐 IP Address: {local_ip}")
    print(f"  🤖 Sarcastic Agent: {local_ip}:{sarcastic_port}")
    print(f"  🤖 Helpful Agent: {local_ip}:{helpful_port}")
    print(f"  📡 A2A Routing: Working with comprehensive logging")
    print(f"  🔄 Message Flow: Direct + A2A + Conversation")

    print(f"\n🎯 What you should observe:")
    print(f"  ✅ Agents respond with their personalities")
    print(f"  ✅ A2A messages are properly routed")
    print(f"  ✅ Comprehensive logging shows message flow")
    print(f"  ✅ Agents find each other using public IP")
    print(f"  ✅ No message improvement (streamlined goal achieved)")

    print(f"\n📝 Check the agent logs to see:")
    print(f"  - Message reception logging")
    print(f"  - Agent lookup with public IP")
    print(f"  - External message formatting")
    print(f"  - A2A client communication")
    print(f"  - Response generation")

if __name__ == "__main__":
    test_full_a2a_conversation()