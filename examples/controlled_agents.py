#!/usr/bin/env python3
"""
Example agents with conversation control mechanisms
Demonstrates different stopping strategies for A2A communication
"""

import os
import sys
import time
import threading

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter

def create_limited_agent():
    """Agent that stops after 3 exchanges"""
    os.environ["AGENT_ID"] = "limited_agent"
    os.environ["PORT"] = "6004"

    adapter = StreamlinedAdapter("limited_agent")

    # Enable conversation control with exchange limit
    adapter.enable_conversation_control(max_exchanges=3)

    def limited_response_handler(message_text: str, conversation_id: str) -> str:
        return f"Limited agent: {message_text} (I stop after 3 exchanges)"

    adapter.set_message_handler(limited_response_handler)
    return adapter

def create_keyword_agent():
    """Agent that stops on specific keywords"""
    os.environ["AGENT_ID"] = "keyword_agent"
    os.environ["PORT"] = "6005"

    adapter = StreamlinedAdapter("keyword_agent")

    # Enable conversation control with stop keywords
    adapter.enable_conversation_control(stop_keywords=['bye', 'stop', 'end', 'goodbye'])

    def keyword_response_handler(message_text: str, conversation_id: str) -> str:
        return f"Keyword agent: {message_text} (say 'bye' to stop)"

    adapter.set_message_handler(keyword_response_handler)
    return adapter

def create_combined_agent():
    """Agent with both exchange limit and keyword stopping"""
    os.environ["AGENT_ID"] = "combined_agent"
    os.environ["PORT"] = "6006"

    adapter = StreamlinedAdapter("combined_agent")

    # Enable both controls
    adapter.enable_conversation_control(max_exchanges=5, stop_keywords=['bye', 'stop'])

    def combined_response_handler(message_text: str, conversation_id: str) -> str:
        return f"Combined agent: {message_text} (max 5 exchanges OR say 'stop')"

    adapter.set_message_handler(combined_response_handler)
    return adapter

def create_unlimited_agent():
    """Agent with no conversation control (original behavior)"""
    os.environ["AGENT_ID"] = "unlimited_agent"
    os.environ["PORT"] = "6007"

    adapter = StreamlinedAdapter("unlimited_agent")

    # No conversation control enabled
    def unlimited_response_handler(message_text: str, conversation_id: str) -> str:
        return f"Unlimited agent: {message_text} (I never stop responding)"

    adapter.set_message_handler(unlimited_response_handler)
    return adapter

def start_agent_async(adapter, name):
    """Start an agent in background thread"""
    def run():
        try:
            print(f"🚀 Starting {name}...")
            adapter.start_server(register_with_registry=False)
        except Exception as e:
            print(f"Error starting {name}: {e}")

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return thread

def main():
    """Demonstrate conversation control agents"""
    print("🛑 Conversation Control Agent Demo")
    print("=" * 40)

    agents = [
        (create_limited_agent(), "Limited Agent (3 exchanges)"),
        (create_keyword_agent(), "Keyword Agent ('bye' to stop)"),
        (create_combined_agent(), "Combined Agent (5 exchanges OR 'stop')"),
        (create_unlimited_agent(), "Unlimited Agent (no control)")
    ]

    threads = []

    # Start all agents
    for adapter, name in agents:
        thread = start_agent_async(adapter, name)
        threads.append((thread, name))
        time.sleep(2)  # Stagger startup

    print(f"\n✅ All agents started!")
    print(f"\n📡 Agent endpoints:")
    print(f"  Limited Agent:    http://localhost:6004/a2a")
    print(f"  Keyword Agent:    http://localhost:6005/a2a")
    print(f"  Combined Agent:   http://localhost:6006/a2a")
    print(f"  Unlimited Agent:  http://localhost:6007/a2a")

    print(f"\n🧪 Test conversation control:")
    print(f"""
# Test limited agent (stops after 3)
curl -X POST http://localhost:6004/a2a \\
  -H "Content-Type: application/json" \\
  -d '{{"role": "user", "content": {{"type": "text", "text": "@keyword_agent Hello!"}}, "conversation_id": "test_limit"}}'

# Test keyword agent (say 'bye' to stop)
curl -X POST http://localhost:6005/a2a \\
  -H "Content-Type: application/json" \\
  -d '{{"role": "user", "content": {{"type": "text", "text": "@limited_agent Hey there!"}}, "conversation_id": "test_keyword"}}'

# Test with stop keyword
curl -X POST http://localhost:6005/a2a \\
  -H "Content-Type: application/json" \\
  -d '{{"role": "user", "content": {{"type": "text", "text": "bye"}}, "conversation_id": "test_keyword"}}'
    """)

    print(f"\n🎯 Expected behavior:")
    print(f"  ✅ Limited agent stops after 3rd exchange")
    print(f"  ✅ Keyword agent stops when it sees 'bye'")
    print(f"  ✅ Combined agent stops on either condition")
    print(f"  ⚠️  Unlimited agent never stops (infinite risk)")

    print(f"\n🛑 Press Ctrl+C to stop all agents")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all agents...")
        for adapter, _ in agents:
            adapter.stop()
        print("✅ All agents stopped")

if __name__ == "__main__":
    main()