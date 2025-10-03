import sys
sys.path.append('/home/ubuntu/nanda-60-domain-agents')

from nanda_core.core.registry_client import RegistryClient

print("🔍 Testing server RegistryClient:")
client = RegistryClient("http://capregistry.duckdns.org:6900")

try:
    agents = client.search_agents_by_structure("general data visualization statistics", "keywords", limit=5)
    print(f"  Server RegistryClient returned: {len(agents)} agents")
    for i, agent in enumerate(agents[:3]):
        print(f"    Agent {i+1}: {agent.get('agent_id', 'unknown')} (Score: {agent.get('score', 0):.3f})")
except Exception as e:
    print(f"  ERROR in server RegistryClient: {e}")
    import traceback
    traceback.print_exc()
