#!/usr/bin/env python3
"""
Core components for the Streamlined NANDA Adapter
"""

from .core.adapter import StreamlinedAdapter
from .core.agent_bridge import StreamlinedAgentBridge
from .core.mcp_client import MCPClient
from .core.registry_client import RegistryClient

__all__ = [
    "StreamlinedAdapter",
    "StreamlinedAgentBridge",
    "MCPClient",
    "RegistryClient"
]