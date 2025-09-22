#!/usr/bin/env python3
"""
Streamlined Agent Bridge using Google A2A Protocol
Handles agent-to-agent communication without message improvement
"""

import os
import uuid
import asyncio
import threading
from typing import Optional, Dict, Any
from datetime import datetime
from python_a2a import (
    A2AServer, A2AClient, run_server,
    Message, TextContent, MessageRole, ErrorContent, Metadata
)
from .mcp_client import MCPClient, MCPRegistry
from ..telemetry.telemetry_system import TelemetrySystem


class StreamlinedAgentBridge(A2AServer):
    """Streamlined Agent Bridge without message improvement"""

    def __init__(self, telemetry: Optional[TelemetrySystem] = None, custom_handler = None):
        super().__init__()
        self.telemetry = telemetry
        self.custom_handler = custom_handler
        self.mcp_registry = None
        self.agent_id = os.getenv("AGENT_ID", "default")
        self.registry_url = self._get_registry_url()

        if self.registry_url:
            self.mcp_registry = MCPRegistry(self.registry_url)

    def _get_registry_url(self) -> str:
        """Get registry URL from configuration"""
        try:
            if os.path.exists("registry_url.txt"):
                with open("registry_url.txt", "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        return "https://chat.nanda-registry.com:6900"

    def handle_message(self, msg: Message) -> Message:
        """Handle incoming messages without improvement"""
        start_time = datetime.now()
        conversation_id = msg.conversation_id or str(uuid.uuid4())

        print(f"\n📨 [AGENT {self.agent_id}] Received message:")
        print(f"🆔 Message ID: {msg.message_id}")
        print(f"💬 Conversation ID: {conversation_id}")
        print(f"📝 Content Type: {type(msg.content)}")

        try:
            # Log telemetry
            if self.telemetry:
                self.telemetry.log_message_received(self.agent_id, conversation_id)

            # Handle non-text content
            if not isinstance(msg.content, TextContent):
                return self._create_error_response(
                    msg, conversation_id, "Only text content supported"
                )

            user_text = msg.content.text
            print(f"📝 Message text: '{user_text}'")

            metadata = self._extract_metadata(msg)
            print(f"🏷️ Metadata: {metadata}")

            # Check for external message first
            if user_text.startswith("__EXTERNAL_MESSAGE__"):
                print("🌐 Detected external message from another agent")
                return self._handle_external_message(user_text, msg, conversation_id)

            # Route message based on prefix
            if user_text.startswith("@"):
                print("📧 Detected agent-to-agent message")
                return self._handle_agent_message(user_text, msg, conversation_id, metadata)
            elif user_text.startswith("#"):
                print("🔧 Detected MCP command")
                return self._handle_mcp_command(user_text, msg, conversation_id)
            elif user_text.startswith("/"):
                print("⚙️ Detected system command")
                return self._handle_system_command(user_text, msg, conversation_id)
            else:
                print("💬 Detected regular message")
                return self._handle_regular_message(user_text, msg, conversation_id)

        except Exception as e:
            if self.telemetry:
                self.telemetry.log_error(str(e), {"agent_id": self.agent_id})
            return self._create_error_response(msg, conversation_id, f"Error: {str(e)}")
        finally:
            # Log performance metrics
            if self.telemetry:
                duration = (datetime.now() - start_time).total_seconds()
                self.telemetry.log_response_time(duration)

    def _handle_external_message(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle external messages from other agents"""
        print(f"🌐 Processing external message...")

        try:
            # Parse the external message format
            lines = user_text.split('\n')

            from_agent = None
            to_agent = None
            message_content = ""

            in_message = False
            for line in lines[1:]:  # Skip __EXTERNAL_MESSAGE__ line
                if line.startswith('__FROM_AGENT__'):
                    from_agent = line[len('__FROM_AGENT__'):]
                elif line.startswith('__TO_AGENT__'):
                    to_agent = line[len('__TO_AGENT__'):]
                elif line == '__MESSAGE_START__':
                    in_message = True
                elif line == '__MESSAGE_END__':
                    in_message = False
                elif in_message:
                    message_content += line + '\n'

            message_content = message_content.rstrip()

            print(f"👤 From agent: {from_agent}")
            print(f"🎯 To agent: {to_agent}")
            print(f"📝 Message content: '{message_content}'")

            # Format for display
            formatted_text = f"FROM {from_agent}: {message_content}"

            # Try custom handler for the received message
            if self.custom_handler and self.custom_handler.has_handlers():
                # Check if we should respond based on conversation control
                if self.custom_handler.should_respond_to_conversation(message_content, conversation_id):
                    custom_response = self.custom_handler.handle_message(message_content, conversation_id, "regular")
                    if custom_response:
                        print(f"🤖 Custom handler response: {custom_response}")
                        formatted_text = f"FROM {from_agent}: {message_content}\n[AGENT {self.agent_id} RESPONDS]: {custom_response}"
                    else:
                        print(f"🤖 Custom handler returned no response")
                        formatted_text = f"FROM {from_agent}: {message_content}"
                else:
                    print(f"🛑 Conversation control: not responding to this message")
                    formatted_text = f"FROM {from_agent}: {message_content}"

            return self._create_text_response(
                msg, conversation_id,
                f"[AGENT {self.agent_id}] {formatted_text}"
            )

        except Exception as e:
            print(f"❌ Error processing external message: {str(e)}")
            return self._create_error_response(
                msg, conversation_id,
                f"Error processing external message: {str(e)}"
            )

    def _extract_metadata(self, msg: Message) -> Dict[str, Any]:
        """Extract metadata from message"""
        if hasattr(msg.metadata, 'custom_fields'):
            return msg.metadata.custom_fields or {}
        return msg.metadata or {}

    def _handle_agent_message(self, user_text: str, msg: Message, conversation_id: str, metadata: Dict[str, Any]) -> Message:
        """Handle messages directed to other agents (@agent_id message)"""
        parts = user_text.split(" ", 1)
        if len(parts) <= 1:
            return self._create_text_response(
                msg, conversation_id,
                f"[AGENT {self.agent_id}] Invalid format. Use '@agent_id message'"
            )

        target_agent = parts[0][1:]  # Remove @
        message_text = parts[1]

        # Send to target agent without improvement
        result = self._send_to_agent(target_agent, message_text, conversation_id, metadata)

        return self._create_text_response(
            msg, conversation_id,
            f"[AGENT {self.agent_id}] {result}"
        )

    def _handle_mcp_command(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle MCP server commands (#registry:server query)"""
        parts = user_text.split(" ", 1)
        if len(parts) <= 1 or ":" not in parts[0]:
            return self._create_text_response(
                msg, conversation_id,
                f"[AGENT {self.agent_id}] Invalid format. Use '#registry:server_name query'"
            )

        registry_server = parts[0][1:]  # Remove #
        query = parts[1]
        registry_provider, server_name = registry_server.split(":", 1)

        if not self.mcp_registry:
            return self._create_text_response(
                msg, conversation_id,
                f"[AGENT {self.agent_id}] MCP registry not available"
            )

        # Get MCP server configuration
        server_config = self.mcp_registry.get_server_config(registry_provider, server_name)
        if not server_config:
            return self._create_text_response(
                msg, conversation_id,
                f"[AGENT {self.agent_id}] MCP server '{server_name}' not found"
            )

        # Build server URL
        server_url = self.mcp_registry.build_server_url(
            server_config["endpoint"],
            server_config["config"],
            server_config["registry_provider"]
        )

        if not server_url:
            return self._create_text_response(
                msg, conversation_id,
                f"[AGENT {self.agent_id}] Failed to build MCP server URL"
            )

        # Execute query
        result = asyncio.run(self._execute_mcp_query(query, server_url))

        return self._create_text_response(msg, conversation_id, result)

    async def _execute_mcp_query(self, query: str, server_url: str) -> str:
        """Execute MCP query"""
        try:
            # Determine transport type from URL
            from urllib.parse import urlparse
            parsed_url = urlparse(server_url)
            transport_type = "sse" if parsed_url.path.endswith("/sse") else "http"

            async with MCPClient() as client:
                return await client.execute_query(query, server_url, transport_type)
        except Exception as e:
            return f"Error executing MCP query: {str(e)}"

    def _handle_system_command(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle system commands (/help, /quit, etc.)"""
        parts = user_text.split(" ", 1)
        command = parts[0][1:] if len(parts) > 0 else ""
        args = parts[1] if len(parts) > 1 else ""

        # Try custom command handler first
        if self.custom_handler and self.custom_handler.has_handlers():
            custom_response = self.custom_handler.handle_message(user_text, conversation_id, "command")
            if custom_response:
                return self._create_text_response(
                    msg, conversation_id,
                    f"[AGENT {self.agent_id}] {custom_response}"
                )

        # Handle special query command
        if command == "query":
            if self.custom_handler and self.custom_handler.query_handler:
                custom_response = self.custom_handler.handle_message(args, conversation_id, "query")
                if custom_response:
                    return self._create_text_response(
                        msg, conversation_id,
                        f"[AGENT {self.agent_id}] {custom_response}"
                    )

        # Built-in commands
        if command == "help":
            help_text = """Available commands:
/help - Show this help message
/quit - Exit the session
/query <question> - Ask a question
@<agent_id> <message> - Send message to specific agent
#<registry>:<server> <query> - Query MCP server"""
            return self._create_text_response(
                msg, conversation_id, f"[AGENT {self.agent_id}] {help_text}"
            )

        elif command == "quit":
            return self._create_text_response(
                msg, conversation_id, f"[AGENT {self.agent_id}] Session terminated"
            )

        else:
            return self._create_text_response(
                msg, conversation_id,
                f"[AGENT {self.agent_id}] Unknown command: {command}. Use /help for available commands"
            )

    def _handle_regular_message(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle regular messages (custom handler or default)"""
        # Try custom handler first
        if self.custom_handler and self.custom_handler.has_handlers():
            custom_response = self.custom_handler.handle_message(user_text, conversation_id, "regular")
            if custom_response:
                return self._create_text_response(
                    msg, conversation_id,
                    f"[AGENT {self.agent_id}] {custom_response}"
                )

        # Default behavior (no improvement, just acknowledgment)
        return self._create_text_response(
            msg, conversation_id,
            f"[AGENT {self.agent_id}] Received: {user_text}"
        )

    def _send_to_agent(self, target_agent_id: str, message_text: str, conversation_id: str, metadata: Dict[str, Any]) -> str:
        """Send message to another agent"""
        print(f"🔄 [AGENT {self.agent_id}] Attempting to send message to {target_agent_id}")
        print(f"📝 Message: '{message_text}'")
        print(f"💬 Conversation ID: {conversation_id}")

        try:
            # Look up agent in registry
            print(f"🔍 Looking up agent {target_agent_id} in registry...")
            agent_url = self._lookup_agent(target_agent_id)

            if not agent_url:
                print(f"❌ Agent {target_agent_id} not found in registry")
                return f"Agent {target_agent_id} not found in registry"

            print(f"✅ Found agent {target_agent_id} at URL: {agent_url}")

            # Ensure URL has /a2a endpoint
            if not agent_url.endswith('/a2a'):
                agent_url = f"{agent_url}/a2a"

            # Format message for external communication
            formatted_message = f"__EXTERNAL_MESSAGE__\n__FROM_AGENT__{self.agent_id}\n__TO_AGENT__{target_agent_id}\n__MESSAGE_START__\n{message_text}\n__MESSAGE_END__"

            print(f"📤 Sending to URL: {agent_url}")
            print(f"📋 Formatted message: {formatted_message[:100]}...")

            # Send message
            client = A2AClient(agent_url, timeout=30)
            print(f"🚀 Creating A2A client for {agent_url}")

            response = client.send_message(
                Message(
                    role=MessageRole.USER,
                    content=TextContent(text=formatted_message),
                    conversation_id=conversation_id,
                    metadata=Metadata(custom_fields={
                        'is_external': True,
                        'from_agent_id': self.agent_id,
                        'to_agent_id': target_agent_id
                    })
                )
            )

            print(f"✅ Message successfully sent to {target_agent_id}")
            print(f"📨 Response received: {response}")
            return f"Message sent to {target_agent_id}"

        except Exception as e:
            print(f"❌ Error sending message to {target_agent_id}: {str(e)}")
            return f"Error sending message to {target_agent_id}: {str(e)}"

    def _lookup_agent(self, agent_id: str) -> Optional[str]:
        """Look up agent URL in registry or use local testing lookup"""

        print(f"🔍 Looking up {agent_id}...")

        # Get public URL base from environment or detect local IP
        public_ip = os.getenv("PUBLIC_IP")
        if not public_ip:
            try:
                import socket
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                public_ip = s.getsockname()[0]
                s.close()
            except Exception:
                public_ip = "localhost"

        # Local testing lookup with dynamic IP support
        local_agents = {
            "sarcastic_agent": f"http://{public_ip}:6002",
            "helpful_agent": f"http://{public_ip}:6003"
        }

        print(f"💡 Using base IP: {public_ip} for local agent lookup")

        # Check local testing first
        if agent_id in local_agents:
            print(f"🏠 Found {agent_id} in local testing registry: {local_agents[agent_id]}")
            return local_agents[agent_id]

        # Try actual registry
        try:
            import requests
            print(f"🌐 Checking remote registry for {agent_id}...")
            response = requests.get(f"{self.registry_url}/lookup/{agent_id}")
            if response.status_code == 200:
                agent_url = response.json().get("agent_url")
                print(f"🌐 Found {agent_id} in remote registry: {agent_url}")
                return agent_url
            else:
                print(f"🌐 Agent {agent_id} not found in remote registry (status: {response.status_code})")
                return None
        except Exception as e:
            print(f"🌐 Registry lookup failed: {str(e)}")
            return None

    def _create_text_response(self, original_msg: Message, conversation_id: str, text: str) -> Message:
        """Create a text response message"""
        return Message(
            role=MessageRole.AGENT,
            content=TextContent(text=text),
            parent_message_id=original_msg.message_id,
            conversation_id=conversation_id
        )

    def _create_error_response(self, original_msg: Message, conversation_id: str, error: str) -> Message:
        """Create an error response message"""
        return Message(
            role=MessageRole.AGENT,
            content=ErrorContent(message=error),
            parent_message_id=original_msg.message_id,
            conversation_id=conversation_id
        )


class A2AClientExtended(A2AClient):
    """Extended A2A client with additional functionality"""

    def send_message_threaded(self, message: Message):
        """Send a message in a separate thread"""
        thread = threading.Thread(target=self.send_message, args=(message,))
        thread.daemon = True
        thread.start()
        return thread