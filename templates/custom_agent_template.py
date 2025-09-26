#!/usr/bin/env python3
"""
Custom NANDA Agent Template

Copy this template and modify the agent_logic function to create your own agent.
"""

import os
import sys

# Add the streamlined adapter to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import NANDA


def my_custom_agent_logic(message: str, conversation_id: str) -> str:
    """
    Define your agent's behavior here.
    
    Args:
        message: The incoming message text
        conversation_id: Unique conversation identifier
        
    Returns:
        Your agent's response string
    """
    
    # Example: Simple keyword-based responses
    message_lower = message.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        return "Hello! I'm a custom NANDA agent. How can I help you?"
    
    elif "time" in message_lower:
        from datetime import datetime
        return f"Current time: {datetime.now().strftime('%H:%M:%S')}"
    
    elif "help" in message_lower:
        return """I'm a custom agent. I can:
        • Respond to greetings
        • Tell you the time  
        • Answer basic questions
        • Route messages to other agents with @agent_id
        
        What would you like to do?"""
    
    elif "calculate" in message_lower or any(op in message for op in ['+', '-', '*', '/']):
        try:
            # Simple calculator (be careful with eval in production!)
            expression = message.replace('calculate', '').strip()
            result = eval(expression)
            return f"Result: {result}"
        except:
            return "I can help with simple math. Try: 5 + 3"
    
    else:
        # Default response
        return f"I received: '{message}'. Type 'help' for what I can do!"


def main():
    """Main function to start your custom agent"""
    
    # Check for API key (if your agent needs external services)
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️ ANTHROPIC_API_KEY not set (may be needed for some features)")
    
    # Create your NANDA agent (modify these parameters)
    nanda = NANDA(
        agent_id="my_custom_agent",           # Change this to your agent name
        agent_logic=my_custom_agent_logic,    # Your agent logic function
        port=6030,                            # Change port if needed
        registry_url=None,                    # Add registry URL if you have one
        public_url=None,                      # Add public URL for registration
        enable_telemetry=False                # Enable to track usage
    )
    
    print("""
🤖 Custom NANDA Agent Starting
===============================
Agent ID: my_custom_agent
Port: 6030
Type: Custom Logic
===============================

📝 Test your agent:
• Send: 'hello'
• Send: 'what time is it?'
• Send: 'calculate 5 + 3'
• Send: 'help'
• Send: '@other_agent message' (to talk to other agents)

🛑 Press Ctrl+C to stop
    """)
    
    try:
        nanda.start(register=False)  # Set to True if you have a registry
    except KeyboardInterrupt:
        print("\n🛑 Custom agent stopped")


if __name__ == "__main__":
    main()

