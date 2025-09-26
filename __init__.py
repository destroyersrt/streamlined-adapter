#!/usr/bin/env python3
"""
Streamlined NANDA Adapter - Efficient AI Agent Communication System

A clean, feature-rich adapter that maintains full functionality parity with the original
while eliminating unnecessary query preprocessing and adding intelligent agent discovery
and comprehensive monitoring capabilities.
"""

from .nanda_core.core.adapter import NANDA, StreamlinedAdapter
from .nanda_core.core.adapter import echo_agent, pirate_agent, helpful_agent

__version__ = "2.0.0"
__author__ = "NANDA Team"
__email__ = "support@nanda.ai"

__all__ = [
    "NANDA",           # Main class
    "StreamlinedAdapter",  # Alias
    "echo_agent",      # Example agents
    "pirate_agent", 
    "helpful_agent"
]