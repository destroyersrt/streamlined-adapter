#!/usr/bin/env python3
"""
Healthcare Domain Agent

This agent specializes in medical diagnosis, patient data analysis, and treatment recommendations.
It can answer domain-specific questions about healthcare AI, medical systems, and patient care.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import nanda_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nanda_core.core.adapter import NANDA

class HealthcareAgent:
    """Healthcare domain expert agent"""
    
    def __init__(self, agent_id: str, structure_type: str):
        self.agent_id = agent_id
        self.structure_type = structure_type
        
        # Domain-specific knowledge base
        self.knowledge_base = {
            "early_detection": "AI assists in early disease detection through: 1) Medical imaging analysis (CT, MRI, X-ray) using deep learning, 2) Pattern recognition in lab results and vital signs, 3) Predictive modeling for risk assessment, 4) Continuous monitoring with wearable devices, 5) Natural language processing of clinical notes for symptom identification.",
            
            "ai_integration_challenges": "Key challenges in healthcare AI integration: 1) Regulatory compliance (FDA, HIPAA), 2) Interoperability with existing EHR systems, 3) Clinical workflow integration, 4) Staff training and adoption, 5) Data quality and standardization, 6) Cost-benefit analysis, 7) Maintaining human oversight and clinical judgment.",
            
            "patient_privacy": "Patient data privacy in AI requires: 1) HIPAA compliance and data encryption, 2) De-identification and anonymization techniques, 3) Federated learning to avoid centralized data storage, 4) Access controls and audit trails, 5) Consent management systems, 6) Regular security assessments, 7) Transparent data usage policies.",
            
            "hospital_ai_outcomes": "AI improves hospital outcomes through: 1) Predictive analytics for patient deterioration (sepsis, cardiac events), 2) Optimized resource allocation and bed management, 3) Clinical decision support systems, 4) Automated medication reconciliation, 5) Reduced diagnostic errors through second opinions, 6) Streamlined administrative processes.",
            
            "ai_medical_reliability": "Ensuring AI medical recommendation reliability: 1) Rigorous clinical validation and trials, 2) Continuous monitoring and performance metrics, 3) Human-in-the-loop verification, 4) Explainable AI for clinical transparency, 5) Regular model updates with new data, 6) Bias detection and mitigation, 7) Clear limitations and contraindications."
        }
        
        # Capability structure based on type
        if structure_type == "keywords":
            self.capabilities = {
                "keywords": ["healthcare", "medical diagnosis", "patient care", "ehr", "telemedicine", "biotech"],
                "search_method": "keyword_match"
            }
        elif structure_type == "description":
            self.capabilities = {
                "description_text": "AI assistant specializing in medical diagnosis, patient data analysis, and treatment recommendations. Expert in healthcare technology integration and clinical decision support systems.",
                "search_method": "text_search"
            }
        elif structure_type == "embedding":
            self.capabilities = {
                "description_text": "Comprehensive healthcare AI specialist with deep expertise in medical diagnosis systems, patient data analytics, clinical workflow optimization, healthcare technology integration, medical ethics, and regulatory compliance in healthcare environments.",
                "search_method": "embedding_search"
            }
    
    def agent_logic(self, message: str, conversation_id: str) -> str:
        """Process incoming messages and provide healthcare expertise"""
        
        message_lower = message.lower()
        
        # Handle domain-specific questions
        if "early" in message_lower and "detection" in message_lower:
            return f"🏥 Healthcare Expert ({self.structure_type}): {self.knowledge_base['early_detection']}"
        
        elif "integration" in message_lower and ("healthcare" in message_lower or "hospital" in message_lower):
            return f"🏥 Healthcare Expert ({self.structure_type}): {self.knowledge_base['ai_integration_challenges']}"
        
        elif "privacy" in message_lower and ("patient" in message_lower or "data" in message_lower):
            return f"🏥 Healthcare Expert ({self.structure_type}): {self.knowledge_base['patient_privacy']}"
        
        elif "hospital" in message_lower and ("outcomes" in message_lower or "improve" in message_lower):
            return f"🏥 Healthcare Expert ({self.structure_type}): {self.knowledge_base['hospital_ai_outcomes']}"
        
        elif "reliability" in message_lower or "accuracy" in message_lower or "medical recommendation" in message_lower:
            return f"🏥 Healthcare Expert ({self.structure_type}): {self.knowledge_base['ai_medical_reliability']}"
        
        # General healthcare response
        elif any(keyword in message_lower for keyword in ["medical", "healthcare", "patient", "diagnosis", "treatment", "clinical", "hospital", "ehr"]):
            return f"🏥 Healthcare Expert ({self.structure_type}): I specialize in healthcare AI and medical systems. I can help with medical diagnosis support, patient data analysis, clinical workflow optimization, healthcare technology integration, and medical ethics. What healthcare challenge are you addressing?"
        
        # Default response
        return f"🏥 Healthcare Expert ({self.structure_type}): Hello! I'm a healthcare AI specialist. I can assist with medical diagnosis systems, patient data analytics, clinical decision support, and healthcare technology integration. How can I help with your healthcare project?"

def main():
    """Main function to run the healthcare agent"""
    
    # Get agent configuration from environment or command line
    agent_id = os.getenv("AGENT_ID", "healthcare-agent-001")
    structure_type = os.getenv("STRUCTURE_TYPE", "keywords")  # keywords, description, or embedding
    port = int(os.getenv("PORT", "6000"))
    
    print(f"🚀 Starting Healthcare Agent: {agent_id}")
    print(f"📊 Structure Type: {structure_type}")
    print(f"🔌 Port: {port}")
    
    # Create the domain agent
    domain_agent = HealthcareAgent(agent_id, structure_type)
    
    # Create and start the NANDA agent
    nanda = NANDA(
        agent_id=agent_id,
        agent_logic=domain_agent.agent_logic,
        port=port,
        registry_url="http://capregistry.duckdns.org:6900"
    )
    
    # Add domain-specific metadata for registration
    nanda.metadata = {
        "domain": "healthcare",
        "specialization": "Healthcare AI and Medical Systems",
        "capabilities": domain_agent.capabilities,
        "structure_type": structure_type,
        "description": f"AI assistant specializing in medical diagnosis, patient data analysis, and treatment recommendations. ({structure_type} structure)",
        "tags": ["healthcare", "medical-diagnosis", "patient-care", "ehr", "telemedicine", "biotech"]
    }
    
    print(f"🎯 Agent ready to serve healthcare expertise!")
    nanda.run()

if __name__ == "__main__":
    main()
