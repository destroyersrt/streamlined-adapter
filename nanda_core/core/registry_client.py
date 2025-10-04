#!/usr/bin/env python3
"""
Registry Client for Nanda Index Registry Integration
Handles agent registration, discovery, and management
"""

import requests
import json
import os
from typing import Optional, Dict, List, Any
from datetime import datetime


class RegistryClient:
    """Client for interacting with the Nanda index registry"""

    def __init__(self, registry_url: Optional[str] = None):
        self.registry_url = registry_url or self._get_default_registry_url()
        self.session = requests.Session()
        self.session.verify = False  # For development with self-signed certs

    def _get_default_registry_url(self) -> str:
        """Get default registry URL from configuration"""
        try:
            if os.path.exists("registry_url.txt"):
                with open("registry_url.txt", "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        return "http://capregistry.duckdns.org:6900"

    def register_agent(self, agent_id: str, agent_url: str, api_url: Optional[str] = None, agent_facts_url: Optional[str] = None) -> bool:
        """Register an agent with the registry"""
        try:
            data = {
                "agent_id": agent_id,
                "agent_url": agent_url
            }
            if api_url:
                data["api_url"] = api_url
            if agent_facts_url:
                data["agent_facts_url"] = agent_facts_url

            response = self.session.post(f"{self.registry_url}/register", json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error registering agent: {e}")
            return False

    def lookup_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Look up an agent in the registry"""
        try:
            response = self.session.get(f"{self.registry_url}/lookup/{agent_id}")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error looking up agent {agent_id}: {e}")
            return None

    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        try:
            response = self.session.get(f"{self.registry_url}/list")
            if response.status_code == 200:
                result = response.json()
                # Extract agents array from response
                return result.get('agents', [])
            return []
        except Exception as e:
            print(f"Error listing agents: {e}")
            return []

    def list_clients(self) -> List[Dict[str, Any]]:
        """List all registered clients"""
        try:
            response = self.session.get(f"{self.registry_url}/clients")
            if response.status_code == 200:
                return response.json()
            return self.list_agents()  # Fallback to list endpoint
        except Exception as e:
            print(f"Error listing clients: {e}")
            return []

    def get_agent_metadata(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed metadata for an agent"""
        agent_info = self.lookup_agent(agent_id)
        if not agent_info:
            return None

        # Extract additional metadata if available
        metadata = {
            "agent_id": agent_id,
            "agent_url": agent_info.get("agent_url"),
            "api_url": agent_info.get("api_url"),
            "last_seen": agent_info.get("last_seen"),
            "capabilities": agent_info.get("capabilities", []),
            "description": agent_info.get("description", ""),
            "tags": agent_info.get("tags", [])
        }
        return metadata

    def search_agents(self, query: str = "", capabilities: List[str] = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search for agents based on criteria"""
        try:
            # FIX: Use working structure-based searches instead of broken /search endpoint
            if query:
                print(f"🔍 Using structure-based search fallback for query: {query}")
                all_agents = []
                
                # Search across all structures and combine results
                for structure_type in ["keywords", "description", "embedding"]:
                    try:
                        structure_agents = self.search_agents_by_structure(query, structure_type, limit=10)
                        all_agents.extend(structure_agents)
                    except Exception as e:
                        print(f"Structure search failed for {structure_type}: {e}")
                        continue
                
                # Remove duplicates based on agent_id
                seen_ids = set()
                unique_agents = []
                for agent in all_agents:
                    agent_id = agent.get('agent_id')
                    if agent_id and agent_id not in seen_ids:
                        seen_ids.add(agent_id)
                        unique_agents.append(agent)
                
                print(f"🔍 Found {len(unique_agents)} unique agents across all structures")
                return unique_agents
            
            # Original logic for capabilities/tags (fallback)
            params = {}
            if capabilities:
                params["capabilities"] = ",".join(capabilities)
            if tags:
                params["tags"] = ",".join(tags)
            
            if params:
                response = self.session.get(f"{self.registry_url}/search", params=params)
                if response.status_code == 200:
                    result = response.json()
                    return result.get('agents', [])
            
            # Final fallback to local filtering
            return self._filter_agents_locally(query, capabilities, tags)
            
        except Exception as e:
            print(f"Error searching agents: {e}")
            return self._filter_agents_locally(query, capabilities, tags)

    def search_agents_by_structure(self, query: str, structure_type: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for agents with structure-specific filtering via registry API"""
        try:
            # Use embedding-specific endpoint for embedding searches
            if structure_type == "embedding":
                return self._search_agents_by_embedding(query, limit)
            
            # Use regular structure search for keywords/description
            params = {
                "q": query,
                "limit": limit
            }
            if structure_type:
                params["structure_type"] = structure_type

            # REMOVED: /search/structure endpoint - will be replaced by specific POST endpoints
            print(f"⚠️ Structure search temporarily disabled - will be replaced by POST endpoints")
            return []
        except Exception as e:
            print(f"❌ Error in structure search: {e}")
            return []

    def _search_agents_by_embedding(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search agents using embedding-based cosine similarity"""
        try:
            params = {
                "q": query,
                "limit": limit
            }

            response = self.session.get(f"{self.registry_url}/search/embedding", params=params)
            if response.status_code == 200:
                result = response.json()
                agents = result.get('agents', [])
                search_method = result.get('search_method', 'unknown')
                total_searched = result.get('total_agents_searched', 0)
                print(f"🎯 Registry embedding search: {len(agents)} results from {total_searched} agents using {search_method}")
                return agents
            else:
                print(f"⚠️ Registry embedding search failed: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error in embedding search: {e}")
            return []

    def _filter_agents_locally(self, query: str = "", capabilities: List[str] = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Fallback local filtering when server search is not available"""
        all_agents = self.list_agents()
        scored_agents = []

        for agent in all_agents:
            score = 0.0
            
            # Score based on query matching
            if query:
                query_words = query.lower().split()
                agent_text = f"{agent.get('agent_id', '')} {agent.get('description', '')} {agent.get('specialization', '')} {' '.join(agent.get('expertise', []))}"
                agent_text = agent_text.lower()
                
                # Score based on word matches
                word_matches = sum(1 for word in query_words if word in agent_text)
                if word_matches > 0:
                    score += (word_matches / len(query_words)) * 0.8
                
                # Bonus for agent_id matches (e.g., "tech-expert" matches "tech expert")
                agent_id_normalized = agent.get('agent_id', '').replace('-', ' ').replace('_', ' ').lower()
                if any(word in agent_id_normalized for word in query_words):
                    score += 0.5
                
                # Additional partial matching for better coverage
                for word in query_words:
                    if word in agent_text:
                        score += 0.2  # Small bonus for each word found
                    # Check for partial matches in agent_id (e.g., "tech" in "tech-expert")
                    if word in agent.get('agent_id', '').lower():
                        score += 0.3

            # Score based on capability matching
            if capabilities:
                agent_caps = agent.get('capabilities', [])
                cap_matches = sum(1 for cap in capabilities if cap in agent_caps)
                if cap_matches > 0:
                    score += (cap_matches / len(capabilities)) * 0.6

            # Score based on tag matching
            if tags:
                agent_tags = agent.get('tags', [])
                tag_matches = sum(1 for tag in tags if tag in agent_tags)
                if tag_matches > 0:
                    score += (tag_matches / len(tags)) * 0.4

            # If no specific criteria, give small base score to all agents
            if not query and not capabilities and not tags:
                score = 0.1

            if score > 0:
                scored_agents.append((agent, score))

        # Sort by score (highest first) and return top agents
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        filtered = [agent for agent, score in scored_agents[:20]]  # Return top 20

        return filtered

    def get_mcp_servers(self, registry_provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available MCP servers"""
        try:
            params = {}
            if registry_provider:
                params["registry_provider"] = registry_provider

            response = self.session.get(f"{self.registry_url}/mcp_servers", params=params)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting MCP servers: {e}")
            return []

    def get_mcp_server_config(self, registry_provider: str, qualified_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific MCP server"""
        try:
            response = self.session.get(f"{self.registry_url}/get_mcp_registry", params={
                'registry_provider': registry_provider,
                'qualified_name': qualified_name
            })

            if response.status_code == 200:
                result = response.json()
                config = result.get("config")
                config_json = json.loads(config) if isinstance(config, str) else config

                return {
                    "endpoint": result.get("endpoint"),
                    "config": config_json,
                    "registry_provider": result.get("registry_provider")
                }
            return None
        except Exception as e:
            print(f"Error getting MCP server config: {e}")
            return None

    def update_agent_status(self, agent_id: str, status: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update agent status and metadata"""
        try:
            data = {
                "agent_id": agent_id,
                "status": status,
                "last_seen": datetime.now().isoformat()
            }
            if metadata:
                data.update(metadata)

            response = self.session.put(f"{self.registry_url}/agents/{agent_id}/status", json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error updating agent status: {e}")
            return False

    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent from the registry"""
        try:
            response = self.session.delete(f"{self.registry_url}/agents/{agent_id}")
            return response.status_code == 200
        except Exception as e:
            print(f"Error unregistering agent: {e}")
            return False

    def health_check(self) -> bool:
        """Check if the registry is healthy"""
        try:
            response = self.session.get(f"{self.registry_url}/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def get_registry_stats(self) -> Optional[Dict[str, Any]]:
        """Get registry statistics"""
        try:
            response = self.session.get(f"{self.registry_url}/stats")
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting registry stats: {e}")
            return None

    # ================================
    # NEW METHODS FOR DECOUPLED SEARCH ARCHITECTURE
    # ================================

    def search_keyword(self, formatted_input: Dict) -> List[Dict]:
        """
        Call registry POST /search/keyword endpoint for LLM-based keyword matching.
        
        Args:
            formatted_input: {"keywords": ["keyword1", "keyword2", ...], "original_query": "..."}
            
        Returns:
            List of agent dictionaries with scores and metadata
        """
        try:
            response = self.session.post(f"{self.registry_url}/search/keyword", json=formatted_input)
            if response.status_code == 200:
                result = response.json()
                agents = result.get('agents', [])
                print(f"🔑 Registry keyword search: {len(agents)} results from {result.get('total_agents_searched', 0)} agents")
                return agents
            else:
                print(f"⚠️ Registry keyword search failed: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error in keyword search: {e}")
            return []

    def search_description(self, formatted_input: Dict) -> List[Dict]:
        """
        Call registry POST /search/description endpoint for text similarity search.
        
        Args:
            formatted_input: {"keywords": ["word1", "word2", ...], "original_query": "..."}
            
        Returns:
            List of agent dictionaries with scores and metadata
        """
        try:
            response = self.session.post(f"{self.registry_url}/search/description", json=formatted_input)
            if response.status_code == 200:
                result = response.json()
                agents = result.get('agents', [])
                print(f"📝 Registry description search: {len(agents)} results from {result.get('total_agents_searched', 0)} agents")
                return agents
            else:
                print(f"⚠️ Registry description search failed: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error in description search: {e}")
            return []

    def search_embedding(self, formatted_input: Dict) -> List[Dict]:
        """
        Call registry POST /search/embedding endpoint for cosine similarity search.
        
        Args:
            formatted_input: {"embedding": [0.1, 0.2, ...], "original_query": "..."}
            
        Returns:
            List of agent dictionaries with scores and metadata
        """
        try:
            response = self.session.post(f"{self.registry_url}/search/embedding", json=formatted_input)
            if response.status_code == 200:
                result = response.json()
                agents = result.get('agents', [])
                search_method = result.get('search_method', 'unknown')
                total_searched = result.get('total_agents_searched', 0)
                print(f"🎯 Registry embedding search: {len(agents)} results from {total_searched} agents using {search_method}")
                return agents
            else:
                print(f"⚠️ Registry embedding search failed: HTTP {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error in embedding search: {e}")
            return []

    def log_qa_interaction(self, interaction_data: Dict) -> bool:
        """
        Call registry POST /logger endpoint to log Q&A interactions.
        
        Args:
            interaction_data: {"query": "...", "agents": [...], "interactions": [...], "metadata": {...}}
            
        Returns:
            True if logging was successful, False otherwise
        """
        try:
            response = self.session.post(f"{self.registry_url}/logger", json=interaction_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"📊 Q&A interaction logged successfully: {result.get('log_id', 'unknown')}")
                    return True
                else:
                    print(f"⚠️ Logging failed: {result.get('message', 'unknown error')}")
                    return False
            else:
                print(f"⚠️ Registry logging failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Error in logging Q&A interaction: {e}")
            return False

    def cleanup_registry(self, collections: List[str] = None, confirm: bool = False) -> Dict:
        """
        Call registry POST /cleanup endpoint to clean up registry collections.
        
        Args:
            collections: List of collections to clean (default: ["agent_index", "agent_facts"])
            confirm: Safety confirmation flag
            
        Returns:
            Dictionary with cleanup results
        """
        try:
            cleanup_request = {
                "confirm": confirm
            }
            if collections:
                cleanup_request["collections"] = collections
                
            response = self.session.post(f"{self.registry_url}/cleanup", json=cleanup_request)
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    print(f"🧹 Registry cleanup successful: {result.get('counts', {})}")
                elif result.get('status') == 'confirmation_required':
                    print(f"⚠️ Cleanup requires confirmation: {result.get('message', '')}")
                return result
            else:
                print(f"⚠️ Registry cleanup failed: HTTP {response.status_code}")
                return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"❌ Error in registry cleanup: {e}")
            return {"status": "error", "message": str(e)}