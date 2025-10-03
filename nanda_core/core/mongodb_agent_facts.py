#!/usr/bin/env python3
"""
MongoDB Agent Facts Client for semantic search testing
"""

import os
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from datetime import datetime
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables only.")

# Import modular embedding system
try:
    from ..embeddings.embedding_manager import get_embedding_manager
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("⚠️ Modular embeddings not available - using fallback")
    EMBEDDINGS_AVAILABLE = False


class MongoDBAgentFacts:
    """MongoDB client for agent facts with semantic search capabilities"""
    
    def __init__(self, mongodb_uri: str = None):
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_AGENTFACTS_URI", "mongodb://localhost:27017/")
        self.client = None
        self.db = None
        self.collection = None
        self.embedding_manager = None
        self._connect()
        self._initialize_embeddings()
    
    def _connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client.nanda_test
            self.collection = self.db.agent_facts
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB test cluster")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise
    
    def _initialize_embeddings(self):
        """Initialize the modular embedding system"""
        if EMBEDDINGS_AVAILABLE:
            try:
                # Look for embedding config in the same directory
                config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'embedding_config.json')
                if os.path.exists(config_path):
                    self.embedding_manager = get_embedding_manager(config_path)
                else:
                    self.embedding_manager = get_embedding_manager()
                print("✅ Modular embedding system initialized")
            except Exception as e:
                print(f"⚠️ Failed to initialize embeddings: {e}")
                self.embedding_manager = None
        else:
            self.embedding_manager = None
    
    def create_agent_fact(self, agent_id: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a standardized agent fact document"""
        return {
            "@context": "https://projectnanda.org/agentfacts/v1",
            "id": f"did:nanda:agent:{agent_id}",
            "handle": f"@{agent_id}",
            "agent_id": agent_id,
            "agent_name": agent_data.get("name", f"Agent {agent_id}"),
            "provider": "nanda_test",
            "version": "1.0",
            "created_at": datetime.utcnow(),
            "description": agent_data.get("description", ""),
            "specialization": agent_data.get("specialization", ""),
            "capabilities": {
                "technical_skills": agent_data.get("technical_skills", []),
                "domains": agent_data.get("domains", []),
                "specializations": agent_data.get("specializations", []),
                "tools": agent_data.get("tools", []),
                "languages": agent_data.get("languages", []),
                "certifications": agent_data.get("certifications", [])
            },
            "endpoints": {
                "a2a": agent_data.get("a2a_endpoint", f"http://test.example.com:6000"),
                "api": agent_data.get("api_endpoint", f"http://test.example.com:6001")
            },
            "status": "active",
            "tags": agent_data.get("tags", [])
        }
    
    def populate_test_agents(self):
        """Populate the collection with 100 diverse test agents"""
        print("🔄 Populating test agents...")
        
        # Clear existing data
        self.collection.delete_many({})
        
        test_agents = self._generate_test_agents()
        
        # Insert all agents
        agent_docs = []
        for agent_id, agent_data in test_agents.items():
            doc = self.create_agent_fact(agent_id, agent_data)
            agent_docs.append(doc)
        
        result = self.collection.insert_many(agent_docs)
        print(f"✅ Inserted {len(result.inserted_ids)} test agents")
        
        # Create indexes for better search performance
        self.collection.create_index("agent_id", unique=True)
        self.collection.create_index([("capabilities.technical_skills", "text"), 
                                     ("capabilities.domains", "text"),
                                     ("capabilities.specializations", "text"),
                                     ("description", "text"),
                                     ("specialization", "text")])
        print("✅ Created search indexes")
    
    def _generate_test_agents(self) -> Dict[str, Dict[str, Any]]:
        """Generate 100 diverse test agents with realistic capabilities"""
        agents = {}
        
        # Technology agents
        tech_agents = [
            ("python-expert", {
                "name": "Python Expert",
                "description": "Senior Python developer with expertise in web frameworks, data science, and automation",
                "specialization": "Python Development",
                "technical_skills": ["python", "django", "flask", "fastapi", "pandas", "numpy", "pytest"],
                "domains": ["web_development", "data_science", "automation", "backend_development"],
                "specializations": ["api_development", "data_analysis", "web_scraping", "test_automation"],
                "tools": ["git", "docker", "postgresql", "redis", "celery"],
                "languages": ["python", "sql", "javascript"],
                "tags": ["senior", "python", "backend", "data"]
            }),
            ("javascript-expert", {
                "name": "JavaScript Expert",
                "description": "Full-stack JavaScript developer specializing in React, Node.js, and modern web technologies",
                "specialization": "JavaScript Development",
                "technical_skills": ["javascript", "typescript", "react", "nodejs", "express", "vue", "angular"],
                "domains": ["web_development", "frontend_development", "backend_development", "mobile_development"],
                "specializations": ["spa_development", "api_development", "mobile_apps", "real_time_applications"],
                "tools": ["webpack", "npm", "yarn", "docker", "mongodb"],
                "languages": ["javascript", "typescript", "html", "css"],
                "tags": ["fullstack", "javascript", "react", "nodejs"]
            }),
            ("devops-engineer", {
                "name": "DevOps Engineer",
                "description": "Cloud infrastructure and DevOps specialist with expertise in AWS, Kubernetes, and CI/CD",
                "specialization": "DevOps & Cloud Infrastructure",
                "technical_skills": ["aws", "kubernetes", "docker", "terraform", "ansible", "jenkins", "gitlab-ci"],
                "domains": ["cloud_computing", "infrastructure", "automation", "deployment"],
                "specializations": ["container_orchestration", "infrastructure_as_code", "ci_cd_pipelines", "monitoring"],
                "tools": ["kubernetes", "docker", "terraform", "prometheus", "grafana"],
                "languages": ["bash", "python", "yaml", "go"],
                "tags": ["devops", "cloud", "kubernetes", "aws"]
            }),
            ("data-scientist", {
                "name": "Data Scientist",
                "description": "Machine learning and data science expert with experience in predictive modeling and analytics",
                "specialization": "Data Science & Machine Learning",
                "technical_skills": ["python", "r", "machine_learning", "deep_learning", "statistics", "data_visualization"],
                "domains": ["data_science", "machine_learning", "analytics", "artificial_intelligence"],
                "specializations": ["predictive_modeling", "nlp", "computer_vision", "statistical_analysis"],
                "tools": ["jupyter", "tensorflow", "pytorch", "scikit-learn", "pandas", "matplotlib"],
                "languages": ["python", "r", "sql", "scala"],
                "tags": ["data_science", "ml", "ai", "analytics"]
            }),
            ("cybersecurity-expert", {
                "name": "Cybersecurity Expert",
                "description": "Information security specialist focusing on penetration testing, security audits, and threat analysis",
                "specialization": "Cybersecurity & Information Security",
                "technical_skills": ["penetration_testing", "vulnerability_assessment", "network_security", "cryptography"],
                "domains": ["cybersecurity", "information_security", "risk_assessment", "compliance"],
                "specializations": ["ethical_hacking", "security_auditing", "incident_response", "forensics"],
                "tools": ["metasploit", "nmap", "wireshark", "burp_suite", "kali_linux"],
                "languages": ["python", "bash", "powershell", "c"],
                "tags": ["security", "pentesting", "cybersecurity", "ethical_hacking"]
            })
        ]
        
        # Business & Finance agents
        business_agents = [
            ("financial-advisor", {
                "name": "Financial Advisor",
                "description": "Certified financial planner specializing in investment strategies and wealth management",
                "specialization": "Financial Planning & Investment",
                "technical_skills": ["financial_analysis", "investment_planning", "risk_assessment", "portfolio_management"],
                "domains": ["finance", "investment", "wealth_management", "financial_planning"],
                "specializations": ["retirement_planning", "tax_optimization", "estate_planning", "insurance"],
                "tools": ["excel", "financial_modeling", "bloomberg", "quickbooks"],
                "languages": ["english", "spanish"],
                "certifications": ["CFP", "CFA", "Series_7"],
                "tags": ["finance", "investment", "planning", "certified"]
            }),
            ("business-analyst", {
                "name": "Business Analyst",
                "description": "Strategic business analyst with expertise in process optimization and data-driven decision making",
                "specialization": "Business Analysis & Strategy",
                "technical_skills": ["business_analysis", "process_mapping", "requirements_gathering", "data_analysis"],
                "domains": ["business_strategy", "process_improvement", "project_management", "analytics"],
                "specializations": ["business_process_optimization", "stakeholder_management", "change_management"],
                "tools": ["excel", "powerbi", "tableau", "visio", "jira"],
                "languages": ["english", "mandarin"],
                "certifications": ["CBAP", "PMP"],
                "tags": ["business", "analysis", "strategy", "process"]
            }),
            ("marketing-specialist", {
                "name": "Marketing Specialist",
                "description": "Digital marketing expert specializing in SEO, content marketing, and social media strategy",
                "specialization": "Digital Marketing & Content Strategy",
                "technical_skills": ["seo", "content_marketing", "social_media", "email_marketing", "ppc"],
                "domains": ["digital_marketing", "content_creation", "brand_management", "customer_acquisition"],
                "specializations": ["search_engine_optimization", "content_strategy", "social_media_marketing"],
                "tools": ["google_analytics", "hootsuite", "mailchimp", "canva", "wordpress"],
                "languages": ["english", "french"],
                "tags": ["marketing", "seo", "content", "social_media"]
            })
        ]
        
        # Healthcare agents
        healthcare_agents = [
            ("medical-doctor", {
                "name": "Medical Doctor",
                "description": "Licensed physician specializing in internal medicine and patient care",
                "specialization": "Internal Medicine",
                "technical_skills": ["diagnosis", "treatment_planning", "patient_care", "medical_research"],
                "domains": ["healthcare", "medicine", "patient_care", "medical_research"],
                "specializations": ["internal_medicine", "preventive_care", "chronic_disease_management"],
                "tools": ["electronic_health_records", "medical_imaging", "diagnostic_equipment"],
                "languages": ["english", "spanish", "portuguese"],
                "certifications": ["MD", "Board_Certified_Internal_Medicine"],
                "tags": ["healthcare", "medicine", "doctor", "patient_care"]
            }),
            ("nurse-practitioner", {
                "name": "Nurse Practitioner",
                "description": "Advanced practice nurse with expertise in primary care and patient education",
                "specialization": "Primary Care Nursing",
                "technical_skills": ["patient_assessment", "care_planning", "health_education", "medication_management"],
                "domains": ["healthcare", "nursing", "primary_care", "patient_education"],
                "specializations": ["family_practice", "geriatric_care", "chronic_care_management"],
                "tools": ["ehr_systems", "patient_monitoring", "telehealth_platforms"],
                "languages": ["english", "spanish"],
                "certifications": ["NP", "AANP", "BLS", "ACLS"],
                "tags": ["healthcare", "nursing", "primary_care", "patient_education"]
            })
        ]
        
        # Add all agent categories
        for agent_id, data in tech_agents + business_agents + healthcare_agents:
            agents[agent_id] = data
        
        # Generate more agents to reach 100
        additional_domains = [
            ("legal", "Legal Advisor", "Legal consultation and contract review"),
            ("education", "Education Specialist", "Curriculum development and teaching"),
            ("design", "UX Designer", "User experience and interface design"),
            ("sales", "Sales Representative", "Customer relationship and sales strategy"),
            ("hr", "HR Manager", "Human resources and talent management"),
            ("accounting", "Accountant", "Financial accounting and tax preparation"),
            ("project-management", "Project Manager", "Project planning and execution"),
            ("content-writing", "Content Writer", "Technical and creative writing"),
            ("translation", "Translator", "Language translation and localization"),
            ("research", "Research Analyst", "Market research and data analysis")
        ]
        
        # Generate variations for each domain
        for i, (domain, title, desc) in enumerate(additional_domains):
            for j in range(8):  # 8 variations per domain
                agent_id = f"{domain}-{j+1:03d}"
                agents[agent_id] = {
                    "name": f"{title} {j+1}",
                    "description": f"{desc} - Level {j+1} specialist",
                    "specialization": f"{title} - Level {j+1}",
                    "technical_skills": [domain.replace("-", "_"), "communication", "problem_solving"],
                    "domains": [domain.replace("-", "_"), "consulting", "professional_services"],
                    "specializations": [f"{domain.replace('-', '_')}_specialist"],
                    "tools": ["office_suite", "communication_tools"],
                    "languages": ["english"],
                    "tags": [domain, "professional", f"level_{j+1}"]
                }
        
        return agents
    
    def search_agents_by_capabilities(self, query: str, limit: int = 10, structure_type: str = None) -> List[Dict[str, Any]]:
        """Search agents by capabilities with optional structure type filtering"""
        try:
            query_words = query.lower().split()
            
            # If structure type is specified, use structure-specific search
            if structure_type:
                return self._search_by_structure_type(query, query_words, structure_type, limit)
            
            # Default: MongoDB text search across all agents
            text_results = list(self.collection.find(
                {"$text": {"$search": query}},
                {"score": {"$meta": "textScore"}}
            ).sort([("score", {"$meta": "textScore"})]).limit(limit * 2))
            
            # Manual scoring for better relevance
            scored_agents = []
            
            for agent in text_results:
                score = self._calculate_relevance_score(agent, query_words)
                if score > 0:
                    agent['relevance_score'] = score
                    scored_agents.append(agent)
            
            # If text search doesn't return enough results, do manual search
            if len(scored_agents) < limit:
                manual_results = self._manual_capability_search(query_words, limit)
                for agent in manual_results:
                    if agent['agent_id'] not in [a['agent_id'] for a in scored_agents]:
                        scored_agents.append(agent)
            
            # Sort by relevance score and return top results
            scored_agents.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            return scored_agents[:limit]
            
        except Exception as e:
            print(f"❌ Error searching agents: {e}")
            return []
    
    def _search_by_structure_type(self, query: str, query_words: List[str], structure_type: str, limit: int) -> List[Dict[str, Any]]:
        """Search agents by specific capability structure type"""
        import time
        start_time = time.time()
        
        print(f"🔍 Searching {structure_type} agents (100 agents) for: '{query}'")
        
        # Get agents with specific structure type
        structure_filter = {"structure_type": structure_type}
        
        if structure_type == "keywords":
            return self._search_keywords_structure(query_words, structure_filter, limit)
        elif structure_type == "description":
            return self._search_description_structure(query, structure_filter, limit)
        elif structure_type == "embedding":
            return self._search_embedding_structure(query, structure_filter, limit)
        else:
            print(f"❌ Unknown structure type: {structure_type}")
            return []
    
    def _search_keywords_structure(self, query_words: List[str], structure_filter: Dict, limit: int) -> List[Dict[str, Any]]:
        """Search through keyword-based capability structure (100 agents)"""
        import time
        start_time = time.time()
        
        # Get all keyword-structure agents
        agents = list(self.collection.find(structure_filter))
        scored_agents = []
        
        for agent in agents:
            score = 0.0
            keywords = agent.get('capabilities', {}).get('keywords', [])
            
            # Simple keyword matching
            for word in query_words:
                for keyword in keywords:
                    if word.lower() in keyword.lower():
                        score += 1.0
            
            if score > 0:
                agent['relevance_score'] = score / len(query_words)  # Normalize
                agent['search_method'] = 'keywords'
                scored_agents.append(agent)
        
        # Sort by score and return top results
        scored_agents.sort(key=lambda x: x['relevance_score'], reverse=True)
        search_time = time.time() - start_time
        print(f"⚡ Keywords search: {len(scored_agents)} results in {search_time:.3f}s")
        
        return scored_agents[:limit]
    
    def _search_description_structure(self, query: str, structure_filter: Dict, limit: int) -> List[Dict[str, Any]]:
        """Search through description-based capability structure (100 agents)"""
        import time
        start_time = time.time()
        
        # MongoDB text search within description structure agents only
        text_results = list(self.collection.find(
            {**structure_filter, "$text": {"$search": query}},
            {"score": {"$meta": "textScore"}}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit))
        
        # Add search metadata
        for agent in text_results:
            agent['search_method'] = 'description'
            agent['relevance_score'] = agent.get('score', 0)
        
        search_time = time.time() - start_time
        print(f"⚡ Description search: {len(text_results)} results in {search_time:.3f}s")
        
        return text_results
    
    def _search_embedding_structure(self, query: str, structure_filter: Dict, limit: int) -> List[Dict[str, Any]]:
        """Search through embedding-based capability structure (100 agents)"""
        import time
        start_time = time.time()
        
        # Check if embeddings are available
        if not self.embedding_manager:
            print("⚠️ Embedding manager not available, falling back to text search")
            return self._search_description_structure(query, structure_filter, limit)
        
        try:
            # Create query embedding
            query_embedding = self.embedding_manager.create_embedding(query)
            
            # Get all embedding-structure agents with embeddings
            agents = list(self.collection.find({
                **structure_filter,
                "capabilities.description_embedding": {"$exists": True}
            }))
            
            if not agents:
                print("⚠️ No agents with embeddings found, falling back to text search")
                return self._search_description_structure(query, structure_filter, limit)
            
            # Calculate cosine similarity
            scored_agents = []
            for agent in agents:
                embedding = agent.get('capabilities', {}).get('description_embedding')
                if embedding:
                    similarity = self._cosine_similarity(query_embedding, embedding)
                    agent['relevance_score'] = similarity
                    agent['search_method'] = 'embedding'
                    scored_agents.append(agent)
            
            # Sort by similarity and return top results
            scored_agents.sort(key=lambda x: x['relevance_score'], reverse=True)
            search_time = time.time() - start_time
            print(f"⚡ Embedding search: {len(scored_agents)} results in {search_time:.3f}s")
            
            return scored_agents[:limit]
            
        except Exception as e:
            print(f"❌ Embedding search failed: {e}")
            return self._search_description_structure(query, structure_filter, limit)
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        import math
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _calculate_relevance_score(self, agent: Dict[str, Any], query_words: List[str]) -> float:
        """Calculate relevance score based on capability matching"""
        score = 0.0
        capabilities = agent.get('capabilities', {})
        
        # Search in different capability fields with different weights
        search_fields = [
            (capabilities.get('technical_skills', []), 1.0),
            (capabilities.get('domains', []), 0.8),
            (capabilities.get('specializations', []), 0.9),
            (capabilities.get('tools', []), 0.6),
            ([agent.get('specialization', '')], 0.7),
            ([agent.get('description', '')], 0.5),
            (agent.get('tags', []), 0.4)
        ]
        
        for field_values, weight in search_fields:
            field_text = ' '.join(str(v).lower() for v in field_values)
            word_matches = sum(1 for word in query_words if word in field_text)
            if word_matches > 0:
                score += (word_matches / len(query_words)) * weight
        
        return score
    
    def _manual_capability_search(self, query_words: List[str], limit: int) -> List[Dict[str, Any]]:
        """Manual search through capabilities when text search is insufficient"""
        all_agents = list(self.collection.find())
        scored_agents = []
        
        for agent in all_agents:
            score = self._calculate_relevance_score(agent, query_words)
            if score > 0:
                agent['relevance_score'] = score
                scored_agents.append(agent)
        
        scored_agents.sort(key=lambda x: x['relevance_score'], reverse=True)
        return scored_agents[:limit]
    
    def get_agent_count(self) -> int:
        """Get total number of agents in the collection"""
        return self.collection.count_documents({})
    
    def get_sample_agents(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get a sample of agents for testing"""
        return list(self.collection.find().limit(limit))
    
    def update_agents_with_modular_embeddings(self, structure_type: str = "embedding") -> int:
        """Update agents with embeddings from the modular embedding system"""
        if not self.embedding_manager:
            print("❌ Embedding manager not available")
            return 0
        
        print(f"🔄 Updating {structure_type} agents with modular embeddings...")
        
        # Get agents that need embedding updates
        agents = list(self.collection.find(
            {"structure_type": structure_type},
            {"agent_id": 1, "agent_name": 1, "capabilities.description_text": 1}
        ))
        
        if not agents:
            print(f"⚠️ No {structure_type} agents found")
            return 0
        
        print(f"📋 Found {len(agents)} agents to update")
        
        # Extract texts for batch processing
        texts = []
        agent_ids = []
        
        for agent in agents:
            description = agent.get("capabilities", {}).get("description_text", "")
            if description:
                texts.append(description)
                agent_ids.append(agent["agent_id"])
        
        if not texts:
            print("⚠️ No agent descriptions found")
            return 0
        
        try:
            # Create embeddings using modular system
            embeddings = self.embedding_manager.create_batch_embeddings(texts)
            
            # Get active embedder info
            embedder_info = self.embedding_manager.get_active_embedder_info()
            
            # Update each agent
            updated_count = 0
            for i, (agent_id, embedding) in enumerate(zip(agent_ids, embeddings)):
                result = self.collection.update_one(
                    {"agent_id": agent_id},
                    {
                        "$set": {
                            "capabilities.description_embedding": embedding,
                            "capabilities.embedding_model": embedder_info.get('model', 'unknown'),
                            "capabilities.embedding_dimension": len(embedding),
                            "capabilities.embedding_method": "modular_system",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    if (i + 1) % 10 == 0:
                        print(f"  ✅ Updated {i + 1}/{len(agent_ids)} agents")
            
            print(f"✅ Successfully updated {updated_count} agents with {embedder_info.get('name', 'unknown')} embeddings")
            return updated_count
            
        except Exception as e:
            print(f"❌ Failed to update agents with embeddings: {e}")
            return 0


if __name__ == "__main__":
    # Test the MongoDB agent facts system
    print("🧪 Testing MongoDB Agent Facts System")
    
    try:
        # Initialize client
        mongo_facts = MongoDBAgentFacts()
        
        # Populate test data
        mongo_facts.populate_test_agents()
        
        # Test searches
        test_queries = [
            "python expert",
            "data scientist",
            "financial advisor",
            "cybersecurity",
            "javascript developer",
            "medical doctor",
            "business analyst"
        ]
        
        print("\n🔍 Testing semantic search:")
        for query in test_queries:
            print(f"\n--- Search: '{query}' ---")
            results = mongo_facts.search_agents_by_capabilities(query, limit=3)
            for i, agent in enumerate(results, 1):
                score = agent.get('relevance_score', 0)
                print(f"{i}. {agent['agent_name']} (Score: {score:.2f})")
                print(f"   Specialization: {agent['specialization']}")
                print(f"   Skills: {', '.join(agent['capabilities']['technical_skills'][:3])}")
        
        print(f"\n✅ Test completed. Total agents: {mongo_facts.get_agent_count()}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
