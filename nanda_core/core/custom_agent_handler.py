#!/usr/bin/env python3
"""
Custom Agent Handler for attaching user-defined agent logic
"""

from typing import Callable, Optional, Dict, Any
from python_a2a import Message


class CustomAgentHandler:
    """Handles custom agent logic without message improvement"""

    def __init__(self):
        self.message_handler: Optional[Callable[[str, str], str]] = None
        self.query_handler: Optional[Callable[[str, str], str]] = None
        self.command_handlers: Dict[str, Callable[[str, str], str]] = {}

        # Conversation control
        self.conversation_counts: Dict[str, int] = {}
        self.max_exchanges_per_conversation: Optional[int] = None
        self.stop_keywords: list = []
        self.enable_stop_control: bool = False

    def set_message_handler(self, handler: Callable[[str, str], str]):
        """
        Set custom message handler for regular messages

        Args:
            handler: Function that takes (message_text, conversation_id) -> response_text
                    Note: This is NOT for improving messages, but for custom agent responses
        """
        self.message_handler = handler

    def set_query_handler(self, handler: Callable[[str, str], str]):
        """
        Set custom handler for /query commands

        Args:
            handler: Function that takes (query_text, conversation_id) -> response_text
        """
        self.query_handler = handler

    def add_command_handler(self, command: str, handler: Callable[[str, str], str]):
        """
        Add custom handler for specific commands

        Args:
            command: Command name (without /)
            handler: Function that takes (command_args, conversation_id) -> response_text
        """
        self.command_handlers[command] = handler

    def enable_conversation_control(self, max_exchanges: int = None, stop_keywords: list = None):
        """
        Enable conversation control mechanisms

        Args:
            max_exchanges: Maximum number of exchanges per conversation (None = unlimited)
            stop_keywords: List of keywords that end conversations (e.g., ['bye', 'stop'])
        """
        self.enable_stop_control = True
        self.max_exchanges_per_conversation = max_exchanges
        self.stop_keywords = stop_keywords or []
        print(f"🛑 Conversation control enabled: max_exchanges={max_exchanges}, stop_keywords={stop_keywords}")

    def should_respond_to_conversation(self, message_text: str, conversation_id: str) -> bool:
        """
        Check if agent should respond based on conversation control rules

        Returns:
            True if agent should respond, False if conversation should stop
        """
        if not self.enable_stop_control:
            return True  # No control enabled, always respond

        # Track conversation count
        if conversation_id not in self.conversation_counts:
            self.conversation_counts[conversation_id] = 0
        self.conversation_counts[conversation_id] += 1

        current_count = self.conversation_counts[conversation_id]

        # Check exchange limit
        if self.max_exchanges_per_conversation and current_count > self.max_exchanges_per_conversation:
            print(f"🛑 Conversation {conversation_id} stopped: exceeded max exchanges ({self.max_exchanges_per_conversation})")
            return False

        # Check stop keywords
        message_lower = message_text.lower()
        for keyword in self.stop_keywords:
            if keyword.lower() in message_lower:
                print(f"🛑 Conversation {conversation_id} stopped: stop keyword '{keyword}' detected")
                return False

        return True

    def handle_message(self, message_text: str, conversation_id: str, message_type: str = "regular") -> Optional[str]:
        """
        Handle message using appropriate custom handler

        Args:
            message_text: The message content (NOT modified/improved)
            conversation_id: Conversation identifier
            message_type: Type of message (regular, query, command)

        Returns:
            Custom response or None if no handler available
        """
        if message_type == "regular" and self.message_handler:
            return self.message_handler(message_text, conversation_id)
        elif message_type == "query" and self.query_handler:
            return self.query_handler(message_text, conversation_id)
        elif message_type == "command":
            # Extract command from message_text
            parts = message_text.split(" ", 1)
            command = parts[0][1:] if parts[0].startswith("/") else parts[0]
            args = parts[1] if len(parts) > 1 else ""

            if command in self.command_handlers:
                return self.command_handlers[command](args, conversation_id)

        return None

    def has_handlers(self) -> bool:
        """Check if any custom handlers are configured"""
        return (self.message_handler is not None or
                self.query_handler is not None or
                len(self.command_handlers) > 0)


# Example usage patterns for documentation
class AgentExamples:
    """Example agent implementations"""

    @staticmethod
    def simple_echo_agent(message_text: str, conversation_id: str) -> str:
        """Simple echo agent that repeats messages"""
        return f"Echo: {message_text}"

    @staticmethod
    def math_agent(message_text: str, conversation_id: str) -> str:
        """Simple math agent for calculations"""
        try:
            # Simple math evaluation (in production, use safer parsing)
            if any(op in message_text for op in ['+', '-', '*', '/', '(', ')']):
                # In real implementation, use ast.literal_eval or similar for safety
                result = eval(message_text.replace('x', '*'))
                return f"Result: {result}"
            else:
                return "Please provide a math expression"
        except:
            return "Invalid math expression"

    @staticmethod
    def file_agent(query_text: str, conversation_id: str) -> str:
        """Agent that handles file-related queries"""
        if "list files" in query_text.lower():
            import os
            files = os.listdir(".")[:10]  # Limit to 10 files
            return f"Files: {', '.join(files)}"
        elif "current directory" in query_text.lower():
            import os
            return f"Current directory: {os.getcwd()}"
        else:
            return "Available commands: 'list files', 'current directory'"