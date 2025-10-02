#!/usr/bin/env python3
"""
Deploy Enhanced NANDA Agent Locally

Deploys an enhanced agent with telemetry and semantic search for testing
"""

import os
import sys
import subprocess
import time
import signal
import threading
from typing import Optional

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def deploy_enhanced_agent(agent_id: str = "enhanced-test-agent", port: int = 6000):
    """Deploy an enhanced agent locally"""
    
    print(f"🚀 Deploying Enhanced Agent: {agent_id}")
    print(f"Port: {port}")
    print("Features: Telemetry ✅, Semantic Search ✅, A2A Communication ✅")
    print("")
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        "AGENT_ID": agent_id,
        "AGENT_NAME": "Enhanced Test Agent",
        "AGENT_DOMAIN": "testing",
        "AGENT_SPECIALIZATION": "enhanced AI agent with telemetry and search",
        "AGENT_DESCRIPTION": "Test agent with enhanced telemetry and semantic search capabilities",
        "AGENT_CAPABILITIES": "testing,telemetry,semantic search,data analysis,general assistance",
        "REGISTRY_URL": "http://registry.chat39.com:6900",
        "PUBLIC_URL": f"http://localhost:{port}",
        "PORT": str(port)
    })
    
    # Start the enhanced agent
    try:
        print("🔄 Starting enhanced agent...")
        process = subprocess.Popen([
            sys.executable, "examples/enhanced_nanda_agent.py"
        ], env=env, cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print(f"✅ Agent started with PID: {process.pid}")
        print(f"🌐 Agent URL: http://localhost:{port}/a2a")
        print("")
        print("📋 Test Commands:")
        print(f"  # Test basic functionality:")
        print(f"  curl -X POST http://localhost:{port}/a2a -H 'Content-Type: application/json' \\")
        print(f"    -d '{{\"content\":{{\"text\":\"Hello! What can you help with?\",\"type\":\"text\"}},\"role\":\"user\",\"conversation_id\":\"test1\"}}'")
        print("")
        print(f"  # Test semantic search:")
        print(f"  curl -X POST http://localhost:{port}/a2a -H 'Content-Type: application/json' \\")
        print(f"    -d '{{\"content\":{{\"text\":\"? Find me a data scientist\",\"type\":\"text\"}},\"role\":\"user\",\"conversation_id\":\"search1\"}}'")
        print("")
        print(f"  # Test A2A communication:")
        print(f"  curl -X POST http://localhost:{port}/a2a -H 'Content-Type: application/json' \\")
        print(f"    -d '{{\"content\":{{\"text\":\"@test-agent Hello from enhanced agent\",\"type\":\"text\"}},\"role\":\"user\",\"conversation_id\":\"a2a1\"}}'")
        print("")
        print("Press Ctrl+C to stop the agent...")
        
        # Wait for the process
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping agent...")
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ Agent stopped")
    
    except Exception as e:
        print(f"❌ Error deploying agent: {e}")
        import traceback
        traceback.print_exc()


def test_agent_functionality(port: int = 6000):
    """Test the deployed agent functionality"""
    import requests
    import json
    
    base_url = f"http://localhost:{port}/a2a"
    
    print(f"🧪 Testing Agent at {base_url}")
    
    # Wait for agent to start
    print("⏳ Waiting for agent to start...")
    for i in range(10):
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                break
        except:
            pass
        time.sleep(1)
        print(f"   Attempt {i+1}/10...")
    
    tests = [
        {
            "name": "Basic Functionality",
            "message": "Hello! What can you help with?",
            "expected_keywords": ["help", "assist", "data"]
        },
        {
            "name": "Semantic Search",
            "message": "? Find me a data scientist",
            "expected_keywords": ["search", "agent", "found"]
        },
        {
            "name": "Telemetry Test",
            "message": "Can you analyze some data?",
            "expected_keywords": ["analyze", "data", "help"]
        }
    ]
    
    results = []
    
    for i, test in enumerate(tests, 1):
        print(f"\n🧪 Test {i}: {test['name']}")
        
        try:
            payload = {
                "content": {
                    "text": test["message"],
                    "type": "text"
                },
                "role": "user",
                "conversation_id": f"test-{i}"
            }
            
            response = requests.post(base_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("parts", [{}])[0].get("text", "")
                
                print(f"   ✅ Status: {response.status_code}")
                print(f"   📝 Response: {response_text[:100]}...")
                
                # Check for expected keywords
                found_keywords = [kw for kw in test["expected_keywords"] 
                                if kw.lower() in response_text.lower()]
                
                if found_keywords:
                    print(f"   🎯 Keywords found: {found_keywords}")
                    results.append(True)
                else:
                    print(f"   ⚠️ Expected keywords not found: {test['expected_keywords']}")
                    results.append(False)
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   📝 Response: {response.text}")
                results.append(False)
                
        except Exception as e:
            print(f"   ❌ Test failed: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features working correctly.")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return passed == total


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy Enhanced NANDA Agent")
    parser.add_argument("--agent-id", default="enhanced-test-agent", help="Agent ID")
    parser.add_argument("--port", type=int, default=6000, help="Port number")
    parser.add_argument("--test-only", action="store_true", help="Only run tests")
    
    args = parser.parse_args()
    
    if args.test_only:
        success = test_agent_functionality(args.port)
        sys.exit(0 if success else 1)
    else:
        deploy_enhanced_agent(args.agent_id, args.port)


if __name__ == "__main__":
    main()
