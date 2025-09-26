#!/usr/bin/env python3
"""
Simple Agent Bridge for A2A Communication

Clean, simple bridge focused on agent-to-agent communication.
"""

import os
import uuid
import logging
import requests
from typing import Callable, Optional, Dict, Any
from python_a2a import A2AServer, A2AClient, Message, TextContent, MessageRole, Metadata

# Configure logger to capture conversation logs
logger = logging.getLogger(__name__)


class SimpleAgentBridge(A2AServer):
    """Simple Agent Bridge for A2A communication only"""
    
    def __init__(self, 
                 agent_id: str, 
                 agent_logic: Callable[[str, str], str],
                 registry_url: Optional[str] = None,
                 telemetry = None):
        super().__init__()
        self.agent_id = agent_id
        self.agent_logic = agent_logic
        self.registry_url = registry_url
        self.telemetry = telemetry
        
    def handle_message(self, msg: Message) -> Message:
        """Handle incoming messages"""
        conversation_id = msg.conversation_id or str(uuid.uuid4())
        
        # Only handle text content
        if not isinstance(msg.content, TextContent):
            return self._create_response(
                msg, conversation_id, 
                "Only text messages supported"
            )
        
        user_text = msg.content.text
        
        # Check if this is an agent-to-agent message in our simple format
        if user_text.startswith("FROM:") and "TO:" in user_text and "MESSAGE:" in user_text:
            return self._handle_incoming_agent_message(user_text, msg, conversation_id)
        
        logger.info(f"📨 [{self.agent_id}] Received: {user_text}")
        
        # Handle different message types
        try:
            if user_text.startswith("@"):
                # Agent-to-agent message (outgoing)
                return self._handle_agent_message(user_text, msg, conversation_id)
            elif user_text.startswith("/"):
                # System command
                return self._handle_command(user_text, msg, conversation_id)
            else:
                # Regular message - use agent logic
                if self.telemetry:
                    self.telemetry.log_message_received(self.agent_id, conversation_id)
                
                response = self.agent_logic(user_text, conversation_id)
                return self._create_response(msg, conversation_id, response)
                
        except Exception as e:
            return self._create_response(
                msg, conversation_id, 
                f"Error: {str(e)}"
            )
    
    def _handle_incoming_agent_message(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle incoming messages from other agents"""
        try:
            lines = user_text.strip().split('\n')
            from_agent = ""
            to_agent = ""
            message_content = ""
            
            for line in lines:
                if line.startswith("FROM:"):
                    from_agent = line[5:].strip()
                elif line.startswith("TO:"):
                    to_agent = line[3:].strip()
                elif line.startswith("MESSAGE:"):
                    message_content = line[8:].strip()
            
            logger.info(f"📨 [{self.agent_id}] ← [{from_agent}]: {message_content}")
            
            # Check if this is a reply (don't respond to replies to avoid infinite loops)
            if message_content.startswith("Response to "):
                logger.info(f"🔄 [{self.agent_id}] Received reply from {from_agent}, displaying to user")
                # Display the reply to user but don't respond back to avoid loops
                return self._create_response(
                    msg, conversation_id, 
                    f"[{from_agent}] {message_content[len('Response to ' + self.agent_id + ': '):]}"
                )
            
            # Process the message through our agent logic
            if self.telemetry:
                self.telemetry.log_message_received(self.agent_id, conversation_id)
            
            response = self.agent_logic(message_content, conversation_id)
            
            # Send response back
            return self._create_response(
                msg, conversation_id, 
                f"Response to {from_agent}: {response}"
            )
            
        except Exception as e:
            logger.error(f"❌ [{self.agent_id}] Error processing incoming agent message: {e}")
            return self._create_response(
                msg, conversation_id,
                f"Error processing message from agent: {str(e)}"
            )

    def _handle_agent_message(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle messages to other agents (@agent_id message)"""
        parts = user_text.split(" ", 1)
        if len(parts) <= 1:
            return self._create_response(
                msg, conversation_id,
                "Invalid format. Use '@agent_id message'"
            )
        
        target_agent = parts[0][1:]  # Remove @
        message_text = parts[1]
        
        logger.info(f"🔄 [{self.agent_id}] Sending to {target_agent}: {message_text}")
        
        # Look up target agent and send message
        result = self._send_to_agent(target_agent, message_text, conversation_id)
        return self._create_response(msg, conversation_id, result)
    
    def _handle_command(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle system commands"""
        parts = user_text.split(" ", 1)
        command = parts[0][1:] if len(parts) > 0 else ""
        args = parts[1] if len(parts) > 1 else ""
        
        if command == "help":
            help_text = """Available commands:
/help - Show this help
/ping - Test agent responsiveness  
/status - Show agent status
@agent_id message - Send message to another agent"""
            return self._create_response(msg, conversation_id, help_text)
        
        elif command == "ping":
            return self._create_response(msg, conversation_id, "Pong!")
        
        elif command == "status":
            status = f"Agent: {self.agent_id}, Status: Running"
            if self.registry_url:
                status += f", Registry: {self.registry_url}"
            return self._create_response(msg, conversation_id, status)
        
        else:
            return self._create_response(
                msg, conversation_id,
                f"Unknown command: {command}. Use /help for available commands"
            )
    
    def _send_to_agent(self, target_agent_id: str, message_text: str, conversation_id: str) -> str:
        """Send message to another agent"""
        try:
            # Look up agent URL
            agent_url = self._lookup_agent(target_agent_id)
            if not agent_url:
                return f"Agent {target_agent_id} not found"
            
            # Ensure URL has /a2a endpoint
            if not agent_url.endswith('/a2a'):
                agent_url = f"{agent_url}/a2a"
            
            logger.info(f"📤 [{self.agent_id}] → [{target_agent_id}]: {message_text}")
            
            # Create simple message with metadata
            simple_message = f"FROM: {self.agent_id}\nTO: {target_agent_id}\nMESSAGE: {message_text}"
            
            # Send message using A2A client
            client = A2AClient(agent_url, timeout=30)
            response = client.send_message(
                Message(
                    role=MessageRole.USER,
                    content=TextContent(text=simple_message),
                    conversation_id=conversation_id,
                    metadata=Metadata(custom_fields={
                        'from_agent_id': self.agent_id,
                        'to_agent_id': target_agent_id,
                        'message_type': 'agent_to_agent'
                    })
                )
            )
            
            if self.telemetry:
                self.telemetry.log_agent_message_sent(self.agent_id, target_agent_id, conversation_id)
            
            logger.info(f"✅ [{self.agent_id}] Message delivered to {target_agent_id}")
            return f"Message sent to {target_agent_id}: {message_text}"
            
        except Exception as e:
            return f"❌ Error sending to {target_agent_id}: {str(e)}"
    
    def _lookup_agent(self, agent_id: str) -> Optional[str]:
        """Look up agent URL in registry or use local discovery"""
        
        # Try registry lookup if available
        if self.registry_url:
            try:
                response = requests.get(f"{self.registry_url}/lookup/{agent_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    agent_url = data.get("agent_url")
                    logger.info(f"🌐 Found {agent_id} in registry: {agent_url}")
                    return agent_url
            except Exception as e:
                logger.warning(f"🌐 Registry lookup failed: {e}")
        
        # Fallback to local discovery (for testing)
        local_agents = {
            "test_agent": "http://localhost:6000",
            "pirate_agent": "http://localhost:6001", 
            "helpful_agent": "http://localhost:6002",
            "echo_agent": "http://localhost:6003",
            "simple_test_agent": "http://localhost:6005",
            "agent_alpha": "http://localhost:6010",
            "agent_beta": "http://localhost:6011"
        }
        
        if agent_id in local_agents:
            logger.info(f"🏠 Found {agent_id} locally: {local_agents[agent_id]}")
            return local_agents[agent_id]
        
        return None
    
    def _create_response(self, original_msg: Message, conversation_id: str, text: str) -> Message:
        """Create a response message"""
        return Message(
            role=MessageRole.AGENT,
            content=TextContent(text=f"[{self.agent_id}] {text}"),
            parent_message_id=original_msg.message_id,
            conversation_id=conversation_id
        )