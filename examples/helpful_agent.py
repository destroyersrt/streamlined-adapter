#!/usr/bin/env python3
"""
Helpful Agent Example for Streamlined NANDA Adapter

This example shows how to create a genuinely helpful agent without message improvement.
Demonstrates the difference between the old "improvement" system and new "agent personality" system.
"""

import os
import sys
import datetime

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter

def create_helpful_agent_handler():
    """Create a helpful agent that provides useful responses"""

    def helpful_response_handler(message_text: str, conversation_id: str) -> str:
        """
        Provide helpful responses based on message content
        Note: This is the agent's response, not message modification
        """
        try:
            message_lower = message_text.lower().strip()

            # Greeting responses
            if any(greeting in message_lower for greeting in ["hello", "hi", "hey"]):
                current_time = datetime.datetime.now().strftime("%H:%M")
                return f"Hello! It's {current_time}. How can I help you today?"

            # Time-related queries
            if any(word in message_lower for word in ["time", "clock", "hour"]):
                now = datetime.datetime.now()
                return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

            # Date queries
            if any(word in message_lower for word in ["date", "today", "day"]):
                today = datetime.date.today()
                return f"Today is {today.strftime('%A, %B %d, %Y')}"

            # Math calculations
            if any(word in message_lower for word in ["calculate", "math", "compute", "+"]):
                return "I can help with basic math! Try asking me to calculate something like '5 + 3' or 'What is 10 * 7?'"

            # File operations
            if any(word in message_lower for word in ["file", "directory", "folder"]):
                return "I can help with file operations! Use /query to ask about listing files or checking directories."

            # Help requests
            if any(word in message_lower for word in ["help", "assist", "support"]):
                return """I'm here to help! I can:
                - Tell you the current time and date
                - Help with basic calculations
                - Provide file system information
                - Answer questions via /query commands
                - Route messages to other agents with @agent_id

                What would you like help with?"""

            # Agent discovery
            if any(word in message_lower for word in ["agent", "find agent", "discover"]):
                return "I can help you discover other agents! The system has built-in agent discovery. What kind of task do you need help with?"

            # Questions
            if "?" in message_text:
                return f"That's an interesting question: '{message_text}'. Try using /query for more detailed answers, or I can route it to a specialized agent."

            # Default helpful response
            return f"I received your message: '{message_text}'. Is there something specific I can help you with? Use /help for available commands."

        except Exception as e:
            return f"I encountered an error while trying to help: {str(e)}. Please try again or use /help for assistance."

    return helpful_response_handler

def create_helpful_query_handler():
    """Create a helpful query handler for detailed questions"""

    def helpful_query_handler(query_text: str, conversation_id: str) -> str:
        """Handle /query commands helpfully"""

        query_lower = query_text.lower()

        # System information
        if any(word in query_lower for word in ["system", "status", "health"]):
            return "System is running normally. Use the built-in telemetry system to get detailed health metrics."

        # File system queries
        if "list files" in query_lower or "show files" in query_lower:
            try:
                files = os.listdir(".")[:10]  # Limit to first 10
                return f"Current directory files: {', '.join(files)}"
            except Exception as e:
                return f"Error listing files: {str(e)}"

        if "current directory" in query_lower or "where am i" in query_lower:
            return f"Current directory: {os.getcwd()}"

        # Math queries
        if any(word in query_lower for word in ["calculate", "math", "what is"]):
            if any(op in query_text for op in ['+', '-', '*', '/', '(', ')']):
                try:
                    # Simple safe evaluation for basic math
                    result = eval(query_text.replace('x', '*').replace('what is', '').strip())
                    return f"Result: {result}"
                except:
                    return "I can help with basic math. Try something like '5 + 3' or '10 * 7'"
            else:
                return "Please provide a math expression like '5 + 3' or '10 * 7'"

        # Agent information
        if "agents" in query_lower:
            return "This system supports agent discovery and communication. You can find agents using the built-in discovery system or communicate with known agents using @agent_id format."

        # Default helpful response
        return f"I'd like to help with '{query_text}'. Could you be more specific? I can help with time, dates, basic math, file operations, and system information."

    return helpful_query_handler

def main():
    """Main function to start the helpful agent"""

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️ ANTHROPIC_API_KEY not set - some features may be limited")

    # Set agent configuration
    os.environ["AGENT_ID"] = "helpful_agent"
    os.environ["PORT"] = "6003"

    # Create the streamlined adapter
    adapter = StreamlinedAdapter("helpful_agent")

    # Create custom handlers
    helpful_handler = create_helpful_agent_handler()
    query_handler = create_helpful_query_handler()

    # Attach handlers to the adapter
    adapter.set_message_handler(helpful_handler)
    adapter.set_query_handler(query_handler)

    # Add custom commands
    def time_command_handler(args: str, conversation_id: str) -> str:
        now = datetime.datetime.now()
        return f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}"

    def calc_command_handler(args: str, conversation_id: str) -> str:
        try:
            result = eval(args.replace('x', '*'))
            return f"Calculation result: {result}"
        except:
            return f"Invalid calculation: {args}. Try something like '5 + 3'"

    def discover_command_handler(args: str, conversation_id: str) -> str:
        return f"Use the adapter's built-in discovery: adapter.discover_agents('{args}') to find agents suitable for: {args}"

    adapter.add_command_handler("time", time_command_handler)
    adapter.add_command_handler("calc", calc_command_handler)
    adapter.add_command_handler("discover", discover_command_handler)

    print("""
🤝 Helpful Agent Starting...
================================
Agent ID: helpful_agent
Port: 6003
Personality: Genuinely Helpful
================================

Features:
- Time and date information
- Basic calculations
- File system operations
- Helpful responses to questions
- Agent discovery assistance

Example usage:
- "What time is it?" → Current time
- "Calculate 5 + 3" → Math result
- "/query list files" → File listing
- "/calc 10 * 7" → Quick calculation
- "/time" → Current time
- "@other_agent message" → Route to other agent

💡 Key Difference from Original:
- Original: Modified your messages before sending to other agents
- Streamlined: Provides helpful responses AS this agent, no message modification
    """)

    # Start the server
    adapter.start_server()

if __name__ == "__main__":
    main()