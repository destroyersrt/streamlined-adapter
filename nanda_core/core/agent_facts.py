#!/usr/bin/env python3
"""
AgentFacts Generator and Server for NANDA Project
Implements the AgentFacts specification for agent capability description
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import threading

try:
    from flask import Flask, jsonify, send_from_directory
    FLASK_AVAILABLE = True
except ImportError:
    print("⚠️ Flask not available - AgentFacts server will be disabled")
    FLASK_AVAILABLE = False
    Flask = None


@dataclass
class AgentCapabilities:
    """Agent capabilities structure"""
    modalities: List[str]  # ["text", "image", "audio"]
    skills: List[str]      # ["financial_analysis", "data_visualization"]
    domains: List[str]     # ["finance", "healthcare", "marketing"]
    languages: List[str]   # ["english", "spanish"]
    streaming: bool = False
    batch: bool = True
    reasoning: bool = True
    memory: bool = False


@dataclass
class AgentEndpoints:
    """Agent endpoints structure"""
    static: str           # Primary A2A endpoint
    api: Optional[str] = None      # REST API endpoint
    websocket: Optional[str] = None # WebSocket endpoint


@dataclass
class AgentCertification:
    """Agent certification information"""
    level: str = "verified"        # verified, beta, experimental
    issued_by: str = "NANDA"
    issued_date: str = None
    expires_date: str = None

    def __post_init__(self):
        if not self.issued_date:
            self.issued_date = datetime.now().isoformat()
        if not self.expires_date:
            # Default 30-day expiration
            expires = datetime.now() + timedelta(days=30)
            self.expires_date = expires.isoformat()


@dataclass
class AgentFacts:
    """Complete AgentFacts specification"""
    context: str = "https://projectnanda.org/agentfacts/v1"
    id: str = None
    handle: str = None
    provider: str = "streamlined_adapter"
    jurisdiction: str = "USA"
    version: str = "1.0"
    certification: AgentCertification = None
    capabilities: AgentCapabilities = None
    endpoints: AgentEndpoints = None
    description: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if not self.certification:
            self.certification = AgentCertification()
        if not self.tags:
            self.tags = []


class AgentFactsGenerator:
    """Generate AgentFacts JSON for agents"""

    def __init__(self, base_url: str = None):
        self.base_url = base_url or "http://localhost"

    def create_agent_facts(self,
                          agent_id: str,
                          port: int,
                          capabilities: AgentCapabilities,
                          description: str = "",
                          tags: List[str] = None) -> AgentFacts:
        """Create AgentFacts for an agent"""

        endpoints = AgentEndpoints(
            static=f"{self.base_url}:{port}",
            api=f"{self.base_url}:{port + 100}"  # API port offset
        )

        agent_facts = AgentFacts(
            id=f"did:nanda:agent:{agent_id}",
            handle=f"@{agent_id}",
            capabilities=capabilities,
            endpoints=endpoints,
            description=description,
            tags=tags or []
        )

        return agent_facts

    def to_json(self, agent_facts: AgentFacts) -> Dict[str, Any]:
        """Convert AgentFacts to JSON-serializable dict"""
        result = {
            "@context": agent_facts.context,
            "id": agent_facts.id,
            "handle": agent_facts.handle,
            "provider": agent_facts.provider,
            "jurisdiction": agent_facts.jurisdiction,
            "version": agent_facts.version,
            "certification": asdict(agent_facts.certification),
            "capabilities": asdict(agent_facts.capabilities),
            "endpoints": asdict(agent_facts.endpoints)
        }

        if agent_facts.description:
            result["description"] = agent_facts.description

        if agent_facts.tags:
            result["tags"] = agent_facts.tags

        return result


class AgentFactsServer:
    """HTTP server for serving AgentFacts JSON files"""

    def __init__(self, port: int = 8080):
        self.port = port
        self.agent_facts = {}  # agent_id -> AgentFacts
        self.server_thread = None

        if not FLASK_AVAILABLE:
            print(f"⚠️ Flask not available - AgentFacts server on port {port} disabled")
            self.app = None
            return

        self.app = Flask(__name__)
        self.setup_routes()

    def setup_routes(self):
        """Setup Flask routes for AgentFacts"""

        @self.app.route('/@<agent_id>.json')
        def get_agent_facts(agent_id):
            """Serve AgentFacts JSON for specific agent"""
            if agent_id in self.agent_facts:
                generator = AgentFactsGenerator()
                facts_json = generator.to_json(self.agent_facts[agent_id])
                return jsonify(facts_json)
            else:
                return {"error": f"Agent {agent_id} not found"}, 404

        @self.app.route('/agents')
        def list_agents():
            """List all available agents"""
            return jsonify({
                "agents": list(self.agent_facts.keys()),
                "count": len(self.agent_facts)
            })

        @self.app.route('/health')
        def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "agents": len(self.agent_facts)}

    def register_agent_facts(self, agent_id: str, agent_facts: AgentFacts):
        """Register AgentFacts for an agent"""
        self.agent_facts[agent_id] = agent_facts
        print(f"📋 Registered AgentFacts for {agent_id}")

    def get_agent_facts_url(self, agent_id: str) -> str:
        """Get the AgentFacts URL for an agent"""
        return f"http://localhost:{self.port}/@{agent_id}.json"

    def start_server(self):
        """Start the AgentFacts server in background"""
        if not FLASK_AVAILABLE or not self.app:
            print(f"⚠️ Cannot start AgentFacts server - Flask not available")
            return

        def run_server():
            self.app.run(host='0.0.0.0', port=self.port, debug=False)

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        print(f"📡 AgentFacts server started on port {self.port}")

    def stop_server(self):
        """Stop the AgentFacts server"""
        # Flask doesn't have a built-in stop method, so we use daemon threads
        print(f"🛑 AgentFacts server stopping...")


# Predefined capability templates for common agent types
class CapabilityTemplates:
    """Common capability templates for different agent types"""

    @staticmethod
    def data_scientist(level: str = "senior") -> AgentCapabilities:
        """Data scientist capabilities"""
        skills = ["data_analysis", "statistical_modeling", "data_visualization"]
        if level == "senior":
            skills.extend(["machine_learning", "deep_learning", "feature_engineering"])
        elif level == "ml_specialist":
            skills.extend(["machine_learning", "deep_learning", "neural_networks", "model_optimization"])

        return AgentCapabilities(
            modalities=["text"],
            skills=skills,
            domains=["data_science", "analytics"],
            languages=["english"],
            batch=True,
            reasoning=True
        )

    @staticmethod
    def financial_analyst(specialty: str = "general") -> AgentCapabilities:
        """Financial analyst capabilities"""
        skills = ["financial_analysis", "market_research", "financial_modeling"]
        domains = ["finance", "economics"]

        if specialty == "risk":
            skills.extend(["risk_assessment", "portfolio_analysis", "stress_testing"])
            domains.append("risk_management")
        elif specialty == "investment":
            skills.extend(["investment_analysis", "valuation", "portfolio_optimization"])
            domains.append("investments")

        return AgentCapabilities(
            modalities=["text"],
            skills=skills,
            domains=domains,
            languages=["english"],
            batch=True,
            reasoning=True
        )

    @staticmethod
    def healthcare_expert(specialty: str = "general") -> AgentCapabilities:
        """Healthcare expert capabilities"""
        skills = ["medical_knowledge", "symptom_analysis", "treatment_planning"]
        domains = ["healthcare", "medicine"]

        if specialty == "diagnosis":
            skills.extend(["diagnostic_reasoning", "differential_diagnosis", "clinical_assessment"])
            domains.append("diagnostics")
        elif specialty == "treatment":
            skills.extend(["treatment_protocols", "medication_management", "care_planning"])
            domains.append("therapeutics")

        return AgentCapabilities(
            modalities=["text"],
            skills=skills,
            domains=domains,
            languages=["english"],
            batch=True,
            reasoning=True,
            memory=True  # Medical agents often need patient history
        )

    @staticmethod
    def marketing_specialist(focus: str = "strategy") -> AgentCapabilities:
        """Marketing specialist capabilities"""
        skills = ["market_analysis", "customer_segmentation", "campaign_planning"]
        domains = ["marketing", "business"]

        if focus == "content":
            skills.extend(["content_creation", "copywriting", "brand_messaging"])
            domains.append("content_marketing")
        elif focus == "digital":
            skills.extend(["digital_marketing", "social_media", "seo_optimization"])
            domains.append("digital_marketing")

        return AgentCapabilities(
            modalities=["text"],
            skills=skills,
            domains=domains,
            languages=["english"],
            batch=True,
            reasoning=True
        )

    @staticmethod
    def general_assistant() -> AgentCapabilities:
        """General assistant capabilities"""
        return AgentCapabilities(
            modalities=["text"],
            skills=["general_assistance", "task_coordination", "information_retrieval"],
            domains=["general", "productivity"],
            languages=["english"],
            batch=True,
            reasoning=True,
            memory=True
        )


# Example usage
def create_sample_agent_facts():
    """Create sample AgentFacts for testing"""
    generator = AgentFactsGenerator("http://10.189.72.201")

    # Senior Data Scientist
    senior_ds_facts = generator.create_agent_facts(
        agent_id="senior_data_scientist",
        port=7001,
        capabilities=CapabilityTemplates.data_scientist("senior"),
        description="Senior data scientist with 10+ years experience in machine learning and statistical analysis",
        tags=["expert", "senior", "python", "sql", "machine_learning"]
    )

    # Financial Risk Analyst
    risk_analyst_facts = generator.create_agent_facts(
        agent_id="risk_analyst",
        port=7005,
        capabilities=CapabilityTemplates.financial_analyst("risk"),
        description="Financial risk analyst specializing in portfolio risk assessment and stress testing",
        tags=["finance", "risk", "portfolio", "quantitative"]
    )

    return {
        "senior_data_scientist": senior_ds_facts,
        "risk_analyst": risk_analyst_facts
    }


if __name__ == "__main__":
    # Test the AgentFacts system
    facts_server = AgentFactsServer(8080)

    # Create sample facts
    sample_facts = create_sample_agent_facts()

    # Register with server
    for agent_id, facts in sample_facts.items():
        facts_server.register_agent_facts(agent_id, facts)

    # Start server
    facts_server.start_server()

    print("🧪 Testing AgentFacts URLs:")
    for agent_id in sample_facts.keys():
        url = facts_server.get_agent_facts_url(agent_id)
        print(f"  {agent_id}: {url}")

    print("\n📡 AgentFacts server running. Test with:")
    print("  curl http://localhost:8080/@senior_data_scientist.json")
    print("  curl http://localhost:8080/agents")

    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping AgentFacts server")