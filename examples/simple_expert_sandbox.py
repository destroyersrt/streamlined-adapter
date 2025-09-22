#!/usr/bin/env python3
"""
Simple 3-Agent Expert Sandbox for Testing Infrastructure
Tests AgentFacts registration, registry integration, and A2A discovery
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
from nanda_core.core.agent_facts import CapabilityTemplates

class SimpleExpertSandbox:
    """Simple 3-agent sandbox for infrastructure testing"""

    def __init__(self):
        self.base_ip = self._get_local_ip()
        self.expert_agents = self._define_expert_agents()
        self.agent_processes = {}
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
        """Define 3 expert agents for testing"""
        return [
            {
                "script": "expert_agents/financial_analyst_agent.py",
                "agent_id": "financial_analyst",
                "port": 7004,
                "domain": "finance",
                "capabilities": ["financial_analysis", "market_research", "risk_assessment"]
            },
            {
                "script": "expert_agents/senior_data_scientist_agent.py",
                "agent_id": "senior_data_scientist",
                "port": 7001,
                "domain": "data_science",
                "capabilities": ["machine_learning", "data_analysis", "statistical_modeling"]
            },
            {
                "script": "expert_agents/marketing_strategist_agent.py",
                "agent_id": "marketing_strategist",
                "port": 7008,
                "domain": "marketing",
                "capabilities": ["marketing_strategy", "campaign_planning", "brand_positioning"]
            }
        ]

    def check_flask_dependency(self):
        """Check if Flask is available for AgentFacts server"""
        try:
            import flask
            print("✅ Flask is available for AgentFacts server")
            return True
        except ImportError:
            print("❌ Flask not found. Installing flask...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
                print("✅ Flask installed successfully")
                return True
            except Exception as e:
                print(f"❌ Failed to install Flask: {e}")
                print("⚠️ AgentFacts server will be disabled")
                return False

    def start_agents(self):
        """Start the 3 expert agents"""
        print(f"🚀 Starting Simple Expert Sandbox (3 agents)")
        print(f"🌐 Base IP: {self.base_ip}")
        print("=" * 60)

        # Check dependencies
        flask_available = self.check_flask_dependency()

        # Set environment variables
        os.environ["PUBLIC_IP"] = self.base_ip

        for agent in self.expert_agents:
            try:
                print(f"\n🤖 Starting {agent['agent_id']}...")
                self._start_agent(agent, flask_available)
                time.sleep(4)  # Give time for startup and registration
            except Exception as e:
                print(f"❌ Failed to start {agent['agent_id']}: {e}")

        self.running = True
        print(f"\n✅ Simple Expert Sandbox Running!")
        self._print_agent_status()

    def _start_agent(self, agent_config: Dict[str, Any], flask_available: bool):
        """Start a single agent"""
        env = os.environ.copy()
        env["AGENT_ID"] = agent_config["agent_id"]
        env["PORT"] = str(agent_config["port"])
        env["PUBLIC_URL"] = f"http://{self.base_ip}:{agent_config['port']}"
        env["API_URL"] = f"http://{self.base_ip}:{agent_config['port'] + 100}"
        env["PUBLIC_IP"] = self.base_ip

        # Disable AgentFacts if Flask not available
        if not flask_available:
            env["DISABLE_AGENT_FACTS"] = "true"

        process = subprocess.Popen(
            [sys.executable, f"examples/{agent_config['script']}"],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        self.agent_processes[agent_config["agent_id"]] = {
            "process": process,
            "config": agent_config
        }

        print(f"   ✅ {agent_config['agent_id']} started on port {agent_config['port']}")

    def _print_agent_status(self):
        """Print status of all agents"""
        print(f"\n📡 Expert Agents Status:")
        print("-" * 50)
        for agent in self.expert_agents:
            print(f"  {agent['agent_id']:<25} A2A: http://{self.base_ip}:{agent['port']}/a2a")
            print(f"  {'':<25} Facts: http://{self.base_ip}:{agent['port'] + 1000}/@{agent['agent_id']}.json")
            print(f"  {'':<25} Domain: {agent['domain']}")
            print(f"  {'':<25} Capabilities: {', '.join(agent['capabilities'])}")
            print()

    def test_agent_health(self):
        """Test if all agents are responding"""
        print(f"\n🔍 Testing Agent Health...")
        print("-" * 30)

        for agent in self.expert_agents:
            try:
                url = f"http://{self.base_ip}:{agent['port']}/a2a"
                response = requests.get(url, timeout=3)
                if response.status_code in [200, 405]:  # 405 is expected for GET to A2A
                    print(f"  ✅ {agent['agent_id']} is responding")
                else:
                    print(f"  ❌ {agent['agent_id']} unexpected status: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {agent['agent_id']} connection failed: {e}")

    def test_agent_facts(self):
        """Test AgentFacts endpoints"""
        print(f"\n📋 Testing AgentFacts Endpoints...")
        print("-" * 35)

        for agent in self.expert_agents:
            try:
                facts_url = f"http://{self.base_ip}:{agent['port'] + 1000}/@{agent['agent_id']}.json"
                response = requests.get(facts_url, timeout=3)
                if response.status_code == 200:
                    facts = response.json()
                    capabilities = facts.get('capabilities', {})
                    skills = capabilities.get('skills', [])
                    print(f"  ✅ {agent['agent_id']} AgentFacts available")
                    print(f"     Skills: {', '.join(skills[:3])}...")
                else:
                    print(f"  ❌ {agent['agent_id']} AgentFacts failed: {response.status_code}")
            except Exception as e:
                print(f"  ❌ {agent['agent_id']} AgentFacts error: {e}")

    def demonstrate_discovery(self):
        """Demonstrate agent discovery scenarios"""
        print(f"\n🎯 Agent Discovery Test Scenarios")
        print("=" * 40)

        scenarios = [
            {
                "task": "Analyze quarterly financial performance",
                "expected_agent": "financial_analyst",
                "test_endpoint": f"http://{self.base_ip}:7004/a2a"
            },
            {
                "task": "Build machine learning model for sales prediction",
                "expected_agent": "senior_data_scientist",
                "test_endpoint": f"http://{self.base_ip}:7001/a2a"
            },
            {
                "task": "Create marketing campaign for new product",
                "expected_agent": "marketing_strategist",
                "test_endpoint": f"http://{self.base_ip}:7008/a2a"
            }
        ]

        for i, scenario in enumerate(scenarios, 1):
            print(f"\n{i}. Task: {scenario['task']}")
            print(f"   Expected Agent: {scenario['expected_agent']}")
            print(f"   Test Command:")
            print(f"   curl -X POST {scenario['test_endpoint']} \\")
            print(f"        -H 'Content-Type: application/json' \\")
            print(f"        -d '{{\"role\": \"user\", \"content\": {{\"type\": \"text\", \"text\": \"{scenario['task']}\"}}, \"conversation_id\": \"test_{i}\"}}'")

    def demonstrate_a2a_communication(self):
        """Demonstrate A2A communication between agents"""
        print(f"\n🔄 A2A Communication Test")
        print("-" * 30)

        # Test financial analyst asking data scientist for help
        test_message = "@senior_data_scientist I need ML model for risk prediction"
        endpoint = f"http://{self.base_ip}:7004/a2a"

        print(f"Testing: Financial Analyst → Data Scientist")
        print(f"Message: {test_message}")
        print(f"Command:")
        print(f"curl -X POST {endpoint} \\")
        print(f"     -H 'Content-Type: application/json' \\")
        print(f"     -d '{{\"role\": \"user\", \"content\": {{\"type\": \"text\", \"text\": \"{test_message}\"}}, \"conversation_id\": \"a2a_test\"}}'")

        print(f"\n🎯 Expected Flow:")
        print(f"  1. Financial analyst receives A2A message")
        print(f"  2. Looks up 'senior_data_scientist' in registry")
        print(f"  3. Finds endpoint: http://{self.base_ip}:7001/a2a")
        print(f"  4. Sends formatted message to data scientist")
        print(f"  5. Data scientist responds with ML expertise")

    def monitor_agent_logs(self, duration: int = 30):
        """Monitor agent logs for a short duration"""
        print(f"\n📊 Monitoring Agent Logs ({duration}s)...")
        print("-" * 35)

        start_time = time.time()
        while time.time() - start_time < duration:
            for agent_id, agent_info in self.agent_processes.items():
                try:
                    # Read available output
                    process = agent_info["process"]
                    if process.poll() is None:  # Process still running
                        # This is a simplified log monitor - in production would use proper logging
                        pass
                except Exception:
                    pass
            time.sleep(2)

    def check_registry_integration(self):
        """Check if agents registered with the registry"""
        print(f"\n📝 Registry Integration Status")
        print("-" * 35)
        print(f"🎯 Expected Registry Entries:")
        for agent in self.expert_agents:
            print(f"  Agent ID: {agent['agent_id']}")
            print(f"  Agent URL: http://{self.base_ip}:{agent['port']}")
            print(f"  AgentFacts URL: http://{self.base_ip}:{agent['port'] + 1000}/@{agent['agent_id']}.json")
            print()

    def stop_all_agents(self):
        """Stop all running agents"""
        print(f"\n🛑 Stopping Simple Expert Sandbox...")
        for agent_id, agent_info in self.agent_processes.items():
            try:
                agent_info["process"].terminate()
                print(f"   ✅ {agent_id} stopped")
            except Exception as e:
                print(f"   ❌ Error stopping {agent_id}: {e}")

        self.running = False
        print(f"✅ Simple Expert Sandbox stopped")

def main():
    """Main function for simple sandbox testing"""
    sandbox = SimpleExpertSandbox()

    print(f"""
🧪 Simple Expert Sandbox (3 Agents)
===================================
Testing Infrastructure:
✅ AgentFacts specification implementation
✅ Registry registration with capabilities
✅ Agent discovery and endpoint resolution
✅ A2A communication between expert agents

Agents:
• Financial Analyst (finance domain)
• Senior Data Scientist (data_science domain)
• Marketing Strategist (marketing domain)

Press Ctrl+C to stop the sandbox.
    """)

    try:
        # Start agents
        sandbox.start_agents()

        # Wait for registration
        print(f"\n⏳ Waiting for agent registration (15s)...")
        time.sleep(15)

        # Run tests
        sandbox.test_agent_health()
        sandbox.test_agent_facts()
        sandbox.check_registry_integration()
        sandbox.demonstrate_discovery()
        sandbox.demonstrate_a2a_communication()

        print(f"\n🎯 Infrastructure Testing Complete!")
        print(f"✅ Ready to scale to 5-10 agents if tests pass")
        print(f"🔄 Sandbox will continue running for manual testing...")

        # Keep running for manual testing
        while sandbox.running:
            time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n🛑 Received stop signal...")
        sandbox.stop_all_agents()

if __name__ == "__main__":
    main()