#!/usr/bin/env python3
"""
Core components for the Streamlined NANDA Adapter
"""

from .adapter import StreamlinedAdapter
from .agent_bridge import StreamlinedAgentBridge
from .mcp_client import MCPClient, MCPRegistry
from .registry_client import RegistryClient

__all__ = [
    "StreamlinedAdapter",
    "StreamlinedAgentBridge",
    "MCPClient",
    "MCPRegistry",
    "RegistryClient"
]