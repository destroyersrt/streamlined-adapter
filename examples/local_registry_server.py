#!/usr/bin/env python3
"""
Local NANDA Registry Server for Testing
Supports agent registration with AgentFacts URLs and capability-based discovery
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import requests

try:
    from flask import Flask, request, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    print("❌ Flask required for registry server")
    print("Install with: pip install flask")
    exit(1)

@dataclass
class RegisteredAgent:
    """Registered agent information"""
    agent_id: str
    agent_url: str
    api_url: Optional[str] = None
    agent_facts_url: Optional[str] = None
    registered_at: str = None
    last_seen: str = None
    status: str = "active"
    capabilities: List[str] = None
    domain: str = None

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now().isoformat()
        if not self.last_seen:
            self.last_seen = datetime.now().isoformat()
        if self.capabilities is None:
            self.capabilities = []

class LocalRegistry:
    """Simple local registry for testing AgentFacts integration"""

    def __init__(self, port: int = 6900):
        self.port = port
        self.app = Flask(__name__)
        self.agents: Dict[str, RegisteredAgent] = {}
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes for registry API"""

        @self.app.route('/register', methods=['POST'])
        def register_agent():
            """Register an agent with the registry"""
            try:
                data = request.get_json()
                agent_id = data.get('agent_id')
                agent_url = data.get('agent_url')
                api_url = data.get('api_url')
                agent_facts_url = data.get('agent_facts_url')

                if not agent_id or not agent_url:
                    return {"error": "agent_id and agent_url required"}, 400

                # Create registered agent
                agent = RegisteredAgent(
                    agent_id=agent_id,
                    agent_url=agent_url,
                    api_url=api_url,
                    agent_facts_url=agent_facts_url
                )

                # Fetch capabilities from AgentFacts if available
                if agent_facts_url:
                    try:
                        capabilities, domain = self._fetch_agent_capabilities(agent_facts_url)
                        agent.capabilities = capabilities
                        agent.domain = domain
                        print(f"📋 Fetched capabilities for {agent_id}: {capabilities}")
                    except Exception as e:
                        print(f"⚠️ Could not fetch AgentFacts for {agent_id}: {e}")

                # Store agent
                self.agents[agent_id] = agent

                print(f"✅ Registered agent: {agent_id}")
                print(f"   URL: {agent_url}")
                print(f"   AgentFacts: {agent_facts_url}")
                print(f"   Capabilities: {agent.capabilities}")
                print(f"   Domain: {agent.domain}")

                return {"message": f"Agent {agent_id} registered successfully"}, 200

            except Exception as e:
                print(f"❌ Registration error: {e}")
                return {"error": str(e)}, 500

        @self.app.route('/lookup/<agent_id>', methods=['GET'])
        def lookup_agent(agent_id):
            """Look up an agent by ID"""
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                agent.last_seen = datetime.now().isoformat()
                return asdict(agent), 200
            else:
                return {"error": f"Agent {agent_id} not found"}, 404

        @self.app.route('/agents', methods=['GET'])
        @self.app.route('/list', methods=['GET'])
        def list_agents():
            """List all registered agents"""
            agents_list = [asdict(agent) for agent in self.agents.values()]
            return {"agents": agents_list, "count": len(agents_list)}, 200

        @self.app.route('/search', methods=['GET'])
        def search_agents():
            """Search agents by capabilities, domain, or query"""
            query = request.args.get('q', '').lower()
            capabilities = request.args.get('capabilities', '').split(',') if request.args.get('capabilities') else []
            domain = request.args.get('domain', '').lower()

            results = []
            for agent in self.agents.values():
                # Domain filtering
                if domain and agent.domain and domain not in agent.domain.lower():
                    continue

                # Capability filtering
                if capabilities and capabilities != ['']:
                    agent_caps = [cap.lower() for cap in agent.capabilities]
                    if not any(cap.lower() in agent_caps for cap in capabilities):
                        continue

                # Query filtering (search in agent_id, domain, capabilities)
                if query:
                    searchable_text = f"{agent.agent_id} {agent.domain} {' '.join(agent.capabilities)}".lower()
                    if query not in searchable_text:
                        continue

                results.append(asdict(agent))

            print(f"🔍 Search query: '{query}', capabilities: {capabilities}, domain: '{domain}'")
            print(f"   Found {len(results)} agents")

            return {"agents": results, "count": len(results)}, 200

        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "agents_registered": len(self.agents),
                "uptime": "local_registry"
            }, 200

        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Registry statistics"""
            return {
                "total_agents": len(self.agents),
                "active_agents": len([a for a in self.agents.values() if a.status == "active"]),
                "domains": list(set(a.domain for a in self.agents.values() if a.domain)),
                "capabilities": list(set(cap for a in self.agents.values() for cap in a.capabilities))
            }, 200

        @self.app.route('/', methods=['GET'])
        def root():
            """Registry information"""
            return {
                "service": "Local NANDA Registry",
                "version": "1.0.0-local",
                "agents": len(self.agents),
                "endpoints": {
                    "register": "/register",
                    "lookup": "/lookup/<agent_id>",
                    "list": "/list",
                    "search": "/search",
                    "health": "/health"
                }
            }, 200

    def _fetch_agent_capabilities(self, agent_facts_url: str) -> tuple[List[str], str]:
        """Fetch agent capabilities from AgentFacts URL"""
        try:
            response = requests.get(agent_facts_url, timeout=5)
            if response.status_code == 200:
                facts = response.json()
                capabilities_obj = facts.get('capabilities', {})
                skills = capabilities_obj.get('skills', [])
                domains = capabilities_obj.get('domains', [])
                domain = domains[0] if domains else "general"
                return skills, domain
            else:
                return [], "unknown"
        except Exception as e:
            print(f"⚠️ Error fetching AgentFacts: {e}")
            return [], "unknown"

    def start_server(self):
        """Start the registry server"""
        print(f"""
🏛️ Local NANDA Registry Server Starting...
==========================================
Port: {self.port}
Registry URL: http://localhost:{self.port}
==========================================

Endpoints:
📝 POST /register - Register agents
🔍 GET /lookup/<agent_id> - Look up agent
📋 GET /list - List all agents
🔎 GET /search?q=<query>&capabilities=<caps>&domain=<domain>
❤️ GET /health - Health check

AgentFacts Integration:
✅ Fetches capabilities from agent_facts_url
✅ Enables capability-based discovery
✅ Supports domain filtering
        """)

        try:
            self.app.run(host='0.0.0.0', port=self.port, debug=False)
        except KeyboardInterrupt:
            print("\n🛑 Local NANDA Registry stopped")

def main():
    """Start the local registry server"""
    import argparse

    parser = argparse.ArgumentParser(description="Local NANDA Registry Server")
    parser.add_argument("--port", type=int, default=6900, help="Registry port (default: 6900)")
    args = parser.parse_args()

    registry = LocalRegistry(args.port)
    registry.start_server()

if __name__ == "__main__":
    main()