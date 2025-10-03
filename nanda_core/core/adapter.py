#!/usr/bin/env python3
"""
Simple NANDA Adapter - Clean Agent-to-Agent Communication

Simple, clean adapter focused on A2A communication without complexity.
8-10 lines to deploy an agent.
"""

import os
import requests
from typing import Optional, Callable
from python_a2a import run_server
from .agent_bridge import SimpleAgentBridge


class NANDA:
    """Simple NANDA class for clean agent deployment"""
    
    def __init__(self, 
                 agent_id: str,
                 agent_logic: Callable[[str, str], str],
                 port: int = 6000,
                 registry_url: Optional[str] = None,
                 public_url: Optional[str] = None,
                 host: str = "0.0.0.0",
                 enable_telemetry: bool = True):
        """
        Create a simple NANDA agent
        
        Args:
            agent_id: Unique agent identifier
            agent_logic: Function that takes (message: str, conversation_id: str) -> response: str
            port: Port to run on
            registry_url: Optional registry URL for agent discovery
            public_url: Public URL for agent registration (e.g., https://yourdomain.com:6000)
            host: Host to bind to
            enable_telemetry: Enable telemetry logging (optional)
        """
        self.agent_id = agent_id
        self.agent_logic = agent_logic
        self.port = port
        self.registry_url = registry_url
        self.public_url = public_url
        self.host = host
        self.enable_telemetry = enable_telemetry
        
        # Initialize telemetry if enabled
        self.telemetry = None
        if enable_telemetry:
            try:
                from ..telemetry.telemetry_system import TelemetrySystem
                self.telemetry = TelemetrySystem(agent_id)
                print(f"📊 Telemetry enabled for {agent_id}")
            except ImportError:
                print(f"⚠️ Telemetry requested but module not available")
        
        # Create the bridge with optional features
        self.bridge = SimpleAgentBridge(
            agent_id=agent_id,
            agent_logic=agent_logic,
            registry_url=registry_url,
            telemetry=self.telemetry,
            url=public_url  # Pass the public URL for A2A configuration
        )
        
        print(f"🤖 NANDA Agent '{agent_id}' created")
        if registry_url:
            print(f"🌐 Registry: {registry_url}")
        if public_url:
            print(f"🔗 Public URL: {public_url}")
    
    def start(self, register: bool = True):
        """Start the agent server"""
        # Register with registry if provided
        if register and self.registry_url and self.public_url:
            self._register()
        
        print(f"🚀 Starting agent '{self.agent_id}' on {self.host}:{self.port}")
        
        # Start the A2A server
        run_server(self.bridge, host=self.host, port=self.port)
    
    def _register(self):
        """Register agent with registry"""
        try:
            data = {
                "agent_id": self.agent_id,
                "agent_url": self.public_url
            }
            
            # Include metadata if available
            if hasattr(self, 'metadata') and self.metadata:
                # Add metadata fields that the registry expects
                if 'description' in self.metadata:
                    data['description'] = self.metadata['description']
                if 'domain' in self.metadata:
                    data['domain'] = self.metadata['domain']
                if 'specialization' in self.metadata:
                    data['specialization'] = self.metadata['specialization']
                if 'structure_type' in self.metadata:
                    data['structure_type'] = self.metadata['structure_type']
                if 'capabilities' in self.metadata:
                    data['capabilities'] = self.metadata['capabilities'].get('technical_skills', [])                                                                                                  
                if 'tags' in self.metadata:
                    data['tags'] = self.metadata['tags']
                    
            response = requests.post(f"{self.registry_url}/register", json=data, timeout=10)
            if response.status_code == 200:
                print(f"✅ Agent '{self.agent_id}' registered successfully with metadata")
            else:
                print(f"⚠️ Failed to register agent: HTTP {response.status_code} - {response.text}")
        except Exception as e:
            print(f"⚠️ Registration error: {e}")

    def stop(self):
        """Stop the agent (placeholder for cleanup)"""
        print(f"🛑 Stopping agent '{self.agent_id}'")


# Keep the StreamlinedAdapter class name for compatibility but simplified
class StreamlinedAdapter(NANDA):
    """Alias for NANDA class for compatibility"""
    pass


# Example agent logic functions
def echo_agent(message: str, conversation_id: str) -> str:
    """Simple echo agent"""
    return f"Echo: {message}"


def pirate_agent(message: str, conversation_id: str) -> str:
    """Pirate-style agent"""
    return f"Arrr! {message}, matey!"


def helpful_agent(message: str, conversation_id: str) -> str:
    """Helpful agent"""
    if "time" in message.lower():
        from datetime import datetime
        return f"Current time: {datetime.now().strftime('%H:%M:%S')}"
    elif "help" in message.lower():
        return "I can help with time, calculations, and general questions!"
    elif any(op in message for op in ['+', '-', '*', '/']):
        try:
            result = eval(message.replace('x', '*').replace('X', '*'))
            return f"Result: {result}"
        except:
            return "Invalid calculation"
    else:
        return f"I can help with: {message}"


def main():
    """Main CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Simple NANDA Agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--port", type=int, default=6000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--registry", help="Registry URL")
    parser.add_argument("--public-url", help="Public URL for registration")
    parser.add_argument("--no-register", action="store_true", help="Don't register with registry")
    
    args = parser.parse_args()
    
    # Use helpful agent as default
    nanda = NANDA(
        agent_id=args.agent_id,
        agent_logic=helpful_agent,
        port=args.port,
        registry_url=args.registry,
        public_url=args.public_url,
        host=args.host
    )
    
    try:
        nanda.start(register=not args.no_register)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        nanda.stop()


if __name__ == "__main__":
    main()