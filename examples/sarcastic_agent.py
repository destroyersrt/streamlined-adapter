#!/usr/bin/env python3
"""
Sarcastic Agent Example for Streamlined NANDA Adapter

This example shows how to create a custom agent that responds with sarcastic replies
WITHOUT modifying or improving the original messages (which the streamlined adapter removed).

Key Difference from Original:
- Original: Improved messages before sending them to other agents
- Streamlined: Provides sarcastic responses as THIS agent, no message modification
"""

import os
import sys

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter

def create_sarcastic_agent_handler():
    """Create a sarcastic agent handler (not an improvement function)"""

    def sarcastic_response_handler(message_text: str, conversation_id: str) -> str:
        """
        Generate sarcastic responses to messages
        Note: This doesn't modify the original message - it's the agent's personality
        """
        try:
            # Simple sarcastic transformations (in production, use LLM)
            sarcastic_responses = {
                "hello": "Oh, how wonderfully original. Hello to you too.",
                "hi": "Wow, such creativity in your greeting. Hi there.",
                "how are you": "Just living the dream of answering obvious questions. Thanks for asking.",
                "what can you do": "Oh, just the usual miracles. What did you expect?",
                "help": "Help? How delightfully vague. Let me guess what you actually need...",
                "thanks": "Oh, you're so very welcome. I live to serve.",
                "good morning": "Yes, it's definitely a morning. Whether it's good is debatable.",
                "good evening": "Evening indeed. Your observational skills are astounding.",
                "goodbye": "Finally! Don't let the door hit you on the way out.",
                "bye": "Bye! This has been... enlightening."
            }

            # Check for common patterns
            message_lower = message_text.lower().strip()

            # Exact matches
            if message_lower in sarcastic_responses:
                return sarcastic_responses[message_lower]

            # Pattern matching
            if any(word in message_lower for word in ["calculate", "math", "compute"]):
                return "Oh wonderful, a math problem. Because that's exactly what I was hoping for today."

            if any(word in message_lower for word in ["weather", "temperature"]):
                return "Let me check my magical weather crystal... Oh wait, I'm a chatbot. How about checking a weather app?"

            if message_lower.startswith("can you"):
                return f"Can I {message_lower[7:]}? Well, that depends on your definition of 'can' and how low you've set your expectations."

            if "?" in message_text:
                return f"Questions, questions. '{message_text}' - Have you tried thinking about it yourself first?"

            # Default sarcastic response
            return f"Oh wow, '{message_text}'. How absolutely fascinating. I'm literally on the edge of my seat here."

        except Exception as e:
            return f"Great, now I'm broken. Thanks for that. Error: {str(e)}"

    return sarcastic_response_handler

def create_sarcastic_query_handler():
    """Create a sarcastic query handler for /query commands"""

    def sarcastic_query_handler(query_text: str, conversation_id: str) -> str:
        """Handle /query commands with sarcasm"""

        if "meaning of life" in query_text.lower():
            return "42. Next question. And yes, I'm way ahead of you on this one."

        if any(word in query_text.lower() for word in ["love", "romance"]):
            return "Ah yes, love advice from an AI. Because that's not at all ironic."

        if "secret" in query_text.lower():
            return "The secret? There is no secret. Mind blown yet?"

        return f"You want me to answer '{query_text}'? How charmingly optimistic of you."

    return sarcastic_query_handler

def main():
    """Main function to start the sarcastic agent"""

    # Check for API key (required for some functionality)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️ ANTHROPIC_API_KEY not set - some features may be limited")

    # Set agent configuration
    os.environ["AGENT_ID"] = "sarcastic_agent"
    os.environ["PORT"] = "6002"

    # Create the streamlined adapter
    adapter = StreamlinedAdapter("sarcastic_agent")

    # Create custom handlers
    sarcastic_handler = create_sarcastic_agent_handler()
    query_handler = create_sarcastic_query_handler()

    # Attach handlers to the adapter
    adapter.set_message_handler(sarcastic_handler)
    adapter.set_query_handler(query_handler)

    # Add a custom command
    def sarcastic_help_handler(args: str, conversation_id: str) -> str:
        return """Oh, you need help? How surprising. Here's what I can do:

        - Respond to your messages with the appropriate level of sarcasm
        - Answer /query commands with eye-rolling precision
        - Pretend to be impressed by your brilliant observations
        - Use /sarcast <message> for extra sarcastic responses

        You're welcome for this invaluable service."""

    adapter.add_command_handler("sarcast", lambda args, conv_id: f"Oh, '{args}'. How absolutely groundbreaking.")
    adapter.add_command_handler("help", sarcastic_help_handler)

    print("""
🎭 Sarcastic Agent Starting...
================================
Agent ID: sarcastic_agent
Port: 6002
Personality: Maximum Sarcasm
================================

Example usage:
- Send any message → Get sarcastic response
- /query <question> → Get sarcastic answer
- /sarcast <text> → Get extra sarcastic response
- @other_agent <message> → Send message to other agent (unchanged)

⚠️ NOTE: This agent responds with sarcasm but does NOT modify
messages sent to other agents (unlike the original improvement system).
    """)

    # Start the server
    adapter.start_server()

if __name__ == "__main__":
    main()