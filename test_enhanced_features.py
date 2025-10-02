#!/usr/bin/env python3
"""
Test script for enhanced NANDA features

Tests the new telemetry and semantic search functionality
"""

import os
import sys
import json
from typing import Dict, Any

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_telemetry_system():
    """Test the telemetry system"""
    print("🧪 Testing Telemetry System...")
    
    try:
        from nanda_core.telemetry.telemetry_system import TelemetrySystem
        
        # Create telemetry instance
        telemetry = TelemetrySystem("test-agent")
        
        # Log some test events
        telemetry.log_event("test", "startup", {"version": "2.0.0"})
        telemetry.log_message_received("test-agent", "conv-123")
        telemetry.log_message_sent("target-agent", "conv-123", True)
        telemetry.log_response_time(0.5, "message_handling")
        
        # Get metrics summary
        metrics = telemetry.get_metrics_summary(1)  # Last 1 hour
        
        print("✅ Telemetry System Working!")
        print(f"   📊 Total Events: {metrics['total_events']}")
        print(f"   📈 Event Types: {metrics['event_types']}")
        print(f"   ⚡ Performance: {metrics.get('performance', 'No data')}")
        
        # Test export
        json_export = telemetry.export_metrics("json", 1)
        print(f"   📄 JSON Export: {len(json_export)} characters")
        
        telemetry.stop()
        return True
        
    except Exception as e:
        print(f"❌ Telemetry Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_discovery_system():
    """Test the agent discovery system"""
    print("\n🧪 Testing Agent Discovery System...")
    
    try:
        from nanda_core.discovery.agent_discovery import AgentDiscovery
        from nanda_core.discovery.task_analyzer import TaskAnalyzer
        from nanda_core.discovery.agent_ranker import AgentRanker
        
        # Test task analyzer
        analyzer = TaskAnalyzer()
        task_analysis = analyzer.analyze_task("I need help with Python data analysis")
        
        print("✅ Task Analysis Working!")
        print(f"   🎯 Task Type: {task_analysis.task_type}")
        print(f"   🏷️ Domain: {task_analysis.domain}")
        print(f"   🔧 Required Capabilities: {task_analysis.required_capabilities}")
        print(f"   📊 Complexity: {task_analysis.complexity}")
        print(f"   🎪 Keywords: {task_analysis.keywords[:5]}")
        
        # Test agent ranker (with mock data)
        ranker = AgentRanker()
        mock_agents = [
            {
                "agent_id": "data-scientist-1",
                "domain": "data science",
                "capabilities": ["python", "data analysis", "machine learning"],
                "description": "Expert data scientist"
            },
            {
                "agent_id": "business-analyst-1", 
                "domain": "business analysis",
                "capabilities": ["market research", "strategy", "analysis"],
                "description": "Business strategy expert"
            }
        ]
        
        scores = ranker.rank_agents(mock_agents, task_analysis, {})
        
        print("✅ Agent Ranking Working!")
        for score in scores[:2]:
            print(f"   🤖 {score.agent_id}: Score {score.score:.2f}")
            if score.match_reasons:
                print(f"      ✅ {score.match_reasons[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Discovery Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_registry_client():
    """Test the registry client (mock test)"""
    print("\n🧪 Testing Registry Client...")
    
    try:
        from nanda_core.core.registry_client import RegistryClient
        
        # Create registry client (will use default URL)
        registry = RegistryClient("http://registry.chat39.com:6900")
        
        print("✅ Registry Client Created!")
        print(f"   🌐 Registry URL: {registry.registry_url}")
        
        # Note: We won't test actual network calls in this demo
        print("   📝 Note: Network calls not tested in demo mode")
        
        return True
        
    except Exception as e:
        print(f"❌ Registry Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enhanced_agent_creation():
    """Test creating an enhanced agent (without starting server)"""
    print("\n🧪 Testing Enhanced Agent Creation...")
    
    try:
        # Mock agent logic
        def test_agent_logic(message: str, conversation_id: str) -> str:
            return f"Test response to: {message}"
        
        from nanda_core.core.adapter import NANDA
        
        # Create enhanced agent
        agent = NANDA(
            agent_id="test-enhanced-agent",
            agent_logic=test_agent_logic,
            port=6999,  # Use a different port for testing
            registry_url="http://registry.chat39.com:6900",
            public_url="http://localhost:6999",
            enable_telemetry=True
        )
        
        print("✅ Enhanced Agent Created!")
        print(f"   🤖 Agent ID: {agent.agent_id}")
        print(f"   📊 Telemetry: {'Enabled' if agent.telemetry else 'Disabled'}")
        print(f"   🔍 Discovery: {'Enabled' if agent.bridge.discovery else 'Disabled'}")
        
        # Test telemetry if available
        if agent.telemetry:
            agent.telemetry.log_event("test", "agent_created", {"test": True})
            metrics = agent.telemetry.get_metrics_summary(1)
            print(f"   📈 Telemetry Events: {metrics['total_events']}")
        
        # Cleanup
        if agent.telemetry:
            agent.telemetry.stop()
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Agent Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("🚀 Testing Enhanced NANDA Features")
    print("=" * 50)
    
    tests = [
        ("Telemetry System", test_telemetry_system),
        ("Discovery System", test_discovery_system), 
        ("Registry Client", test_registry_client),
        ("Enhanced Agent", test_enhanced_agent_creation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Results Summary:")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    print(f"\n📊 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced features are working.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
