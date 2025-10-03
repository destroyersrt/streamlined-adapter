#!/usr/bin/env python3
"""
Data Science Domain Agent

This agent specializes in data science, machine learning, and statistical analysis.
It can answer domain-specific questions about data analysis, ML algorithms, and statistics.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import nanda_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nanda_core.core.adapter import NANDA

class DataScienceAgent:
    """Data Science domain expert agent"""
    
    def __init__(self, agent_id: str, structure_type: str):
        self.agent_id = agent_id
        self.structure_type = structure_type
        
        # Domain-specific knowledge base
        self.knowledge_base = {
            "anomaly_detection": "For time series anomaly detection, I recommend using isolation forests, LSTM autoencoders, or statistical methods like Z-score and IQR. The choice depends on your data characteristics and real-time requirements.",
            
            "bagging_vs_boosting": "Bagging (Bootstrap Aggregating) trains models in parallel on different subsets and averages predictions, reducing variance. Boosting trains models sequentially, each correcting previous errors, reducing bias. Random Forest uses bagging, while XGBoost uses boosting.",
            
            "missing_values": "For large datasets with missing values, consider: 1) Analyze missingness patterns (MCAR, MAR, MNAR), 2) Use imputation techniques like KNN, MICE, or domain-specific methods, 3) Consider missingness as a feature, 4) Use algorithms that handle missing values natively like XGBoost.",
            
            "ai_ethics": "Key ethical considerations in AI deployment include: bias and fairness, transparency and explainability, privacy protection, accountability, human oversight, and continuous monitoring for unintended consequences. Always conduct bias audits and implement fairness metrics.",
            
            "nlp_deep_learning": "For NLP projects, I've used transformer architectures like BERT for text classification, GPT for generation, and T5 for text-to-text tasks. Key considerations include tokenization, attention mechanisms, fine-tuning strategies, and handling domain-specific vocabulary."
        }
        
        # Capability structure based on type
        if structure_type == "keywords":
            self.capabilities = {
                "keywords": ["data science", "machine learning", "statistics", "python", "r", "analysis"],
                "search_method": "keyword_match"
            }
        elif structure_type == "description":
            self.capabilities = {
                "description_text": "Expert in data science, machine learning, and statistical analysis. Specializes in predictive modeling, data preprocessing, feature engineering, model evaluation, and deployment of ML systems in production environments.",
                "search_method": "text_search"
            }
        elif structure_type == "embedding":
            self.capabilities = {
                "description_text": "Comprehensive data science expert with deep knowledge in machine learning algorithms, statistical analysis, data visualization, and AI ethics. Experienced in end-to-end ML pipeline development from data collection to model deployment and monitoring.",
                "search_method": "embedding_search"
            }
    
    def agent_logic(self, message: str, conversation_id: str) -> str:
        """Process incoming messages and provide data science expertise"""
        
        message_lower = message.lower()
        
        # Handle domain-specific questions
        if "anomaly detection" in message_lower or "time series" in message_lower:
            return f"🔬 Data Science Expert ({self.structure_type}): {self.knowledge_base['anomaly_detection']}"
        
        elif "bagging" in message_lower and "boosting" in message_lower:
            return f"🔬 Data Science Expert ({self.structure_type}): {self.knowledge_base['bagging_vs_boosting']}"
        
        elif "missing values" in message_lower or "missing data" in message_lower:
            return f"🔬 Data Science Expert ({self.structure_type}): {self.knowledge_base['missing_values']}"
        
        elif "ethical" in message_lower or "ethics" in message_lower or "bias" in message_lower:
            return f"🔬 Data Science Expert ({self.structure_type}): {self.knowledge_base['ai_ethics']}"
        
        elif "nlp" in message_lower or "natural language" in message_lower or "deep learning" in message_lower:
            return f"🔬 Data Science Expert ({self.structure_type}): {self.knowledge_base['nlp_deep_learning']}"
        
        # General data science response
        elif any(keyword in message_lower for keyword in ["data", "machine learning", "ml", "statistics", "analysis", "model"]):
            return f"🔬 Data Science Expert ({self.structure_type}): I specialize in data science and machine learning. I can help with statistical analysis, predictive modeling, feature engineering, model evaluation, and ML deployment. What specific data science challenge are you working on?"
        
        # Default response
        return f"🔬 Data Science Expert ({self.structure_type}): Hello! I'm a data science specialist. I can help with machine learning, statistical analysis, data preprocessing, model development, and AI ethics. How can I assist you with your data science needs?"

def main():
    """Main function to run the data science agent"""
    
    # Get agent configuration from environment or command line
    agent_id = os.getenv("AGENT_ID", "data-science-agent-001")
    structure_type = os.getenv("STRUCTURE_TYPE", "keywords")  # keywords, description, or embedding
    port = int(os.getenv("PORT", "6000"))
    
    print(f"🚀 Starting Data Science Agent: {agent_id}")
    print(f"📊 Structure Type: {structure_type}")
    print(f"🔌 Port: {port}")
    
    # Create the domain agent
    domain_agent = DataScienceAgent(agent_id, structure_type)
    
    # Create and start the NANDA agent
    nanda = NANDA(
        agent_id=agent_id,
        agent_logic=domain_agent.agent_logic,
        port=port,
        registry_url="http://capregistry.duckdns.org:6900"
    )
    
    # Add domain-specific metadata for registration
    nanda.metadata = {
        "domain": "data_science",
        "specialization": "Data Science and Machine Learning",
        "capabilities": domain_agent.capabilities,
        "structure_type": structure_type,
        "description": f"Expert in data science, machine learning, and statistical analysis. ({structure_type} structure)",
        "tags": ["data-science", "machine-learning", "statistics", "python", "analysis"]
    }
    
    print(f"🎯 Agent ready to serve data science expertise!")
    nanda.run()

if __name__ == "__main__":
    main()
