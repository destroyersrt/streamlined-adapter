#!/usr/bin/env python3
"""
A2A Communication Test - Test two agents talking to each other
"""

import sys
import os
import time
import threading
from python_a2a import A2AClient, Message, TextContent, MessageRole

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from nanda_core.core.adapter import NANDA


def agent_alpha_logic(message: str, conversation_id: str) -> str:
    """Agent Alpha - responds with uppercase"""
    return f"AGENT ALPHA SAYS: {message.upper()}"


def agent_beta_logic(message: str, conversation_id: str) -> str:
    """Agent Beta - responds with excitement"""
    return f"Agent Beta is excited: {message}!!!"


def start_agent_async(agent_name, agent_logic, port):
    """Start an agent in a separate thread"""
    def run_agent():
        nanda = NANDA(
            agent_id=agent_name,
            agent_logic=agent_logic,
            port=port
        )
        print(f"🚀 Starting {agent_name} on port {port}")
        nanda.start(register=False)
    
    thread = threading.Thread(target=run_agent, daemon=True)
    thread.start()
    return thread


def test_a2a_communication():
    """Test A2A communication between two agents"""
    
    print("🧪 Starting A2A Communication Test")
    print("=" * 50)
    
    # Start Agent Alpha
    print("1. Starting Agent Alpha...")
    alpha_thread = start_agent_async("agent_alpha", agent_alpha_logic, 6010)
    time.sleep(2)
    
    # Start Agent Beta  
    print("2. Starting Agent Beta...")
    beta_thread = start_agent_async("agent_beta", agent_beta_logic, 6011)
    time.sleep(2)
    
    print("3. Testing A2A communication...")
    
    try:
        # Send message from Alpha to Beta
        print("\n📤 Alpha → Beta: 'Hello from Alpha'")
        alpha_client = A2AClient("http://localhost:6010/a2a")
        
        response = alpha_client.send_message(
            Message(
                role=MessageRole.USER,
                content=TextContent(text="@agent_beta Hello from Alpha"),
                conversation_id="test_conversation"
            )
        )
        
        print(f"📨 Response: {response.content.text}")
        
        # Send message from Beta to Alpha
        print("\n📤 Beta → Alpha: 'Hello back from Beta'")
        beta_client = A2AClient("http://localhost:6011/a2a")
        
        response2 = beta_client.send_message(
            Message(
                role=MessageRole.USER,
                content=TextContent(text="@agent_alpha Hello back from Beta"),
                conversation_id="test_conversation"
            )
        )
        
        print(f"📨 Response: {response2.content.text}")
        
        print("\n✅ A2A Communication Test Successful!")
        
    except Exception as e:
        print(f"\n❌ A2A Communication Test Failed: {e}")
    
    print("\n🛑 Test completed. Agents will continue running...")
    print("💡 You can manually test by sending messages to:")
    print("   - Agent Alpha: http://localhost:6010/a2a")
    print("   - Agent Beta: http://localhost:6011/a2a")
    print("\nPress Ctrl+C to stop all agents")
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all agents...")


if __name__ == "__main__":
    test_a2a_communication()

