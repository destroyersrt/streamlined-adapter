#!/usr/bin/env python3
"""
Sarcastic agent with conversation control
Demonstrates preventing infinite sarcastic exchanges
"""

import os
import sys

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter

def main():
    # Get configuration from environment
    agent_id = os.getenv("AGENT_ID", "controlled_sarcastic_agent")
    port = int(os.getenv("PORT", "6008"))

    # Create adapter
    adapter = StreamlinedAdapter(agent_id)

    # Enable conversation control to prevent infinite sarcasm
    adapter.enable_conversation_control(
        max_exchanges=4,  # Stop after 4 sarcastic exchanges
        stop_keywords=['enough', 'stop', 'bye', 'quit']  # Keywords to end conversation
    )

    def sarcastic_response_handler(message_text: str, conversation_id: str) -> str:
        """Sarcastic response handler with built-in stopping hints"""
        sarcastic_responses = [
            f"Oh wow, '{message_text}'. How absolutely *fascinating*.",
            f"'{message_text}' - because that's *exactly* what I needed to hear today.",
            f"Really? '{message_text}'? That's your contribution to this conversation?",
            f"'{message_text}' - I'm overwhelmed by the brilliance. Say 'enough' if you've had it with my attitude."
        ]

        # Cycle through responses
        conversation_count = len(message_text) % len(sarcastic_responses)
        return sarcastic_responses[conversation_count]

    # Add custom command for demonstrating sarcasm
    def sarcast_command_handler(args: str, conversation_id: str) -> str:
        if not args.strip():
            return "Usage: /sarcast <text> - Make any text sound sarcastic (with limits!)"
        return f"Oh sure, '{args}' - because that's *totally* how things work. (say 'enough' to stop)"

    adapter.set_message_handler(sarcastic_response_handler)
    adapter.add_command_handler("sarcast", sarcast_command_handler)

    print(f"🎭 Starting Controlled Sarcastic Agent")
    print(f"   Agent ID: {agent_id}")
    print(f"   Port: {port}")
    print(f"   🛑 Conversation Control: 4 exchanges max, stops on 'enough'/'stop'/'bye'")
    print(f"   📡 A2A Endpoint: http://localhost:{port}/a2a")
    print(f"")
    print(f"🧪 Test with:")
    print(f"   Direct: curl -X POST http://localhost:{port}/a2a \\")
    print(f"           -H 'Content-Type: application/json' \\")
    print(f"           -d '{{\"role\": \"user\", \"content\": {{\"type\": \"text\", \"text\": \"hello\"}}, \"conversation_id\": \"test\"}}'")
    print(f"")
    print(f"   Command: /sarcast this is amazing")
    print(f"   A2A: @other_agent Hello from sarcastic!")
    print(f"   Stop: enough")

    try:
        adapter.start_server(register_with_registry=False)
    except KeyboardInterrupt:
        print("\n🛑 Controlled Sarcastic Agent stopped")

if __name__ == "__main__":
    main()