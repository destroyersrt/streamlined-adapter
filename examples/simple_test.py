#!/usr/bin/env python3
"""
Simple NANDA Test - Create and test an agent in just a few lines
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from nanda_core.core.adapter import NANDA, helpful_agent

def main():
    # Create agent in just 6 lines!
    nanda = NANDA(
        agent_id="simple_test_agent",
        agent_logic=helpful_agent,
        port=6005
    )
    
    print("🧪 Simple test agent created")
    print("📝 Try these commands once started:")
    print("   - Send: 'Hello agent'")
    print("   - Send: 'What time is it?'") 
    print("   - Send: '5 + 3'")
    print("   - Send: '/help'")
    print("   - Send: '/ping'")
    print("   - Send: '@other_agent Hello there'")
    
    nanda.start(register=False)

if __name__ == "__main__":
    main()

