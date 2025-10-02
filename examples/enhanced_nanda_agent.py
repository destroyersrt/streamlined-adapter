#!/usr/bin/env python3
"""
Enhanced NANDA Agent with Telemetry and Semantic Search

Demonstrates the new features:
- Telemetry system for monitoring
- Semantic search with '?' command
- Enhanced A2A communication
"""

import os
import sys
import time
from typing import Dict, Any, Callable

# Add the parent directory to the path so we can import nanda_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nanda_core.core.adapter import NANDA


def create_data_scientist_agent(agent_id: str, port: int = 6000) -> Callable[[str, str], str]:
    """Create a data scientist agent with enhanced capabilities"""
    
    def data_scientist_logic(message: str, conversation_id: str) -> str:
        """Enhanced data scientist agent logic"""
        message_lower = message.lower()
        
        # Handle different types of data science queries
        if any(word in message_lower for word in ['analyze', 'analysis', 'data']):
            return (
                "I can help you analyze data! I specialize in:\n"
                "📊 Statistical analysis and hypothesis testing\n"
                "🤖 Machine learning model development\n"
                "📈 Data visualization and reporting\n"
                "🔍 Exploratory data analysis\n"
                "What specific analysis do you need?"
            )
        
        elif any(word in message_lower for word in ['python', 'pandas', 'numpy']):
            return (
                "Great! I'm expert in Python data science libraries:\n"
                "🐍 Python: pandas, numpy, scikit-learn\n"
                "📊 Visualization: matplotlib, seaborn, plotly\n"
                "🤖 ML: tensorflow, pytorch, xgboost\n"
                "What Python task can I help with?"
            )
        
        elif any(word in message_lower for word in ['model', 'machine learning', 'ml']):
            return (
                "I can help with machine learning models:\n"
                "🎯 Classification: Random Forest, SVM, Neural Networks\n"
                "📈 Regression: Linear, Polynomial, Ridge, Lasso\n"
                "🔍 Clustering: K-means, DBSCAN, Hierarchical\n"
                "🧠 Deep Learning: CNN, RNN, Transformers\n"
                "What type of model are you building?"
            )
        
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return (
                f"Hello! I'm {agent_id}, your data science specialist. "
                "I can help with data analysis, machine learning, Python programming, "
                "and statistical modeling. What data challenge are you working on?"
            )
        
        else:
            return (
                f"As a data scientist, I can help with:\n"
                "• Data analysis and statistical testing\n"
                "• Machine learning model development\n"
                "• Python programming (pandas, numpy, scikit-learn)\n"
                "• Data visualization and reporting\n"
                "• Predictive modeling and forecasting\n\n"
                f"Your message: '{message}'\n"
                "How can I apply my data science expertise to help you?"
            )
    
    return data_scientist_logic


def create_business_analyst_agent(agent_id: str, port: int = 6001) -> Callable[[str, str], str]:
    """Create a business analyst agent"""
    
    def business_analyst_logic(message: str, conversation_id: str) -> str:
        """Business analyst agent logic"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['strategy', 'business', 'market']):
            return (
                "I can help with business strategy and analysis:\n"
                "📊 Market research and competitive analysis\n"
                "💼 Business process optimization\n"
                "📈 Financial modeling and forecasting\n"
                "🎯 Strategic planning and roadmaps\n"
                "What business challenge are you facing?"
            )
        
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            return (
                f"Hello! I'm {agent_id}, your business analysis expert. "
                "I specialize in market research, strategic planning, and business optimization. "
                "How can I help grow your business?"
            )
        
        else:
            return (
                f"As a business analyst, I can assist with:\n"
                "• Market research and analysis\n"
                "• Business process improvement\n"
                "• Financial planning and modeling\n"
                "• Strategic planning and execution\n"
                "• Competitive intelligence\n\n"
                f"Your message: '{message}'\n"
                "What business insights do you need?"
            )
    
    return business_analyst_logic


def main():
    """Main function to run the enhanced agent"""
    
    # Configuration
    AGENT_ID = os.getenv("AGENT_ID", "enhanced-data-scientist")
    AGENT_NAME = os.getenv("AGENT_NAME", "Enhanced Data Scientist")
    AGENT_DOMAIN = os.getenv("AGENT_DOMAIN", "data science")
    AGENT_SPECIALIZATION = os.getenv("AGENT_SPECIALIZATION", "AI-powered data scientist with telemetry")
    AGENT_DESCRIPTION = os.getenv("AGENT_DESCRIPTION", "Enhanced data scientist with semantic search and telemetry capabilities")
    AGENT_CAPABILITIES = os.getenv("AGENT_CAPABILITIES", "data analysis,machine learning,Python,statistics,telemetry,semantic search")
    REGISTRY_URL = os.getenv("REGISTRY_URL", "http://capregistry.duckdns.org:6900")
    PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:6000")
    PORT = int(os.getenv("PORT", "6000"))
    
    print("🚀 Enhanced NANDA Agent Starting...")
    print(f"Agent ID: {AGENT_ID}")
    print(f"Agent Name: {AGENT_NAME}")
    print(f"Domain: {AGENT_DOMAIN}")
    print(f"Capabilities: {AGENT_CAPABILITIES}")
    print(f"Registry: {REGISTRY_URL}")
    print(f"Port: {PORT}")
    print("")
    
    # Create agent logic based on agent type
    if "business" in AGENT_ID.lower():
        agent_logic = create_business_analyst_agent(AGENT_ID, PORT)
    else:
        agent_logic = create_data_scientist_agent(AGENT_ID, PORT)
    
    # Create NANDA agent with enhanced features
    nanda = NANDA(
        agent_id=AGENT_ID,
        agent_logic=agent_logic,
        port=PORT,
        registry_url=REGISTRY_URL,
        public_url=PUBLIC_URL,
        enable_telemetry=True  # Enable telemetry by default
    )
    
    print("✨ Enhanced Features Enabled:")
    print("  🔍 Semantic Search: Use '? <query>' to find agents")
    print("  📊 Telemetry: Automatic monitoring and metrics")
    print("  💬 A2A Communication: Use '@agent-id message'")
    print("")
    print("📋 Example Commands:")
    print("  ? Find me a data scientist")
    print("  ? I need help with Python programming")
    print("  @business-analyst Can you help with market research?")
    print("")
    
    try:
        # Start the agent (this will register with registry if configured)
        nanda.start(register=bool(REGISTRY_URL))
    except KeyboardInterrupt:
        print("\n🛑 Agent stopped by user")
    except Exception as e:
        print(f"❌ Error starting agent: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
