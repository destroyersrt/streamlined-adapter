#!/usr/bin/env python3
"""
Enhanced NANDA Agent with Domain-Specific Logic

Modular agent that handles different domains and capability structures via environment variables:
- AGENT_DOMAIN: data_science, web_development, healthcare, finance
- AGENT_STRUCTURE_TYPE: keywords, description, embedding
- AGENT_SYSTEM_PROMPT: Domain-specific system prompt
- AGENT_QUESTIONS: JSON array of domain questions
"""

import os
import sys
import json
import time
from typing import Dict, Any, Callable

# Add the parent directory to the path so we can import nanda_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nanda_core.core.adapter import NANDA


class DomainAgentLogic:
    """Modular domain agent logic based on environment variables"""
    
    def __init__(self):
        # Get configuration from environment variables
        self.agent_id = os.getenv("AGENT_ID", "domain-agent-001")
        self.agent_name = os.getenv("AGENT_NAME", "Domain Agent")
        self.domain = os.getenv("AGENT_DOMAIN", "general")
        self.structure_type = os.getenv("AGENT_STRUCTURE_TYPE", "keywords")
        self.specialization = os.getenv("AGENT_SPECIALIZATION", "General Expert")
        self.description = os.getenv("AGENT_DESCRIPTION", "General purpose agent")
        self.capabilities = os.getenv("AGENT_CAPABILITIES", "").split(",")
        self.system_prompt = os.getenv("AGENT_SYSTEM_PROMPT", "You are a helpful AI assistant.")
        
        # Parse questions from JSON
        questions_json = os.getenv("AGENT_QUESTIONS", "[]")
        try:
            self.questions = json.loads(questions_json)
        except json.JSONDecodeError:
            self.questions = []
        
        # Domain-specific knowledge bases
        self.knowledge_bases = {
            "data_science": {
                "anomaly_detection": "For time series anomaly detection, I recommend using isolation forests, LSTM autoencoders, or statistical methods like Z-score and IQR. The choice depends on your data characteristics and real-time requirements.",
                "bagging_vs_boosting": "Bagging (Bootstrap Aggregating) trains models in parallel on different subsets and averages predictions, reducing variance. Boosting trains models sequentially, each correcting previous errors, reducing bias. Random Forest uses bagging, while XGBoost uses boosting.",
                "missing_values": "For large datasets with missing values, consider: 1) Analyze missingness patterns (MCAR, MAR, MNAR), 2) Use imputation techniques like KNN, MICE, or domain-specific methods, 3) Consider missingness as a feature, 4) Use algorithms that handle missing values natively like XGBoost.",
                "ai_ethics": "Key ethical considerations in AI deployment include: bias and fairness, transparency and explainability, privacy protection, accountability, human oversight, and continuous monitoring for unintended consequences. Always conduct bias audits and implement fairness metrics.",
                "nlp_deep_learning": "For NLP projects, I've used transformer architectures like BERT for text classification, GPT for generation, and T5 for text-to-text tasks. Key considerations include tokenization, attention mechanisms, fine-tuning strategies, and handling domain-specific vocabulary."
            },
            "web_development": {
                "react_optimization": "To optimize React applications: 1) Use React.memo() for component memoization, 2) Implement useMemo() and useCallback() for expensive calculations, 3) Code splitting with React.lazy() and Suspense, 4) Optimize bundle size with tree shaking, 5) Use React DevTools Profiler to identify bottlenecks.",
                "serverless_architecture": "Serverless architecture in web development involves using cloud functions (AWS Lambda, Vercel Functions) for backend logic. Benefits include automatic scaling, pay-per-use pricing, and reduced infrastructure management. Consider cold starts, vendor lock-in, and debugging challenges.",
                "api_security": "RESTful API security best practices: 1) Use HTTPS everywhere, 2) Implement proper authentication (JWT, OAuth), 3) Input validation and sanitization, 4) Rate limiting and throttling, 5) CORS configuration, 6) SQL injection prevention, 7) Regular security audits and dependency updates.",
                "cicd_webapp": "For web app CI/CD: 1) Use Git workflows (feature branches, pull requests), 2) Automated testing (unit, integration, e2e), 3) Build automation (webpack, Vite), 4) Deployment pipelines (GitHub Actions, GitLab CI), 5) Environment management (staging, production), 6) Monitoring and rollback strategies.",
                "state_management": "For complex front-end state management: 1) Redux Toolkit for predictable state updates, 2) Zustand for simpler state needs, 3) React Query for server state, 4) Context API for component tree state, 5) Consider state colocation and avoid over-engineering."
            },
            "healthcare": {
                "early_detection": "AI assists in early disease detection through: 1) Medical imaging analysis (CT, MRI, X-ray) using deep learning, 2) Pattern recognition in lab results and vital signs, 3) Predictive modeling for risk assessment, 4) Continuous monitoring with wearable devices, 5) Natural language processing of clinical notes for symptom identification.",
                "ai_integration_challenges": "Key challenges in healthcare AI integration: 1) Regulatory compliance (FDA, HIPAA), 2) Interoperability with existing EHR systems, 3) Clinical workflow integration, 4) Staff training and adoption, 5) Data quality and standardization, 6) Cost-benefit analysis, 7) Maintaining human oversight and clinical judgment.",
                "patient_privacy": "Patient data privacy in AI requires: 1) HIPAA compliance and data encryption, 2) De-identification and anonymization techniques, 3) Federated learning to avoid centralized data storage, 4) Access controls and audit trails, 5) Consent management systems, 6) Regular security assessments, 7) Transparent data usage policies.",
                "hospital_ai_outcomes": "AI improves hospital outcomes through: 1) Predictive analytics for patient deterioration (sepsis, cardiac events), 2) Optimized resource allocation and bed management, 3) Clinical decision support systems, 4) Automated medication reconciliation, 5) Reduced diagnostic errors through second opinions, 6) Streamlined administrative processes.",
                "ai_medical_reliability": "Ensuring AI medical recommendation reliability: 1) Rigorous clinical validation and trials, 2) Continuous monitoring and performance metrics, 3) Human-in-the-loop verification, 4) Explainable AI for clinical transparency, 5) Regular model updates with new data, 6) Bias detection and mitigation, 7) Clear limitations and contraindications."
            },
            "finance": {
                "portfolio_diversification": "Key factors for diversified portfolios: 1) Asset class allocation (stocks, bonds, commodities, REITs), 2) Geographic diversification (domestic vs international), 3) Sector diversification, 4) Market cap diversification (large, mid, small cap), 5) Time diversification (dollar-cost averaging), 6) Risk tolerance alignment, 7) Regular rebalancing.",
                "interest_rates_bonds": "Interest rate changes have inverse relationship with bond prices: 1) Rising rates decrease existing bond values, 2) Falling rates increase bond values, 3) Duration measures price sensitivity to rate changes, 4) Longer-term bonds more sensitive than short-term, 5) Credit quality affects sensitivity, 6) Consider laddering strategies for rate risk management.",
                "investment_risk_assessment": "Investment risk assessment involves: 1) Fundamental analysis (financial statements, competitive position), 2) Technical analysis (price trends, volume patterns), 3) Macroeconomic factors (interest rates, inflation, GDP), 4) Industry and sector analysis, 5) Liquidity risk evaluation, 6) Correlation with existing holdings, 7) Stress testing under different scenarios.",
                "algorithmic_trading": "Algorithmic trading in modern markets: 1) High-frequency trading for market making, 2) Statistical arbitrage strategies, 3) Trend following and momentum strategies, 4) Mean reversion algorithms, 5) Risk management and position sizing, 6) Market impact considerations, 7) Regulatory compliance and best execution requirements.",
                "economic_trends_impact": "Global economic trends affect local investments through: 1) Currency exchange rate fluctuations, 2) Trade policy and tariff impacts, 3) Interest rate differentials, 4) Commodity price movements, 5) Supply chain disruptions, 6) Capital flow patterns, 7) Geopolitical risk considerations."
            }
        }
        
        print(f"🤖 Initialized {self.domain.replace('_', ' ').title()} Agent ({self.structure_type})")
        print(f"   Agent ID: {self.agent_id}")
        print(f"   Specialization: {self.specialization}")
    
    def get_domain_knowledge(self) -> Dict[str, str]:
        """Get domain-specific knowledge base"""
        return self.knowledge_bases.get(self.domain, {})
    
    def agent_logic(self, message: str, conversation_id: str) -> str:
        """Process incoming messages with domain-specific logic"""
        message_lower = message.lower()
        knowledge = self.get_domain_knowledge()
        
        # Domain-specific question handling
        if self.domain == "data_science":
            return self._handle_data_science_questions(message_lower, knowledge)
        elif self.domain == "web_development":
            return self._handle_web_development_questions(message_lower, knowledge)
        elif self.domain == "healthcare":
            return self._handle_healthcare_questions(message_lower, knowledge)
        elif self.domain == "finance":
            return self._handle_finance_questions(message_lower, knowledge)
        else:
            return self._handle_general_questions(message_lower)
    
    def _handle_data_science_questions(self, message_lower: str, knowledge: Dict[str, str]) -> str:
        """Handle data science domain questions"""
        domain_emoji = "🔬"
        
        if "anomaly detection" in message_lower or "time series" in message_lower:
            return f"{domain_emoji} Data Science Expert ({self.structure_type}): {knowledge.get('anomaly_detection', 'I can help with anomaly detection techniques.')}"
        elif "bagging" in message_lower and "boosting" in message_lower:
            return f"{domain_emoji} Data Science Expert ({self.structure_type}): {knowledge.get('bagging_vs_boosting', 'I can explain ensemble methods.')}"
        elif "missing values" in message_lower or "missing data" in message_lower:
            return f"{domain_emoji} Data Science Expert ({self.structure_type}): {knowledge.get('missing_values', 'I can help with missing data strategies.')}"
        elif "ethical" in message_lower or "ethics" in message_lower or "bias" in message_lower:
            return f"{domain_emoji} Data Science Expert ({self.structure_type}): {knowledge.get('ai_ethics', 'I can discuss AI ethics and bias.')}"
        elif "nlp" in message_lower or "natural language" in message_lower or "deep learning" in message_lower:
            return f"{domain_emoji} Data Science Expert ({self.structure_type}): {knowledge.get('nlp_deep_learning', 'I can help with NLP and deep learning.')}"
        else:
            return f"{domain_emoji} Data Science Expert ({self.structure_type}): I specialize in data science and machine learning using {self.structure_type}-based capabilities. I can help with statistical analysis, predictive modeling, feature engineering, model evaluation, and ML deployment. What specific data science challenge are you working on?"
    
    def _handle_web_development_questions(self, message_lower: str, knowledge: Dict[str, str]) -> str:
        """Handle web development domain questions"""
        domain_emoji = "💻"
        
        if "react" in message_lower and ("optimize" in message_lower or "performance" in message_lower):
            return f"{domain_emoji} Web Dev Expert ({self.structure_type}): {knowledge.get('react_optimization', 'I can help optimize React applications.')}"
        elif "serverless" in message_lower or "serverless architecture" in message_lower:
            return f"{domain_emoji} Web Dev Expert ({self.structure_type}): {knowledge.get('serverless_architecture', 'I can explain serverless architecture.')}"
        elif "security" in message_lower and ("api" in message_lower or "restful" in message_lower):
            return f"{domain_emoji} Web Dev Expert ({self.structure_type}): {knowledge.get('api_security', 'I can help with API security best practices.')}"
        elif "ci/cd" in message_lower or "continuous integration" in message_lower or "deployment" in message_lower:
            return f"{domain_emoji} Web Dev Expert ({self.structure_type}): {knowledge.get('cicd_webapp', 'I can help with CI/CD for web applications.')}"
        elif "state management" in message_lower or ("state" in message_lower and "front" in message_lower):
            return f"{domain_emoji} Web Dev Expert ({self.structure_type}): {knowledge.get('state_management', 'I can help with front-end state management.')}"
        else:
            return f"{domain_emoji} Web Dev Expert ({self.structure_type}): I specialize in full-stack web development using {self.structure_type}-based capabilities. I can help with React, Node.js, API design, database integration, performance optimization, security, and deployment. What web development challenge are you facing?"
    
    def _handle_healthcare_questions(self, message_lower: str, knowledge: Dict[str, str]) -> str:
        """Handle healthcare domain questions"""
        domain_emoji = "🏥"
        
        if "early" in message_lower and "detection" in message_lower:
            return f"{domain_emoji} Healthcare Expert ({self.structure_type}): {knowledge.get('early_detection', 'I can help with AI-assisted early disease detection.')}"
        elif "integration" in message_lower and ("healthcare" in message_lower or "hospital" in message_lower):
            return f"{domain_emoji} Healthcare Expert ({self.structure_type}): {knowledge.get('ai_integration_challenges', 'I can discuss healthcare AI integration challenges.')}"
        elif "privacy" in message_lower and ("patient" in message_lower or "data" in message_lower):
            return f"{domain_emoji} Healthcare Expert ({self.structure_type}): {knowledge.get('patient_privacy', 'I can help with patient data privacy in AI.')}"
        elif "hospital" in message_lower and ("outcomes" in message_lower or "improve" in message_lower):
            return f"{domain_emoji} Healthcare Expert ({self.structure_type}): {knowledge.get('hospital_ai_outcomes', 'I can explain how AI improves hospital outcomes.')}"
        elif "reliability" in message_lower or "accuracy" in message_lower or "medical recommendation" in message_lower:
            return f"{domain_emoji} Healthcare Expert ({self.structure_type}): {knowledge.get('ai_medical_reliability', 'I can discuss AI medical recommendation reliability.')}"
        else:
            return f"{domain_emoji} Healthcare Expert ({self.structure_type}): I specialize in healthcare AI and medical systems using {self.structure_type}-based capabilities. I can help with medical diagnosis support, patient data analysis, clinical workflow optimization, healthcare technology integration, and medical ethics. What healthcare challenge are you addressing?"
    
    def _handle_finance_questions(self, message_lower: str, knowledge: Dict[str, str]) -> str:
        """Handle finance domain questions"""
        domain_emoji = "💰"
        
        if "portfolio" in message_lower and "diversif" in message_lower:
            return f"{domain_emoji} Finance Expert ({self.structure_type}): {knowledge.get('portfolio_diversification', 'I can help with portfolio diversification strategies.')}"
        elif "interest rate" in message_lower and "bond" in message_lower:
            return f"{domain_emoji} Finance Expert ({self.structure_type}): {knowledge.get('interest_rates_bonds', 'I can explain interest rate impacts on bonds.')}"
        elif "risk" in message_lower and ("assess" in message_lower or "investment" in message_lower):
            return f"{domain_emoji} Finance Expert ({self.structure_type}): {knowledge.get('investment_risk_assessment', 'I can help with investment risk assessment.')}"
        elif "algorithmic trading" in message_lower or "algo trading" in message_lower:
            return f"{domain_emoji} Finance Expert ({self.structure_type}): {knowledge.get('algorithmic_trading', 'I can discuss algorithmic trading in modern markets.')}"
        elif "economic trends" in message_lower or ("global" in message_lower and "investment" in message_lower):
            return f"{domain_emoji} Finance Expert ({self.structure_type}): {knowledge.get('economic_trends_impact', 'I can explain how economic trends affect investments.')}"
        else:
            return f"{domain_emoji} Finance Expert ({self.structure_type}): I specialize in financial planning and investment strategies using {self.structure_type}-based capabilities. I can help with portfolio management, market analysis, risk assessment, investment planning, and economic forecasting. What financial challenge can I assist with?"
    
    def _handle_general_questions(self, message_lower: str) -> str:
        """Handle general questions for unknown domains"""
        return f"🤖 {self.specialization} ({self.structure_type}): Hello! I'm a {self.domain.replace('_', ' ')} specialist using {self.structure_type}-based capabilities. How can I help you today?"


