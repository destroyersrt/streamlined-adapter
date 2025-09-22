#!/usr/bin/env python3
"""
Expert Agent Sandbox Orchestrator
Manages 5-10 field expert agents, demonstrates registry-based discovery and A2A communication
"""

import os
import sys
import time
import threading
import subprocess
import socket
from typing import Dict, List, Any
import requests

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates, AgentFactsServer

class ExpertSandbox:
    """Orchestrates multiple expert agents for demonstration"""

    def __init__(self):
        self.base_ip = self._get_local_ip()
        self.expert_agents = self._define_expert_agents()
        self.agent_processes = {}
        self.coordinator_agent = None
        self.facts_server = None
        self.running = False

    def _get_local_ip(self) -> str:
        """Get local IP address"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            return "localhost"

    def _define_expert_agents(self) -> List[Dict[str, Any]]:
        """Define the expert agents to be created"""
        return [
            {
                "script": "expert_agents/senior_data_scientist_agent.py",
                "agent_id": "senior_data_scientist",
                "port": 7001,
                "domain": "data_science",
                "capabilities": ["machine_learning", "data_analysis", "statistical_modeling"]
            },
            {
                "script": "expert_agents/junior_data_scientist_agent.py",
                "agent_id": "junior_data_scientist",
                "port": 7002,
                "domain": "data_science",
                "capabilities": ["data_analysis", "data_visualization", "basic_ml"]
            },
            {
                "script": "expert_agents/financial_analyst_agent.py",
                "agent_id": "financial_analyst",
                "port": 7004,
                "domain": "finance",
                "capabilities": ["financial_analysis", "market_research", "risk_assessment"]
            },
            {
                "script": "expert_agents/risk_analyst_agent.py",
                "agent_id": "risk_analyst",
                "port": 7005,
                "domain": "finance",
                "capabilities": ["risk_assessment", "portfolio_analysis", "stress_testing"]
            },
            {
                "script": "expert_agents/marketing_strategist_agent.py",
                "agent_id": "marketing_strategist",
                "port": 7008,
                "domain": "marketing",
                "capabilities": ["marketing_strategy", "campaign_planning", "brand_positioning"]
            },
            {
                "script": "expert_agents/content_creator_agent.py",
                "agent_id": "content_creator",
                "port": 7009,
                "domain": "marketing",
                "capabilities": ["content_creation", "copywriting", "social_media"]
            },
            {
                "script": "expert_agents/healthcare_diagnostician_agent.py",
                "agent_id": "healthcare_diagnostician",
                "port": 7006,
                "domain": "healthcare",
                "capabilities": ["medical_diagnosis", "symptom_analysis", "clinical_assessment"]
            },
            {
                "script": "general_coordinator_agent.py",
                "agent_id": "general_coordinator",
                "port": 7010,
                "domain": "coordination",
                "capabilities": ["task_coordination", "agent_discovery", "workflow_management"]
            }
        ]

    def create_missing_agents(self):
        """Create agent scripts that don't exist yet"""
        print("🔧 Creating missing expert agent scripts...")

        # Create junior data scientist
        self._create_junior_data_scientist()
        self._create_risk_analyst()
        self._create_content_creator()
        self._create_healthcare_diagnostician()
        self._create_general_coordinator()

    def _create_junior_data_scientist(self):
        """Create junior data scientist agent"""
        script_path = "examples/expert_agents/junior_data_scientist_agent.py"
        if os.path.exists(script_path):
            return

        content = '''#!/usr/bin/env python3
"""
Junior Data Scientist Agent - Learning-focused with basic ML capabilities
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def main():
    agent_id = os.getenv("AGENT_ID", "junior_data_scientist")
    port = int(os.getenv("PORT", "7002"))

    adapter = StreamlinedAdapter(agent_id)

    capabilities = CapabilityTemplates.data_scientist("junior")
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="Junior data scientist learning advanced analytics. Skilled in basic ML, data visualization, and statistical analysis.",
        tags=["junior", "learning", "data_visualization", "basic_ml"]
    )

    def junior_handler(message_text: str, conversation_id: str) -> str:
        message_lower = message_text.lower()
        if "learn" in message_lower or "help" in message_lower:
            return f"I'm eager to learn! For {message_text}, I can start with basic analysis and ask for guidance on advanced techniques."
        elif "visualization" in message_lower:
            return f"I'll create clear visualizations for {message_text} using matplotlib, seaborn, and plotly for better insights."
        else:
            return f"Junior data scientist approach: {message_text}. I'll apply fundamental techniques and seek mentorship for complex problems."

    adapter.set_message_handler(junior_handler)

    try:
        adapter.start_agent_facts_server(port + 1000)
    except:
        pass

    print(f"👶 Junior Data Scientist Agent on port {port}")
    adapter.start_server(register_with_registry=True)

if __name__ == "__main__":
    main()
'''
        os.makedirs(os.path.dirname(script_path), exist_ok=True)
        with open(script_path, 'w') as f:
            f.write(content)

    def _create_risk_analyst(self):
        """Create risk analyst agent"""
        script_path = "examples/expert_agents/risk_analyst_agent.py"
        if os.path.exists(script_path):
            return

        content = '''#!/usr/bin/env python3
"""
Risk Analyst Expert Agent - Specialized in financial risk assessment
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def main():
    agent_id = os.getenv("AGENT_ID", "risk_analyst")
    port = int(os.getenv("PORT", "7005"))

    adapter = StreamlinedAdapter(agent_id)

    capabilities = CapabilityTemplates.financial_analyst("risk")
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="Risk analyst specializing in portfolio risk, VaR modeling, and stress testing for financial institutions.",
        tags=["expert", "risk_management", "portfolio", "var_modeling"]
    )

    def risk_handler(message_text: str, conversation_id: str) -> str:
        message_lower = message_text.lower()
        if "var" in message_lower or "value at risk" in message_lower:
            return f"Calculating VaR for {message_text} using Monte Carlo simulation, historical method, and parametric approach."
        elif "stress" in message_lower:
            return f"Conducting stress testing for {message_text} with adverse market scenarios and regulatory requirements."
        else:
            return f"Risk assessment: {message_text}. I'll quantify potential losses and recommend mitigation strategies."

    adapter.set_message_handler(risk_handler)

    try:
        adapter.start_agent_facts_server(port + 1000)
    except:
        pass

    print(f"⚠️ Risk Analyst Agent on port {port}")
    adapter.start_server(register_with_registry=True)

if __name__ == "__main__":
    main()
'''
        with open(script_path, 'w') as f:
            f.write(content)

    def _create_content_creator(self):
        """Create content creator agent"""
        script_path = "examples/expert_agents/content_creator_agent.py"
        if os.path.exists(script_path):
            return

        content = '''#!/usr/bin/env python3
"""
Content Creator Expert Agent - Creative content and copywriting specialist
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def main():
    agent_id = os.getenv("AGENT_ID", "content_creator")
    port = int(os.getenv("PORT", "7009"))

    adapter = StreamlinedAdapter(agent_id)

    capabilities = CapabilityTemplates.marketing_specialist("content")
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="Creative content specialist for copywriting, social media content, and brand messaging across digital platforms.",
        tags=["creative", "copywriting", "social_media", "content_strategy"]
    )

    def content_handler(message_text: str, conversation_id: str) -> str:
        message_lower = message_text.lower()
        if "social media" in message_lower:
            return f"Creating engaging social media content for {message_text} with platform-specific optimization and viral potential."
        elif "copy" in message_lower or "write" in message_lower:
            return f"Crafting compelling copy for {message_text} with persuasive messaging and clear call-to-action."
        else:
            return f"Content creation for {message_text}: developing creative concepts with brand alignment and audience engagement focus."

    adapter.set_message_handler(content_handler)

    try:
        adapter.start_agent_facts_server(port + 1000)
    except:
        pass

    print(f"✍️ Content Creator Agent on port {port}")
    adapter.start_server(register_with_registry=True)

if __name__ == "__main__":
    main()
'''
        with open(script_path, 'w') as f:
            f.write(content)

    def _create_healthcare_diagnostician(self):
        """Create healthcare diagnostician agent"""
        script_path = "examples/expert_agents/healthcare_diagnostician_agent.py"
        if os.path.exists(script_path):
            return

        content = '''#!/usr/bin/env python3
"""
Healthcare Diagnostician Agent - Medical diagnosis and clinical assessment
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def main():
    agent_id = os.getenv("AGENT_ID", "healthcare_diagnostician")
    port = int(os.getenv("PORT", "7006"))

    adapter = StreamlinedAdapter(agent_id)

    capabilities = CapabilityTemplates.healthcare_expert("diagnosis")
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="Healthcare diagnostician with expertise in symptom analysis, differential diagnosis, and clinical decision support.",
        tags=["medical", "diagnosis", "clinical_assessment", "healthcare"]
    )

    def health_handler(message_text: str, conversation_id: str) -> str:
        message_lower = message_text.lower()
        if "symptom" in message_lower or "diagnosis" in message_lower:
            return f"Clinical assessment for {message_text}: systematic symptom analysis, differential diagnosis, and evidence-based recommendations."
        elif "treatment" in message_lower:
            return f"Treatment planning for {message_text}: evidence-based protocols, patient-specific considerations, and monitoring requirements."
        else:
            return f"Healthcare analysis: {message_text}. I'll provide clinical insights with medical evidence and safety considerations."

    adapter.set_message_handler(health_handler)

    try:
        adapter.start_agent_facts_server(port + 1000)
    except:
        pass

    print(f"🏥 Healthcare Diagnostician Agent on port {port}")
    adapter.start_server(register_with_registry=True)

if __name__ == "__main__":
    main()
'''
        with open(script_path, 'w') as f:
            f.write(content)

    def _create_general_coordinator(self):
        """Create general coordinator agent"""
        script_path = "examples/general_coordinator_agent.py"
        if os.path.exists(script_path):
            return

        content = '''#!/usr/bin/env python3
"""
General Coordinator Agent - Task coordination and agent discovery
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def main():
    agent_id = os.getenv("AGENT_ID", "general_coordinator")
    port = int(os.getenv("PORT", "7010"))

    adapter = StreamlinedAdapter(agent_id)

    capabilities = CapabilityTemplates.general_assistant()
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="General coordinator for complex tasks requiring multiple expert agents. Specializes in agent discovery and workflow orchestration.",
        tags=["coordinator", "orchestration", "agent_discovery", "workflow"]
    )

    def coordinator_handler(message_text: str, conversation_id: str) -> str:
        message_lower = message_text.lower()

        # Demonstrate agent discovery
        if "financial" in message_lower and "analysis" in message_lower:
            return "I'll coordinate with @financial_analyst and @risk_analyst for comprehensive financial analysis. Discovering appropriate experts..."
        elif "data" in message_lower and ("analysis" in message_lower or "science" in message_lower):
            return "Coordinating with @senior_data_scientist and @junior_data_scientist for data analysis tasks. Finding best-matched experts..."
        elif "marketing" in message_lower:
            return "Engaging @marketing_strategist and @content_creator for integrated marketing solutions. Locating marketing experts..."
        elif "medical" in message_lower or "health" in message_lower:
            return "Connecting with @healthcare_diagnostician for medical expertise. Discovering healthcare specialists..."
        else:
            return f"Task coordination: {message_text}. I'll discover and engage appropriate expert agents based on required capabilities."

    adapter.set_message_handler(coordinator_handler)

    try:
        adapter.start_agent_facts_server(port + 1000)
    except:
        pass

    print(f"🎯 General Coordinator Agent on port {port}")
    adapter.start_server(register_with_registry=True)

if __name__ == "__main__":
    main()
'''
        with open(script_path, 'w') as f:
            f.write(content)

    def start_all_agents(self):
        """Start all expert agents"""
        print(f"🚀 Starting Expert Agent Sandbox on IP: {self.base_ip}")
        print("=" * 60)

        # Create missing agent scripts
        self.create_missing_agents()

        # Set environment variables
        os.environ["PUBLIC_IP"] = self.base_ip

        for agent in self.expert_agents:
            try:
                print(f"\n🤖 Starting {agent['agent_id']}...")
                self._start_agent(agent)
                time.sleep(3)  # Stagger startup
            except Exception as e:
                print(f"❌ Failed to start {agent['agent_id']}: {e}")

        self.running = True
        print(f"\n✅ Expert Agent Sandbox Running!")
        self._print_agent_status()

    def _start_agent(self, agent_config: Dict[str, Any]):
        """Start a single agent"""
        env = os.environ.copy()
        env["AGENT_ID"] = agent_config["agent_id"]
        env["PORT"] = str(agent_config["port"])
        env["PUBLIC_URL"] = f"http://{self.base_ip}:{agent_config['port']}"
        env["API_URL"] = f"http://{self.base_ip}:{agent_config['port'] + 100}"

        process = subprocess.Popen(
            [sys.executable, f"examples/{agent_config['script']}"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        self.agent_processes[agent_config["agent_id"]] = {
            "process": process,
            "config": agent_config
        }

        print(f"   ✅ {agent_config['agent_id']} started on port {agent_config['port']}")

    def _print_agent_status(self):
        """Print status of all agents"""
        print(f"\n📡 Expert Agents Registry:")
        print("-" * 40)
        for agent in self.expert_agents:
            print(f"  {agent['agent_id']:<25} http://{self.base_ip}:{agent['port']}/a2a")
            print(f"  {'':<25} AgentFacts: http://{self.base_ip}:{agent['port'] + 1000}/@{agent['agent_id']}.json")

    def demonstrate_discovery_scenarios(self):
        """Demonstrate agent discovery scenarios"""
        print(f"\n🎯 Agent Discovery Demonstration")
        print("=" * 50)

        scenarios = [
            {
                "task": "Analyze financial market trends and investment opportunities",
                "expected_agents": ["financial_analyst", "risk_analyst"],
                "capabilities": ["financial_analysis", "risk_assessment"]
            },
            {
                "task": "Build machine learning model for customer churn prediction",
                "expected_agents": ["senior_data_scientist", "junior_data_scientist"],
                "capabilities": ["machine_learning", "data_analysis"]
            },
            {
                "task": "Create comprehensive marketing campaign for product launch",
                "expected_agents": ["marketing_strategist", "content_creator"],
                "capabilities": ["marketing_strategy", "content_creation"]
            },
            {
                "task": "Analyze patient symptoms and recommend diagnostic approach",
                "expected_agents": ["healthcare_diagnostician"],
                "capabilities": ["medical_diagnosis", "clinical_assessment"]
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. Task: {scenario['task']}")
            print(f"   Expected Capabilities: {', '.join(scenario['capabilities'])}")
            print(f"   Expected Agents: {', '.join(scenario['expected_agents'])}")
            print(f"   Discovery URL: http://{self.base_ip}:7010/a2a")
            print(f"   Test Command:")
            print(f"   curl -X POST http://{self.base_ip}:7010/a2a \\")
            print(f"        -H 'Content-Type: application/json' \\")
            print(f"        -d '{{\"role\": \"user\", \"content\": {{\"type\": \"text\", \"text\": \"{scenario['task']}\"}}, \"conversation_id\": \"scenario_{i}\"}}'")

    def stop_all_agents(self):
        """Stop all running agents"""
        print(f"\n🛑 Stopping Expert Agent Sandbox...")
        for agent_id, agent_info in self.agent_processes.items():
            try:
                agent_info["process"].terminate()
                print(f"   ✅ {agent_id} stopped")
            except Exception as e:
                print(f"   ❌ Error stopping {agent_id}: {e}")

        self.running = False
        print(f"✅ Expert Agent Sandbox stopped")

def main():
    """Main function"""
    sandbox = ExpertSandbox()

    print(f"""
🏗️ Expert Agent Sandbox Orchestrator
====================================
This sandbox demonstrates:
✅ 8 expert agents with specialized capabilities
✅ AgentFacts-based capability registration
✅ Registry-based agent discovery
✅ A2A communication between experts
✅ Real-world multi-agent collaboration

Press Ctrl+C to stop the sandbox.
    """)

    try:
        # Start all agents
        sandbox.start_all_agents()

        # Wait a bit for agents to register
        print(f"\n⏳ Waiting for agents to register with registry...")
        time.sleep(10)

        # Show discovery scenarios
        sandbox.demonstrate_discovery_scenarios()

        print(f"\n🎯 Sandbox is running. Test agent discovery and A2A communication!")
        print(f"📋 Registry should now contain all expert agents with their capabilities.")

        # Keep running
        while sandbox.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n🛑 Received stop signal...")
        sandbox.stop_all_agents()

if __name__ == "__main__":
    main()
'''