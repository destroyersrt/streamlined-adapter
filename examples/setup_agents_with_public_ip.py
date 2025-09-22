#!/usr/bin/env python3
"""
Setup agents with public IP addresses for real A2A testing
"""

import os
import sys
import socket
import subprocess
import threading
import time

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "localhost"

def setup_agent_environment(agent_id: str, port: int, ip_address: str):
    """Set up environment for an agent"""
    env = os.environ.copy()
    env["AGENT_ID"] = agent_id
    env["PORT"] = str(port)
    env["PUBLIC_URL"] = f"http://{ip_address}:{port}"
    env["API_URL"] = f"http://{ip_address}:{port + 100}"  # Different port for API
    env["PUBLIC_IP"] = ip_address  # Set the IP for agent lookup

    # Set API key if available
    if "ANTHROPIC_API_KEY" in os.environ:
        env["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_API_KEY"]

    return env

def start_agent(script_name: str, agent_id: str, port: int, ip_address: str):
    """Start an agent with proper environment"""
    env = setup_agent_environment(agent_id, port, ip_address)

    print(f"🚀 Starting {agent_id} on {ip_address}:{port}")
    print(f"   PUBLIC_URL: {env['PUBLIC_URL']}")
    print(f"   API_URL: {env['API_URL']}")

    # Start the agent process
    process = subprocess.Popen(
        [sys.executable, f"examples/{script_name}"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    return process

def main():
    """Set up and start both agents with proper IP configuration"""
    print("🌐 Setting up agents with public IP addresses")
    print("=" * 50)

    # Get local IP
    local_ip = get_local_ip()
    print(f"🔍 Detected local IP address: {local_ip}")

    # Agent configurations
    agents = [
        {
            "script": "sarcastic_agent.py",
            "agent_id": "sarcastic_agent",
            "port": 6002
        },
        {
            "script": "helpful_agent.py",
            "agent_id": "helpful_agent",
            "port": 6003
        }
    ]

    processes = []

    # Start agents
    for agent in agents:
        try:
            process = start_agent(
                agent["script"],
                agent["agent_id"],
                agent["port"],
                local_ip
            )
            processes.append({
                "process": process,
                "name": agent["agent_id"],
                "port": agent["port"]
            })

            print(f"✅ {agent['agent_id']} started")

        except Exception as e:
            print(f"❌ Failed to start {agent['agent_id']}: {str(e)}")

    if not processes:
        print("❌ No agents started successfully")
        return

    print(f"\n🎯 Agents started with IP: {local_ip}")
    print("📡 A2A endpoints:")
    for agent in agents:
        print(f"   {agent['agent_id']}: http://{local_ip}:{agent['port']}/a2a")

    print(f"\n🧪 Test A2A communication:")
    print(f"""
# Test sarcastic agent
curl -X POST http://{local_ip}:6002/a2a \\
  -H "Content-Type: application/json" \\
  -d '{{"role": "user", "content": {{"type": "text", "text": "@helpful_agent Hello from sarcastic!"}}, "conversation_id": "test1"}}'

# Test helpful agent
curl -X POST http://{local_ip}:6003/a2a \\
  -H "Content-Type: application/json" \\
  -d '{{"role": "user", "content": {{"type": "text", "text": "@sarcastic_agent Hello from helpful!"}}, "conversation_id": "test2"}}'
    """)

    print("\n📋 What to expect:")
    print("  1. Agents will attempt registry lookup first")
    print("  2. Fall back to local testing lookup")
    print("  3. Send messages between agents")
    print("  4. Receiving agents will process and respond")
    print("  5. Full conversation logs will be visible")

    print("\n🛑 Press Ctrl+C to stop all agents")

    try:
        # Monitor processes
        while True:
            time.sleep(1)

            # Check if any process died
            for proc_info in processes:
                if proc_info["process"].poll() is not None:
                    print(f"⚠️ Agent {proc_info['name']} stopped")

    except KeyboardInterrupt:
        print("\n🛑 Stopping all agents...")
        for proc_info in processes:
            proc_info["process"].terminate()

        # Wait for cleanup
        time.sleep(2)
        print("✅ All agents stopped")

if __name__ == "__main__":
    main()