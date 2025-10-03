#!/usr/bin/env python3
"""
Create 60 Test Agents for Capability Structure Testing
4 Topics × 3 Structures × 5 Agents = 60 Total Agents
"""

import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts

class TestAgentCreator:
    def __init__(self):
        self.mongodb_facts = MongoDBAgentFacts()
        
        # Define 4 topics/domains
        self.topics = {
            "data_science": {
                "name": "Data Science",
                "description": "Expert in data analysis, machine learning, and statistical modeling",
                "keywords": ["data", "analysis", "machine_learning", "statistics", "python", "pandas", "numpy", "visualization"],
                "capabilities": ["data_analysis", "machine_learning", "statistical_modeling", "data_visualization", "python_programming"],
                "tools": ["python", "pandas", "numpy", "scikit_learn", "matplotlib", "jupyter"],
                "questions": [
                    "How would you approach cleaning a dataset with missing values?",
                    "What machine learning algorithm would you recommend for predicting customer churn?",
                    "How do you handle overfitting in machine learning models?",
                    "What's the best way to visualize time series data?",
                    "How would you evaluate the performance of a classification model?"
                ]
            },
            "web_development": {
                "name": "Web Development", 
                "description": "Expert in building modern web applications and user interfaces",
                "keywords": ["web", "development", "javascript", "react", "node", "html", "css", "frontend", "backend"],
                "capabilities": ["frontend_development", "backend_development", "javascript_programming", "react_development", "api_design"],
                "tools": ["javascript", "react", "nodejs", "html", "css", "webpack", "git"],
                "questions": [
                    "How would you optimize the performance of a React application?",
                    "What's the best approach for handling state management in a large React app?",
                    "How do you implement user authentication in a Node.js application?",
                    "What are the key principles of responsive web design?",
                    "How would you structure a RESTful API for an e-commerce platform?"
                ]
            },
            "healthcare": {
                "name": "Healthcare",
                "description": "Expert in medical knowledge, patient care, and healthcare systems",
                "keywords": ["healthcare", "medical", "patient", "diagnosis", "treatment", "clinical", "medicine", "health"],
                "capabilities": ["medical_diagnosis", "patient_care", "clinical_analysis", "healthcare_systems", "medical_research"],
                "tools": ["electronic_health_records", "medical_imaging", "diagnostic_tools", "telemedicine", "clinical_databases"],
                "questions": [
                    "What are the key factors to consider when diagnosing diabetes?",
                    "How would you develop a patient care plan for chronic heart disease?",
                    "What are the best practices for infection control in hospitals?",
                    "How do you interpret common blood test results?",
                    "What role does preventive care play in population health management?"
                ]
            },
            "finance": {
                "name": "Finance",
                "description": "Expert in financial analysis, investment strategies, and risk management",
                "keywords": ["finance", "investment", "analysis", "risk", "portfolio", "trading", "banking", "economics"],
                "capabilities": ["financial_analysis", "investment_strategy", "risk_management", "portfolio_optimization", "market_analysis"],
                "tools": ["excel", "bloomberg", "financial_modeling", "trading_platforms", "risk_analytics"],
                "questions": [
                    "How would you evaluate the risk-return profile of a stock portfolio?",
                    "What factors should be considered when creating an investment strategy?",
                    "How do you perform a discounted cash flow analysis?",
                    "What are the key metrics for evaluating a company's financial health?",
                    "How would you hedge against currency risk in international investments?"
                ]
            }
        }
        
        self.structures = ["keywords", "description", "embedding"]
    
    def create_keywords_agent(self, topic_key: str, topic_data: Dict, agent_num: int) -> Dict[str, Any]:
        """Create an agent with keywords capability structure"""
        agent_id = f"{topic_key}-kw-{agent_num:03d}"
        
        return {
            "@context": "https://projectnanda.org/agentfacts/v1",
            "id": f"did:nanda:agent:{agent_id}",
            "agent_id": agent_id,
            "agent_name": f"{topic_data['name']} Keywords Agent {agent_num}",
            "structure_type": "keywords",
            "topic": topic_key,
            "capabilities": {
                "keywords": topic_data["keywords"],
                "search_method": "keyword_match",
                "specialization_level": f"level_{agent_num}",
                "technical_skills": topic_data["capabilities"],
                "tools": topic_data["tools"]
            },
            "description": f"{topic_data['description']} - Keywords Variant {agent_num}",
            "specialization": topic_data["name"],
            "domain": topic_key,
            "tags": topic_data["keywords"][:5],  # First 5 keywords as tags
            "questions": topic_data["questions"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    def create_description_agent(self, topic_key: str, topic_data: Dict, agent_num: int) -> Dict[str, Any]:
        """Create an agent with description capability structure"""
        agent_id = f"{topic_key}-desc-{agent_num:03d}"
        
        # Create detailed description (250-300 words)
        detailed_description = f"""
        {topic_data['description']} This agent specializes in {topic_key.replace('_', ' ')} with extensive experience 
        in {', '.join(topic_data['capabilities'][:3])}. With advanced knowledge in {', '.join(topic_data['tools'][:4])}, 
        this agent can handle complex {topic_key.replace('_', ' ')} challenges and provide expert-level guidance.
        
        Key areas of expertise include {', '.join(topic_data['capabilities'])}, with particular strength in 
        problem-solving and analytical thinking. The agent has been trained on industry best practices and 
        can adapt to various project requirements and constraints.
        
        This variant {agent_num} brings unique perspectives and specialized knowledge to {topic_key.replace('_', ' ')} 
        projects, ensuring high-quality deliverables and innovative solutions. Whether working on research, 
        development, or implementation tasks, this agent maintains professional standards and delivers 
        comprehensive results that meet or exceed expectations.
        """.strip()
        
        return {
            "@context": "https://projectnanda.org/agentfacts/v1",
            "id": f"did:nanda:agent:{agent_id}",
            "agent_id": agent_id,
            "agent_name": f"{topic_data['name']} Description Agent {agent_num}",
            "structure_type": "description",
            "topic": topic_key,
            "capabilities": {
                "description_text": detailed_description,
                "search_method": "text_search",
                "specialization_level": f"level_{agent_num}",
                "technical_skills": topic_data["capabilities"],
                "tools": topic_data["tools"]
            },
            "description": detailed_description,
            "specialization": topic_data["name"],
            "domain": topic_key,
            "tags": topic_data["keywords"][:5],
            "questions": topic_data["questions"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    def create_embedding_agent(self, topic_key: str, topic_data: Dict, agent_num: int) -> Dict[str, Any]:
        """Create an agent with embedding capability structure"""
        agent_id = f"{topic_key}-embed-{agent_num:03d}"
        
        # Create description for embedding
        embedding_description = f"""
        Advanced {topic_data['name']} specialist with deep expertise in {', '.join(topic_data['capabilities'])}. 
        This agent combines theoretical knowledge with practical experience in {topic_key.replace('_', ' ')}, 
        utilizing cutting-edge tools and methodologies including {', '.join(topic_data['tools'])}. 
        Specializes in delivering high-quality solutions and expert consultation for complex {topic_key.replace('_', ' ')} 
        challenges. Variant {agent_num} offers unique insights and specialized approaches to problem-solving.
        """.strip()
        
        return {
            "@context": "https://projectnanda.org/agentfacts/v1",
            "id": f"did:nanda:agent:{agent_id}",
            "agent_id": agent_id,
            "agent_name": f"{topic_data['name']} Embedding Agent {agent_num}",
            "structure_type": "embedding",
            "topic": topic_key,
            "capabilities": {
                "description_text": embedding_description,
                "search_method": "embedding_similarity",
                "specialization_level": f"level_{agent_num}",
                "technical_skills": topic_data["capabilities"],
                "tools": topic_data["tools"],
                # Embedding will be added later by the embedding manager
                "description_embedding": None,
                "embedding_model": "clip",
                "embedding_dimension": 512
            },
            "description": embedding_description,
            "specialization": topic_data["name"],
            "domain": topic_key,
            "tags": topic_data["keywords"][:5],
            "questions": topic_data["questions"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    
    def create_all_agents(self) -> List[Dict[str, Any]]:
        """Create all 60 agents"""
        all_agents = []
        
        print("🏗️ Creating 60 test agents...")
        print("=" * 50)
        
        for topic_key, topic_data in self.topics.items():
            print(f"\n📋 Creating agents for {topic_data['name']}:")
            
            for structure in self.structures:
                print(f"  🔧 {structure.capitalize()} structure:")
                
                for agent_num in range(1, 6):  # 5 agents per structure
                    if structure == "keywords":
                        agent = self.create_keywords_agent(topic_key, topic_data, agent_num)
                    elif structure == "description":
                        agent = self.create_description_agent(topic_key, topic_data, agent_num)
                    elif structure == "embedding":
                        agent = self.create_embedding_agent(topic_key, topic_data, agent_num)
                    
                    all_agents.append(agent)
                    print(f"    ✅ {agent['agent_id']}")
        
        print(f"\n🎯 Total agents created: {len(all_agents)}")
        return all_agents
    
    def populate_database(self, agents: List[Dict[str, Any]]) -> int:
        """Populate MongoDB with the created agents"""
        print("\n💾 Populating MongoDB database...")
        
        try:
            # Insert all agents
            result = self.mongodb_facts.collection.insert_many(agents)
            inserted_count = len(result.inserted_ids)
            
            print(f"✅ Successfully inserted {inserted_count} agents")
            
            # Update embedding agents with actual embeddings
            embedding_agents = [a for a in agents if a['structure_type'] == 'embedding']
            if embedding_agents:
                print(f"🔄 Updating {len(embedding_agents)} embedding agents with CLIP embeddings...")
                updated_count = self.mongodb_facts.update_agents_with_modular_embeddings("embedding")
                print(f"✅ Updated {updated_count} agents with embeddings")
            
            return inserted_count
            
        except Exception as e:
            print(f"❌ Error populating database: {e}")
            return 0
    
    def verify_creation(self):
        """Verify that all agents were created correctly"""
        print("\n🔍 Verifying agent creation...")
        
        # Count by structure type
        for structure in self.structures:
            count = self.mongodb_facts.collection.count_documents({"structure_type": structure})
            expected = 4 * 5  # 4 topics × 5 agents
            print(f"  {structure.capitalize()}: {count}/{expected} agents")
        
        # Count by topic
        for topic_key in self.topics.keys():
            count = self.mongodb_facts.collection.count_documents({"topic": topic_key})
            expected = 3 * 5  # 3 structures × 5 agents
            print(f"  {topic_key.replace('_', ' ').title()}: {count}/{expected} agents")
        
        # Total count
        total_count = self.mongodb_facts.get_agent_count()
        print(f"\n📊 Total agents in database: {total_count}")

def main():
    """Main execution function"""
    creator = TestAgentCreator()
    
    # Create all agents
    agents = creator.create_all_agents()
    
    # Populate database
    inserted_count = creator.populate_database(agents)
    
    if inserted_count > 0:
        # Verify creation
        creator.verify_creation()
        print("\n🎉 Agent creation completed successfully!")
    else:
        print("\n❌ Agent creation failed!")

if __name__ == "__main__":
    main()