def create_domain_agent_logic() -> Callable[[str, str], str]:
    """Create domain agent logic based on environment variables"""
    domain_logic = DomainAgentLogic()
    return domain_logic.agent_logic


def main():
    """Main function to run the domain agent"""
    
    # Get agent configuration from environment variables
    agent_id = os.getenv("AGENT_ID", "domain-agent-001")
    port = int(os.getenv("PORT", "6000"))
    registry_url = os.getenv("REGISTRY_URL", "http://capregistry.duckdns.org:6900")
    
    # Get domain-specific configuration
    domain = os.getenv("AGENT_DOMAIN", "general")
    structure_type = os.getenv("AGENT_STRUCTURE_TYPE", "keywords")
    specialization = os.getenv("AGENT_SPECIALIZATION", "General Expert")
    description = os.getenv("AGENT_DESCRIPTION", "General purpose agent")
    capabilities = os.getenv("AGENT_CAPABILITIES", "").split(",")
    
    print(f"🚀 Starting Domain Agent: {agent_id}")
    print(f"📊 Domain: {domain}")
    print(f"🏗️ Structure Type: {structure_type}")
    print(f"🔌 Port: {port}")
    print(f"🌐 Registry: {registry_url}")
    print("")
    
    # Create the domain agent logic
    agent_logic = create_domain_agent_logic()
    
    # Create and start the NANDA agent
    nanda = NANDA(
        agent_id=agent_id,
        agent_logic=agent_logic,
        port=port,
        registry_url=registry_url
    )
    
    # Add domain-specific metadata for registration
    nanda.metadata = {
        "domain": domain,
        "specialization": specialization,
        "structure_type": structure_type,
        "description": description,
        "capabilities": {
            "technical_skills": capabilities,
            "search_method": f"{structure_type}_match",
            "domains": [domain]
        },
        "tags": [domain.replace("_", "-"), structure_type, "domain-expert"]
    }
    
    print(f"🎯 Agent ready to serve {domain.replace('_', ' ')} expertise using {structure_type} capabilities!")
    nanda.run()


if __name__ == "__main__":
    main()
