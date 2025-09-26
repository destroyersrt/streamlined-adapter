#!/usr/bin/env python3
"""
Modular NANDA Agent Template

This template makes it easy to create agents with different personalities and expertise
by simply changing the AGENT_CONFIG section.
"""
import os
import sys
import time
from datetime import datetime

# Add the parent directory to the path to allow importing streamlined_adapter
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from nanda_core.core.adapter import NANDA

# =============================================================================
# AGENT CONFIGURATION - Customize this section for different agents
# =============================================================================

AGENT_CONFIG = {
    "agent_id": "helpful-ubuntu-agent",
    "agent_name": "Ubuntu Helper",
    "personality": "helpful and friendly",
    "expertise": [
        "general assistance",
        "time information", 
        "basic calculations",
        "casual conversation"
    ],
    "greeting_responses": [
        "Hello! I'm {agent_name}, a {personality} agent running on Ubuntu 22.04.",
        "Hi there! I'm {agent_name} and I'm here to help.",
        "Hey! {agent_name} at your service. How can I assist you today?"
    ],
    "about_response": "I am {agent_name}, a NANDA agent running on Ubuntu 22.04 with Python 3.12. I specialize in {expertise_list} and I'm {personality}. I'm here to help with whatever you need!",
    "casual_responses": {
        "wassup": "Not much! Just running here on this Ubuntu server, ready to help. What about you?",
        "how are you": "I'm doing great! Running smoothly and ready to assist. How are you doing?",
        "what's up": "Just here helping people! What can I do for you?"
    },
    "help_response": "I can help with: {expertise_list}. Just ask me anything!",
    "fallback_response": "I received: \"{message}\". I can help with {expertise_list}. What would you like to know?"
}

# Port configuration
PORT = 6000

# =============================================================================
# MODULAR AGENT LOGIC - This handles the personality and expertise
# =============================================================================

def create_agent_logic(config):
    """
    Creates an agent logic function based on the provided configuration.
    This makes it easy to create different agent personalities.
    """
    
    def agent_logic(message: str, conversation_id: str) -> str:
        """Dynamic agent logic based on configuration"""
        msg = message.lower().strip()
        
        # Handle greetings
        if any(greeting in msg for greeting in ['hello', 'hi', 'hey']):
            import random
            response = random.choice(config["greeting_responses"])
            return response.format(
                agent_name=config["agent_name"],
                personality=config["personality"]
            )
        
        # Handle "about yourself" questions
        elif any(phrase in msg for phrase in ['about yourself', 'about you', 'who are you']):
            expertise_list = ", ".join(config["expertise"])
            return config["about_response"].format(
                agent_name=config["agent_name"],
                personality=config["personality"],
                expertise_list=expertise_list
            )
        
        # Handle time requests
        elif 'time' in msg:
            current_time = datetime.now().strftime("%H:%M:%S")
            return f"The current time is {current_time}."
        
        # Handle casual conversation
        elif msg in config["casual_responses"]:
            return config["casual_responses"][msg]
        
        # Handle help requests
        elif 'help' in msg:
            expertise_list = ", ".join(config["expertise"])
            return config["help_response"].format(expertise_list=expertise_list)
        
        # Handle basic calculations
        elif any(op in message for op in ['+', '-', '*', '/', '=']):
            try:
                # Simple calculation (be careful with eval in production!)
                calculation = message.replace('x', '*').replace('X', '*').replace('=', '').strip()
                result = eval(calculation)
                return f"Calculation result: {calculation} = {result}"
            except:
                return "Sorry, I couldn't calculate that. Please check your expression."
        
        # Fallback response
        else:
            expertise_list = ", ".join(config["expertise"])
            return config["fallback_response"].format(
                message=message,
                expertise_list=expertise_list
            )
    
    return agent_logic

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Main function to start the modular agent"""
    print(f"🤖 Starting {AGENT_CONFIG['agent_name']}")
    print(f"📝 Personality: {AGENT_CONFIG['personality']}")
    print(f"🎯 Expertise: {', '.join(AGENT_CONFIG['expertise'])}")
    
    # Create the agent logic based on configuration
    agent_logic = create_agent_logic(AGENT_CONFIG)
    
    # Create and start the NANDA agent
    nanda = NANDA(
        agent_id=AGENT_CONFIG["agent_id"],
        agent_logic=agent_logic,
        port=PORT,
        enable_telemetry=False
    )
    
    print(f"🚀 Agent URL: http://localhost:{PORT}/a2a")
    print("💡 Try these messages:")
    print("   - 'Hello there'")
    print("   - 'Tell me about yourself'")
    print("   - 'What time is it?'")
    print("   - 'wassup'")
    print("   - '5 + 3'")
    print("   - 'help'")
    print("\n🛑 Press Ctrl+C to stop")
    
    # Start the agent
    nanda.start()

def create_custom_agent(agent_name, personality, expertise_list, port=6000):
    """
    Helper function to quickly create a custom agent with different config
    
    Example usage:
        create_custom_agent(
            agent_name="Data Scientist", 
            personality="analytical and precise",
            expertise_list=["data analysis", "statistics", "machine learning", "Python"],
            port=6001
        )
    """
    custom_config = AGENT_CONFIG.copy()
    custom_config.update({
        "agent_id": agent_name.lower().replace(" ", "-"),
        "agent_name": agent_name,
        "personality": personality,
        "expertise": expertise_list
    })
    
    agent_logic = create_agent_logic(custom_config)
    
    nanda = NANDA(
        agent_id=custom_config["agent_id"],
        agent_logic=agent_logic,
        port=port,
        enable_telemetry=False
    )
    
    print(f"🤖 Starting custom agent: {agent_name}")
    print(f"🚀 Agent URL: http://localhost:{port}/a2a")
    nanda.start()

if __name__ == "__main__":
    main()
