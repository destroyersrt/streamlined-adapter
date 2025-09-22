#!/usr/bin/env python3
"""
Main Streamlined Adapter - Core integration point for all functionality
"""

import os
import signal
import sys
import threading
from typing import Optional, Dict, Any, List
from python_a2a import run_server
from .agent_bridge import StreamlinedAgentBridge
from .registry_client import RegistryClient
from .custom_agent_handler import CustomAgentHandler
from .agent_facts import AgentFactsGenerator, AgentFactsServer, AgentCapabilities
from ..discovery.agent_discovery import AgentDiscovery
from ..telemetry.telemetry_system import TelemetrySystem


class StreamlinedAdapter:
    """Main adapter class integrating all streamlined functionality"""

    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or os.getenv("AGENT_ID", "streamlined_agent")
        self.port = int(os.getenv("PORT", "6000"))
        self.registry_url = os.getenv("REGISTRY_URL") or self._get_registry_url()

        # Initialize core components
        self.telemetry = TelemetrySystem(self.agent_id)
        self.registry_client = RegistryClient(self.registry_url)
        self.discovery = AgentDiscovery(self.registry_client)
        self.custom_handler = CustomAgentHandler()
        self.bridge = StreamlinedAgentBridge(self.telemetry, self.custom_handler)

        # AgentFacts system
        self.agent_facts_generator = AgentFactsGenerator(self._get_base_url())
        self.agent_facts_server = None
        self.agent_capabilities = None

        # Runtime state
        self.running = False
        self.server_thread = None

        # Set up signal handlers
        self._setup_signal_handlers()

        print(f"🚀 Streamlined NANDA Adapter initialized for agent {self.agent_id}")

    def start_server(self, host: str = "0.0.0.0", register_with_registry: bool = True):
        """Start the adapter server"""
        try:
            # Register with registry if requested
            if register_with_registry:
                self._register_agent()

            print(f"📡 Starting agent bridge on {host}:{self.port}")
            self.running = True

            # Start telemetry
            self.telemetry.start()

            # Log startup
            self.telemetry.log_event("system", "adapter_started", {
                "agent_id": self.agent_id,
                "port": self.port,
                "host": host
            })

            # Run the server
            run_server(self.bridge, host=host, port=self.port)

        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
            self.stop()
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            self.telemetry.log_error(f"Server startup error: {str(e)}")
            raise

    def start_server_async(self, host: str = "0.0.0.0", register_with_registry: bool = True):
        """Start the adapter server in a separate thread"""
        if self.running:
            print("⚠️ Server is already running")
            return

        def server_worker():
            self.start_server(host, register_with_registry)

        self.server_thread = threading.Thread(target=server_worker, daemon=False)
        self.server_thread.start()
        print(f"🚀 Server started in background thread")

    def stop(self):
        """Stop the adapter and clean up resources"""
        if not self.running:
            return

        print("🔄 Stopping streamlined adapter...")
        self.running = False

        # Log shutdown
        self.telemetry.log_event("system", "adapter_stopped", {
            "agent_id": self.agent_id
        })

        # Stop telemetry
        self.telemetry.stop()

        # Unregister from registry
        self._unregister_agent()

        print("✅ Streamlined adapter stopped")

    def discover_agents(self, task_description: str, limit: int = 5) -> Dict[str, Any]:
        """Discover and rank agents for a specific task"""
        try:
            result = self.discovery.discover_agents(task_description, limit)

            # Log discovery operation
            self.telemetry.log_agent_discovery(
                task_description,
                len(result.recommended_agents),
                result.search_time_seconds
            )

            return {
                "task_analysis": {
                    "task_type": result.task_analysis.task_type,
                    "domain": result.task_analysis.domain,
                    "complexity": result.task_analysis.complexity,
                    "required_capabilities": result.task_analysis.required_capabilities,
                    "confidence": result.task_analysis.confidence
                },
                "recommended_agents": [
                    {
                        "agent_id": agent.agent_id,
                        "score": agent.score,
                        "confidence": agent.confidence,
                        "match_reasons": agent.match_reasons
                    }
                    for agent in result.recommended_agents
                ],
                "search_stats": {
                    "total_evaluated": result.total_agents_evaluated,
                    "search_time": result.search_time_seconds
                },
                "suggestions": result.suggestions
            }

        except Exception as e:
            self.telemetry.log_error(f"Agent discovery error: {str(e)}")
            return {"error": str(e)}

    def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent"""
        return self.registry_client.get_agent_metadata(agent_id)

    def list_available_agents(self) -> List[Dict[str, Any]]:
        """List all available agents in the registry"""
        return self.registry_client.list_agents()

    def search_agents(self, query: str = "", capabilities: List[str] = None,
                     domain: str = None) -> List[Dict[str, Any]]:
        """Search for agents with specific criteria"""
        return self.registry_client.search_agents(
            query=query,
            capabilities=capabilities
        )

    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        return self.telemetry.get_health_status()

    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics summary for the specified time window"""
        return self.telemetry.get_metrics_summary(hours)

    def export_telemetry(self, format: str = "json", hours: int = 24) -> str:
        """Export telemetry data"""
        return self.telemetry.export_metrics(format, hours)

    # Custom agent handler methods
    def set_message_handler(self, handler):
        """Set custom message handler for regular messages (no improvement, just custom responses)"""
        self.custom_handler.set_message_handler(handler)

    def set_query_handler(self, handler):
        """Set custom handler for /query commands"""
        self.custom_handler.set_query_handler(handler)

    def add_command_handler(self, command: str, handler):
        """Add custom handler for specific commands"""
        self.custom_handler.add_command_handler(command, handler)

    def enable_conversation_control(self, max_exchanges: int = None, stop_keywords: List[str] = None):
        """
        Enable conversation control for A2A communications

        Args:
            max_exchanges: Maximum exchanges per conversation (prevents infinite loops)
            stop_keywords: Keywords that end conversations (e.g., ['bye', 'stop', 'end'])

        Example:
            # Stop after 3 exchanges per conversation
            adapter.enable_conversation_control(max_exchanges=3)

            # Stop on specific keywords
            adapter.enable_conversation_control(stop_keywords=['bye', 'stop'])

            # Both limits
            adapter.enable_conversation_control(max_exchanges=5, stop_keywords=['bye'])
        """
        self.custom_handler.enable_conversation_control(max_exchanges, stop_keywords)

    def set_agent_capabilities(self, capabilities: AgentCapabilities, description: str = "", tags: List[str] = None):
        """
        Set agent capabilities for AgentFacts registration

        Args:
            capabilities: AgentCapabilities object defining what this agent can do
            description: Human-readable description of the agent
            tags: List of tags for filtering (e.g., ["expert", "finance"])
        """
        self.agent_capabilities = capabilities
        self.agent_description = description
        self.agent_tags = tags or []
        print(f"📋 Agent capabilities set for {self.agent_id}")

    def start_agent_facts_server(self, facts_port: int = None):
        """Start AgentFacts server for this agent"""
        if not facts_port:
            facts_port = self.port + 1000  # Offset for AgentFacts server

        try:
            self.agent_facts_server = AgentFactsServer(facts_port)

            # Generate and register AgentFacts if capabilities are set
            if self.agent_capabilities:
                agent_facts = self.agent_facts_generator.create_agent_facts(
                    agent_id=self.agent_id,
                    port=self.port,
                    capabilities=self.agent_capabilities,
                    description=getattr(self, 'agent_description', ''),
                    tags=getattr(self, 'agent_tags', [])
                )

                self.agent_facts_server.register_agent_facts(self.agent_id, agent_facts)

            self.agent_facts_server.start_server()
            print(f"📡 AgentFacts server started on port {facts_port}")
            return self.agent_facts_server.get_agent_facts_url(self.agent_id)

        except Exception as e:
            print(f"⚠️ AgentFacts server failed to start: {e}")
            print("   Agent will register without AgentFacts URL")
            self.agent_facts_server = None
            return None

    def get_agent_facts_url(self) -> Optional[str]:
        """Get the AgentFacts URL for this agent"""
        if self.agent_facts_server:
            return self.agent_facts_server.get_agent_facts_url(self.agent_id)
        return None

    def _get_registry_url(self) -> str:
        """Get registry URL from configuration"""
        try:
            if os.path.exists("registry_url.txt"):
                with open("registry_url.txt", "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        return "https://chat.nanda-registry.com:6900"

    def _get_base_url(self) -> str:
        """Get base URL for this agent"""
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
        return f"http://{public_ip}"

    def _register_agent(self) -> bool:
        """Register this agent with the registry"""
        public_url = os.getenv("PUBLIC_URL")
        api_url = os.getenv("API_URL")

        if not public_url:
            print("⚠️ PUBLIC_URL not set - agent will not be registered")
            return False

        try:
            # Get AgentFacts URL if available
            agent_facts_url = None
            if self.agent_facts_server:
                agent_facts_url = self.get_agent_facts_url()

            success = self.registry_client.register_agent(
                self.agent_id, public_url, api_url, agent_facts_url
            )

            if success:
                print(f"✅ Agent {self.agent_id} registered with registry")
                if agent_facts_url:
                    print(f"📋 AgentFacts URL: {agent_facts_url}")
                self.telemetry.log_registry_interaction("register", True)
            else:
                print(f"❌ Failed to register agent {self.agent_id}")
                self.telemetry.log_registry_interaction("register", False)
            return success
        except Exception as e:
            print(f"❌ Registration error: {e}")
            self.telemetry.log_error(f"Registration error: {str(e)}")
            return False

    def _unregister_agent(self):
        """Unregister this agent from the registry"""
        try:
            self.registry_client.unregister_agent(self.agent_id)
            print(f"📤 Agent {self.agent_id} unregistered from registry")
        except Exception as e:
            print(f"⚠️ Error unregistering agent: {e}")

    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# CLI functions for backward compatibility
def create_adapter(agent_id: Optional[str] = None) -> StreamlinedAdapter:
    """Create a new streamlined adapter instance"""
    return StreamlinedAdapter(agent_id)


def start_adapter_server(adapter: StreamlinedAdapter, host: str = "0.0.0.0"):
    """Start the adapter server (blocking)"""
    adapter.start_server(host)


def main():
    """Main CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Streamlined NANDA Adapter")
    parser.add_argument("--agent-id", help="Agent ID")
    parser.add_argument("--port", type=int, default=6000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--no-register", action="store_true", help="Don't register with registry")

    args = parser.parse_args()

    # Set environment variables
    if args.agent_id:
        os.environ["AGENT_ID"] = args.agent_id
    os.environ["PORT"] = str(args.port)

    # Create and start adapter
    adapter = StreamlinedAdapter(args.agent_id)

    print(f"""
🚀 Streamlined NANDA Adapter
==============================
Agent ID: {adapter.agent_id}
Port: {adapter.port}
Registry: {adapter.registry_url}
==============================
    """)

    adapter.start_server(args.host, not args.no_register)


if __name__ == "__main__":
    main()