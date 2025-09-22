#!/usr/bin/env python3
"""
Streamlined NANDA Adapter - Efficient AI Agent Communication System

A clean, feature-rich adapter that maintains full functionality parity with the original
while eliminating unnecessary query preprocessing and adding intelligent agent discovery
and comprehensive monitoring capabilities.
"""

from .nanda_core import StreamlinedAdapter
from .nanda_core.discovery import AgentDiscovery, AgentRanker
from .nanda_core.telemetry import TelemetrySystem

__version__ = "2.0.0"
__author__ = "NANDA Team"
__email__ = "support@nanda.ai"

__all__ = [
    "StreamlinedAdapter",
    "AgentDiscovery",
    "AgentRanker",
    "TelemetrySystem"
]