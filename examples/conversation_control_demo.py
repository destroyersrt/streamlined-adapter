#!/usr/bin/env python3
"""
Demonstration of A2A conversation control mechanisms
Shows different ways to stop agent conversations
"""

import os
import sys
import time
import requests

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter

def create_agent_with_stop_logic(agent_id: str, port: int, stop_strategy: str):
    """Create an agent with different stopping strategies"""

    os.environ["AGENT_ID"] = agent_id
    os.environ["PORT"] = str(port)

    adapter = StreamlinedAdapter(agent_id)

    # Conversation tracking
    conversation_counts = {}

    def smart_response_handler(message_text: str, conversation_id: str) -> str:
        """Response handler with built-in stopping logic"""

        # Track conversation count
        if conversation_id not in conversation_counts:
            conversation_counts[conversation_id] = 0
        conversation_counts[conversation_id] += 1

        count = conversation_counts[conversation_id]

        if stop_strategy == "count_limit":
            # Stop after 3 exchanges
            if count > 3:
                return None  # No response = conversation stops
            return f"{agent_id} response #{count}: {message_text} (will stop after 3)"

        elif stop_strategy == "keyword_stop":
            # Stop if message contains "bye" or "stop"
            if any(word in message_text.lower() for word in ["bye", "stop", "end"]):
                return f"{agent_id}: Goodbye! Ending conversation."
            return f"{agent_id}: {message_text} (say 'bye' to stop)"

        elif stop_strategy == "alternating":
            # Only respond to odd-numbered messages
            if count % 2 == 0:
                return None  # Skip even responses
            return f"{agent_id} (selective response #{count}): {message_text}"

        elif stop_strategy == "probability":
            # 50% chance to respond
            import random
            if random.random() < 0.5:
                return None
            return f"{agent_id} (random response #{count}): {message_text}"

        else:  # "no_stop" - always respond
            return f"{agent_id} response #{count}: {message_text}"

    adapter.set_message_handler(smart_response_handler)
    return adapter

def test_conversation_strategies():
    """Test different conversation stopping strategies"""
    print("🛑 A2A Conversation Control Demonstration")
    print("=" * 50)

    strategies = {
        "count_limit": "Stop after 3 exchanges",
        "keyword_stop": "Stop on 'bye', 'stop', 'end'",
        "alternating": "Only respond to odd messages",
        "probability": "50% chance to respond",
        "no_stop": "Never stop (infinite)"
    }

    print("📋 Available stopping strategies:")
    for strategy, description in strategies.items():
        print(f"  {strategy}: {description}")

    print(f"\n🎯 Recommendations:")
    print(f"  ✅ count_limit: Prevents infinite loops")
    print(f"  ✅ keyword_stop: Natural conversation ending")
    print(f"  ⚠️  alternating: Creates sparse conversations")
    print(f"  ⚠️  probability: Unpredictable behavior")
    print(f"  ❌ no_stop: Risk of infinite loops")

if __name__ == "__main__":
    test_conversation_strategies()