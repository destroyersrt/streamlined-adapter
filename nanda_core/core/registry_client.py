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
        return "https://registry.chat39.com"

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
                return response.json()
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
            params = {}
            if query:
                params["q"] = query
            if capabilities:
                params["capabilities"] = ",".join(capabilities)
            if tags:
                params["tags"] = ",".join(tags)

            response = self.session.get(f"{self.registry_url}/search", params=params)
            if response.status_code == 200:
                return response.json()

            # Fallback to client-side filtering
            return self._filter_agents_locally(query, capabilities, tags)
        except Exception as e:
            print(f"Error searching agents: {e}")
            return self._filter_agents_locally(query, capabilities, tags)

    def _filter_agents_locally(self, query: str = "", capabilities: List[str] = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Fallback local filtering when server search is not available"""
        all_agents = self.list_agents()
        filtered = []

        for agent in all_agents:
            # Simple text matching for query
            if query:
                agent_text = f"{agent.get('agent_id', '')} {agent.get('description', '')}"
                if query.lower() not in agent_text.lower():
                    continue

            # Capability matching
            if capabilities:
                agent_caps = agent.get('capabilities', [])
                if not any(cap in agent_caps for cap in capabilities):
                    continue

            # Tag matching
            if tags:
                agent_tags = agent.get('tags', [])
                if not any(tag in agent_tags for tag in tags):
                    continue

            filtered.append(agent)

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