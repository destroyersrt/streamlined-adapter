#!/usr/bin/env python3
"""
Test 3-Agent Sandbox with Local Registry Integration
Tests full AgentFacts registration and capability-based discovery
"""

import os
import sys
import time
import subprocess
import socket
import requests
from typing import Dict, List, Any

def get_local_ip() -> str:
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def start_agent_with_registry(agent_config: Dict[str, Any], base_ip: str):
    """Start an agent configured for local registry"""
    env = os.environ.copy()
    env["AGENT_ID"] = agent_config["agent_id"]
    env["PORT"] = str(agent_config["port"])
    env["PUBLIC_URL"] = f"http://{base_ip}:{agent_config['port']}"
    env["API_URL"] = f"http://{base_ip}:{agent_config['port'] + 100}"
    env["PUBLIC_IP"] = base_ip
    env["REGISTRY_URL"] = "http://localhost:6900"  # Local registry

    print(f"🚀 Starting {agent_config['agent_id']} with registry registration...")

    process = subprocess.Popen(
        [sys.executable, f"examples/{agent_config['script']}"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    return process

def test_registry_functionality():
    """Test registry functionality with real agents"""
    base_ip = get_local_ip()
    print(f"🧪 Testing Local Registry Integration")
    print(f"🌐 Base IP: {base_ip}")
    print("=" * 50)

    # Define our 3 test agents
    agents = [
        {
            "script": "expert_agents/financial_analyst_agent.py",
            "agent_id": "financial_analyst",
            "port": 7004,
            "expected_domain": "finance",
            "expected_capabilities": ["financial_analysis", "market_research"]
        },
        {
            "script": "expert_agents/senior_data_scientist_agent.py",
            "agent_id": "senior_data_scientist",
            "port": 7001,
            "expected_domain": "data_science",
            "expected_capabilities": ["machine_learning", "data_analysis"]
        },
        {
            "script": "expert_agents/marketing_strategist_agent.py",
            "agent_id": "marketing_strategist",
            "port": 7008,
            "expected_domain": "marketing",
            "expected_capabilities": ["marketing_strategy", "campaign_planning"]
        }
    ]

    processes = []

    # Start all agents
    for agent in agents:
        try:
            process = start_agent_with_registry(agent, base_ip)
            processes.append({"process": process, "config": agent})
            time.sleep(4)  # Give time for startup and registration
        except Exception as e:
            print(f"❌ Failed to start {agent['agent_id']}: {e}")

    print(f"\n⏳ Waiting for agents to register (10 seconds)...")
    time.sleep(10)

    # Test registry integration
    test_registry_endpoints()
    test_capability_based_discovery()
    test_a2a_with_registry_lookup(base_ip)

    # Keep running for a bit
    print(f"\n🎯 Registry testing complete! Keeping agents running for 30 seconds...")
    time.sleep(30)

    # Cleanup
    print(f"\n🧹 Stopping agents...")
    for proc_info in processes:
        try:
            proc_info["process"].terminate()
        except Exception as e:
            print(f"Error stopping agent: {e}")

def test_registry_endpoints():
    """Test registry API endpoints"""
    print(f"\n📋 Testing Registry Endpoints")
    print("-" * 30)

    try:
        # Test health
        response = requests.get("http://localhost:6900/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Registry health: {health['agents_registered']} agents registered")
        else:
            print(f"❌ Registry health check failed: {response.status_code}")

        # Test list agents
        response = requests.get("http://localhost:6900/list", timeout=5)
        if response.status_code == 200:
            agents_data = response.json()
            agents = agents_data.get("agents", [])
            print(f"✅ Registry contains {len(agents)} agents:")
            for agent in agents:
                print(f"   • {agent['agent_id']} ({agent.get('domain', 'unknown')} domain)")
                print(f"     Capabilities: {', '.join(agent.get('capabilities', []))}")
        else:
            print(f"❌ Failed to list agents: {response.status_code}")

    except Exception as e:
        print(f"❌ Registry test error: {e}")

def test_capability_based_discovery():
    """Test capability-based agent discovery"""
    print(f"\n🔍 Testing Capability-Based Discovery")
    print("-" * 40)

    test_queries = [
        {
            "name": "Financial Analysis",
            "params": {"capabilities": "financial_analysis"},
            "expected_agent": "financial_analyst"
        },
        {
            "name": "Machine Learning",
            "params": {"capabilities": "machine_learning"},
            "expected_agent": "senior_data_scientist"
        },
        {
            "name": "Marketing Strategy",
            "params": {"capabilities": "marketing_strategy"},
            "expected_agent": "marketing_strategist"
        },
        {
            "name": "Finance Domain",
            "params": {"domain": "finance"},
            "expected_agent": "financial_analyst"
        },
        {
            "name": "Data Science Domain",
            "params": {"domain": "data_science"},
            "expected_agent": "senior_data_scientist"
        }
    ]

    for query in test_queries:
        try:
            response = requests.get("http://localhost:6900/search", params=query["params"], timeout=5)
            if response.status_code == 200:
                results = response.json()
                agents = results.get("agents", [])
                if agents and agents[0]["agent_id"] == query["expected_agent"]:
                    print(f"✅ {query['name']}: Found {agents[0]['agent_id']}")
                else:
                    found = agents[0]["agent_id"] if agents else "none"
                    print(f"❌ {query['name']}: Expected {query['expected_agent']}, found {found}")
            else:
                print(f"❌ {query['name']}: Search failed ({response.status_code})")
        except Exception as e:
            print(f"❌ {query['name']}: Error {e}")

def test_a2a_with_registry_lookup(base_ip: str):
    """Test A2A communication with registry-based agent lookup"""
    print(f"\n🔄 Testing A2A with Registry Lookup")
    print("-" * 35)

    # Test financial analyst sending message to data scientist
    try:
        a2a_url = f"http://{base_ip}:7004/a2a"
        message_data = {
            "role": "user",
            "content": {
                "type": "text",
                "text": "@senior_data_scientist Can you help with ML model for risk analysis?"
            },
            "conversation_id": "registry_test"
        }

        response = requests.post(a2a_url, json=message_data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("content", {}).get("text", "") if "content" in result else result.get("parts", [{}])[0].get("text", "")
            print(f"✅ A2A message sent successfully")
            print(f"   Response: {response_text[:100]}...")

            # Check if it found the agent (should not say "not found" anymore)
            if "not found" in response_text.lower():
                print(f"⚠️ Agent lookup still using local fallback (registry lookup may need enhancement)")
            else:
                print(f"✅ Registry-based agent lookup successful!")
        else:
            print(f"❌ A2A message failed: {response.status_code}")

    except Exception as e:
        print(f"❌ A2A test error: {e}")

def main():
    """Main test function"""
    print(f"""
🧪 Local Registry Integration Test
=================================
This test validates:
✅ Agent registration with AgentFacts URLs
✅ Capability extraction from AgentFacts
✅ Registry-based agent discovery
✅ A2A communication with registry lookup

Prerequisites:
• Local registry running on port 6900
• Flask installed for AgentFacts servers
    """)

    # Check if registry is running
    try:
        response = requests.get("http://localhost:6900/health", timeout=3)
        if response.status_code != 200:
            print("❌ Local registry not responding on port 6900")
            print("   Start it with: python examples/local_registry_server.py")
            return
    except Exception:
        print("❌ Local registry not running on port 6900")
        print("   Start it with: python examples/local_registry_server.py")
        return

    print("✅ Local registry is running")

    # Run the tests
    test_registry_functionality()

if __name__ == "__main__":
    main()