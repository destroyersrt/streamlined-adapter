#!/usr/bin/env python3
"""
Complete System Local Testing

Tests the entire NANDA system locally:
1. Modular embeddings
2. MongoDB agent facts
3. Semantic search
4. Telemetry system
5. Agent discovery
"""

import os
import sys
import time
from typing import Dict, List, Any

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts
from nanda_core.embeddings.embedding_manager import get_embedding_manager
from nanda_core.telemetry.mongodb_telemetry import MongoDBTelemetryStorage
from nanda_core.discovery.agent_discovery import AgentDiscovery
from nanda_core.core.registry_client import RegistryClient


class CompleteSystemTester:
    """Test the complete NANDA system locally"""
    
    def __init__(self):
        self.results = {}
        print("🚀 Initializing Complete System Test...")
    
    def test_1_modular_embeddings(self):
        """Test 1: Modular Embedding System"""
        print("\n" + "="*60)
        print("🧩 TEST 1: Modular Embedding System")
        print("="*60)
        
        try:
            # Initialize embedding manager
            manager = get_embedding_manager('embedding_config.json')
            
            # Check status
            status = manager.get_active_embedder_info()
            print(f"✅ Active embedder: {status.get('name')} ({status.get('model')})")
            print(f"   Dimension: {status.get('dimension')}, Fallbacks: {status.get('fallbacks_available')}")
            
            # Test embedding creation
            test_text = "Python developer specializing in web applications and REST APIs"
            start_time = time.time()
            embedding = manager.create_embedding(test_text)
            embedding_time = time.time() - start_time
            
            print(f"✅ Single embedding: {len(embedding)} dimensions in {embedding_time:.3f}s")
            
            # Test batch embeddings
            test_texts = [
                "Data scientist expert in machine learning",
                "DevOps engineer with cloud expertise",
                "Frontend developer using React"
            ]
            start_time = time.time()
            embeddings = manager.create_batch_embeddings(test_texts)
            batch_time = time.time() - start_time
            
            print(f"✅ Batch embeddings: {len(embeddings)} embeddings in {batch_time:.3f}s")
            
            # Test fallback behavior
            print("\n🔄 Testing fallback behavior...")
            all_status = manager.get_all_embedders_status()
            for name, embedder_status in all_status.items():
                status_icon = "✅" if embedder_status.get('enabled') else "❌"
                available_icon = "🟢" if embedder_status.get('available') else "🔴"
                print(f"   {status_icon} {available_icon} {name}: {embedder_status.get('model', 'N/A')}")
            
            self.results['embeddings'] = {
                'status': 'success',
                'active_embedder': status.get('name'),
                'single_time': embedding_time,
                'batch_time': batch_time,
                'dimension': len(embedding)
            }
            
        except Exception as e:
            print(f"❌ Embedding test failed: {e}")
            self.results['embeddings'] = {'status': 'failed', 'error': str(e)}
    
    def test_2_mongodb_agent_facts(self):
        """Test 2: MongoDB Agent Facts with Modular Embeddings"""
        print("\n" + "="*60)
        print("📊 TEST 2: MongoDB Agent Facts")
        print("="*60)
        
        try:
            # Initialize MongoDB agent facts
            mongo_facts = MongoDBAgentFacts()
            
            # Check agent counts by structure type
            total_agents = mongo_facts.get_agent_count()
            keywords_count = mongo_facts.collection.count_documents({'structure_type': 'keywords'})
            description_count = mongo_facts.collection.count_documents({'structure_type': 'description'})
            embedding_count = mongo_facts.collection.count_documents({'structure_type': 'embedding'})
            
            print(f"✅ Total agents: {total_agents}")
            print(f"   Keywords: {keywords_count}, Descriptions: {description_count}, Embeddings: {embedding_count}")
            
            # Test modular embedding updates
            print(f"\n🔄 Testing modular embedding updates...")
            updated_count = mongo_facts.update_agents_with_modular_embeddings('embedding')
            print(f"✅ Updated {updated_count} agents with modular embeddings")
            
            # Test search functionality
            print(f"\n🔍 Testing search functionality...")
            test_queries = [
                "python web development",
                "machine learning data science", 
                "cloud infrastructure kubernetes"
            ]
            
            search_results = {}
            for query in test_queries:
                start_time = time.time()
                results = mongo_facts.search_agents_by_capabilities(query, limit=5)
                search_time = time.time() - start_time
                
                print(f"   '{query}': {len(results)} results in {search_time:.3f}s")
                search_results[query] = {
                    'count': len(results),
                    'time': search_time,
                    'top_result': results[0].get('agent_name') if results else None
                }
            
            self.results['mongodb'] = {
                'status': 'success',
                'total_agents': total_agents,
                'structure_counts': {
                    'keywords': keywords_count,
                    'description': description_count,
                    'embedding': embedding_count
                },
                'updated_count': updated_count,
                'search_results': search_results
            }
            
        except Exception as e:
            print(f"❌ MongoDB test failed: {e}")
            self.results['mongodb'] = {'status': 'failed', 'error': str(e)}
    
    def test_3_telemetry_system(self):
        """Test 3: Telemetry System"""
        print("\n" + "="*60)
        print("📈 TEST 3: Telemetry System")
        print("="*60)
        
        try:
            # Initialize telemetry
            telemetry = MongoDBTelemetryStorage()
            
            # Test storing telemetry data
            from nanda_core.telemetry.mongodb_telemetry import QueryTelemetry
            from datetime import datetime
            import uuid
            
            test_telemetry = QueryTelemetry(
                query_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                agent_id='test-agent-local',
                session_id='local-test-session',
                query_text='python expert test',
                query_type='search',
                conversation_id='local-test-conv',
                search_time=0.25,
                agents_found=5,
                search_method='mongodb',
                top_agents=[{'agent_id': 'test-1', 'score': 0.95}],
                result_quality_score=0.85,
                memory_usage_mb=128.0,
                cpu_usage_percent=15.0,
                response_time=0.30,
                success=True
            )
            
            # Store telemetry
            result_id = telemetry.store_query_telemetry(test_telemetry)
            print(f"✅ Stored telemetry: {result_id}")
            
            # Test analytics
            analytics = telemetry.get_query_analytics(hours=1)
            print(f"✅ Analytics: {analytics.get('total_queries', 0)} queries, "
                  f"avg time: {analytics.get('avg_search_time', 0):.3f}s")
            
            # Test top queries
            top_queries = telemetry.get_top_queries(hours=24, limit=3)
            print(f"✅ Top queries: {len(top_queries)} found")
            for query in top_queries[:2]:
                print(f"   '{query.get('query_text', 'N/A')}' ({query.get('count', 0)} times)")
            
            self.results['telemetry'] = {
                'status': 'success',
                'stored_id': str(result_id),
                'analytics': analytics,
                'top_queries_count': len(top_queries)
            }
            
        except Exception as e:
            print(f"❌ Telemetry test failed: {e}")
            self.results['telemetry'] = {'status': 'failed', 'error': str(e)}
    
    def test_4_agent_discovery(self):
        """Test 4: Agent Discovery System"""
        print("\n" + "="*60)
        print("🔍 TEST 4: Agent Discovery System")
        print("="*60)
        
        try:
            # Initialize agent discovery (without registry for local test)
            discovery = AgentDiscovery(registry_client=None)
            
            # Test task analysis and agent discovery
            test_queries = [
                "I need a Python developer for web applications",
                "Looking for machine learning expertise",
                "Need help with cloud infrastructure setup"
            ]
            
            discovery_results = {}
            for query in test_queries:
                start_time = time.time()
                
                # This will use MongoDB search since registry_client is None
                result = discovery.discover_agents(query, limit=5)
                
                discovery_time = time.time() - start_time
                
                print(f"   '{query[:30]}...': {len(result.recommended_agents)} agents in {discovery_time:.3f}s")
                
                if result.recommended_agents:
                    top_agent = result.recommended_agents[0]
                    print(f"      Top: {top_agent.agent_id} (score: {top_agent.score:.3f})")
                
                discovery_results[query] = {
                    'count': len(result.recommended_agents),
                    'time': discovery_time,
                    'top_agent': result.recommended_agents[0].agent_id if result.recommended_agents else None,
                    'top_score': result.recommended_agents[0].score if result.recommended_agents else 0
                }
            
            self.results['discovery'] = {
                'status': 'success',
                'results': discovery_results
            }
            
        except Exception as e:
            print(f"❌ Discovery test failed: {e}")
            self.results['discovery'] = {'status': 'failed', 'error': str(e)}
    
    def test_5_integration_flow(self):
        """Test 5: Complete Integration Flow"""
        print("\n" + "="*60)
        print("🔄 TEST 5: Complete Integration Flow")
        print("="*60)
        
        try:
            # Simulate a complete search flow like the agent bridge would do
            from nanda_core.telemetry.telemetry_system import TelemetrySystem
            
            # Initialize components
            mongo_facts = MongoDBAgentFacts()
            telemetry = TelemetrySystem('local-test-agent')
            
            # Test query
            test_query = "python web development expert"
            print(f"🔍 Testing complete flow for: '{test_query}'")
            
            # Step 1: Search agents
            start_time = time.time()
            search_results = mongo_facts.search_agents_by_capabilities(test_query, limit=5)
            search_time = time.time() - start_time
            
            print(f"   Step 1 - Search: {len(search_results)} results in {search_time:.3f}s")
            
            # Step 2: Log telemetry
            if telemetry.use_mongodb_telemetry:
                telemetry.log_structured_query(
                    query_text=test_query,
                    query_type='integration_test',
                    conversation_id='local-integration-test',
                    search_time=search_time,
                    agents_found=len(search_results),
                    search_method='mongodb',
                    top_agents=[{
                        'agent_id': result.get('agent_id', 'unknown'),
                        'score': result.get('relevance_score', 0)
                    } for result in search_results[:3]],
                    result_quality_score=0.85,
                    response_time=search_time + 0.05,
                    success=True
                )
                print(f"   Step 2 - Telemetry: Logged successfully")
            
            # Step 3: Format response (simulate agent bridge response)
            if search_results:
                response_text = f"🔍 Found {len(search_results)} agents for '{test_query}':\\n"
                for i, agent in enumerate(search_results[:3]):
                    agent_id = agent.get('agent_id', 'unknown')
                    agent_name = agent.get('agent_name', 'Unknown')
                    score = agent.get('relevance_score', 0)
                    response_text += f"  {i+1}. {agent_name} ({agent_id}) - Score: {score:.3f}\\n"
                
                print(f"   Step 3 - Response: Generated ({len(response_text)} chars)")
            else:
                response_text = f"🔍 No agents found for '{test_query}'"
                print(f"   Step 3 - Response: No results")
            
            self.results['integration'] = {
                'status': 'success',
                'query': test_query,
                'search_time': search_time,
                'results_count': len(search_results),
                'response_length': len(response_text),
                'telemetry_logged': telemetry.use_mongodb_telemetry
            }
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
            self.results['integration'] = {'status': 'failed', 'error': str(e)}
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📋 COMPLETE SYSTEM TEST REPORT")
        print("="*80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for result in self.results.values() if result.get('status') == 'success')
        
        print(f"\n🎯 Overall Results: {passed_tests}/{total_tests} tests passed")
        
        for test_name, result in self.results.items():
            status_icon = "✅" if result.get('status') == 'success' else "❌"
            print(f"\n{status_icon} {test_name.upper()}:")
            
            if result.get('status') == 'success':
                if test_name == 'embeddings':
                    print(f"   Active: {result['active_embedder']}")
                    print(f"   Performance: {result['single_time']:.3f}s single, {result['batch_time']:.3f}s batch")
                    print(f"   Dimension: {result['dimension']}")
                
                elif test_name == 'mongodb':
                    print(f"   Agents: {result['total_agents']} total")
                    print(f"   Updated: {result['updated_count']} with modular embeddings")
                    print(f"   Search: {len(result['search_results'])} queries tested")
                
                elif test_name == 'telemetry':
                    print(f"   Storage: Working (ID: {result['stored_id'][:8]}...)")
                    print(f"   Analytics: {result['analytics'].get('total_queries', 0)} queries tracked")
                
                elif test_name == 'discovery':
                    print(f"   Queries: {len(result['results'])} tested")
                    avg_time = sum(r['time'] for r in result['results'].values()) / len(result['results'])
                    print(f"   Avg time: {avg_time:.3f}s")
                
                elif test_name == 'integration':
                    print(f"   Query: '{result['query']}'")
                    print(f"   Results: {result['results_count']} in {result['search_time']:.3f}s")
                    print(f"   Telemetry: {'✅' if result['telemetry_logged'] else '❌'}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
        
        # System readiness assessment
        print(f"\n🚀 SYSTEM READINESS:")
        if passed_tests == total_tests:
            print("   ✅ All systems operational - Ready for deployment!")
        elif passed_tests >= total_tests * 0.8:
            print("   ⚠️ Most systems working - Minor issues to resolve")
        else:
            print("   ❌ Major issues detected - Fix before deployment")
        
        return passed_tests == total_tests


if __name__ == "__main__":
    print("🧪 NANDA Complete System Local Testing")
    print("="*80)
    
    tester = CompleteSystemTester()
    
    # Run all tests
    tester.test_1_modular_embeddings()
    tester.test_2_mongodb_agent_facts()
    tester.test_3_telemetry_system()
    tester.test_4_agent_discovery()
    tester.test_5_integration_flow()
    
    # Generate report
    all_passed = tester.generate_test_report()
    
    if all_passed:
        print(f"\n🎉 All tests passed! System ready for end-to-end testing.")
    else:
        print(f"\n⚠️ Some tests failed. Review issues before proceeding.")
