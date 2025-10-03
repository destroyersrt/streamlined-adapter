#!/usr/bin/env python3
"""
Test 3 Different Capability Structures for Agent Discovery
"""

import os
import sys
import time
import json
from typing import Dict, List, Any
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed")

from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts


class CapabilityStructureTester:
    """Test different capability structures for agent discovery"""
    
    def __init__(self):
        self.mongo_facts = MongoDBAgentFacts()
        self.test_results = {}
    
    def create_structure_1_keywords(self) -> List[Dict[str, Any]]:
        """Structure 1: 3-5 Keywords per agent (100 agents)"""
        agents = []
        
        # Base agent templates with different specializations
        base_agents = [
            {
                "name": "Python Developer",
                "keywords": ["python", "django", "flask", "api", "backend"],
                "description": "Python development specialist"
            },
            {
                "name": "Data Scientist", 
                "keywords": ["machine-learning", "pandas", "tensorflow", "statistics", "python"],
                "description": "Data science and ML expert"
            },
            {
                "name": "DevOps Engineer", 
                "keywords": ["kubernetes", "docker", "aws", "terraform", "cicd"],
                "description": "Cloud infrastructure specialist"
            },
            {
                "name": "Frontend Developer",
                "keywords": ["react", "javascript", "typescript", "css", "html"],
                "description": "Frontend web development expert"
            },
            {
                "name": "Security Expert",
                "keywords": ["cybersecurity", "penetration-testing", "encryption", "compliance", "audit"],
                "description": "Information security specialist"
            },
            {
                "name": "Mobile Developer",
                "keywords": ["react-native", "flutter", "ios", "android", "mobile"],
                "description": "Mobile application developer"
            },
            {
                "name": "Database Expert",
                "keywords": ["postgresql", "mongodb", "mysql", "database", "sql"],
                "description": "Database design and optimization specialist"
            },
            {
                "name": "AI Engineer",
                "keywords": ["artificial-intelligence", "neural-networks", "deep-learning", "pytorch", "ai"],
                "description": "Artificial intelligence and ML engineer"
            },
            {
                "name": "Cloud Architect",
                "keywords": ["aws", "azure", "gcp", "cloud-architecture", "serverless"],
                "description": "Cloud solutions architect"
            },
            {
                "name": "QA Engineer",
                "keywords": ["testing", "automation", "selenium", "quality-assurance", "cypress"],
                "description": "Quality assurance and testing specialist"
            }
        ]
        
        # Create 100 agents (10 variations of each base agent)
        for i in range(100):
            base_idx = i % len(base_agents)
            variation = i // len(base_agents) + 1
            base_agent = base_agents[base_idx]
            
            agent = {
                "@context": "https://projectnanda.org/agentfacts/v1",
                "id": f"did:nanda:agent:kw-{i+1:03d}",
                "agent_id": f"kw-{i+1:03d}",
                "agent_name": f"{base_agent['name']} {variation}",
                "structure_type": "keywords",
                "capabilities": {
                    "keywords": base_agent["keywords"],
                    "search_method": "keyword_match",
                    "specialization_level": f"level_{variation}",
                    "experience_years": (variation * 2) + 3
                },
                "description": f"{base_agent['description']} - Variation {variation}",
                "created_at": datetime.utcnow()
            }
            agents.append(agent)
        
        return agents
    
    def create_structure_2_descriptions(self) -> List[Dict[str, Any]]:
        """Structure 2: 250-300 word descriptions (100 agents)"""
        agents = []
        
        # Base description templates
        base_descriptions = [
            {
                "name": "Python Developer",
                "description": """I am a senior Python developer with over 8 years of experience building scalable web applications and backend systems. My expertise spans across multiple Python frameworks including Django, Flask, and FastAPI, allowing me to create robust REST APIs and microservices architectures. I specialize in database design and optimization, working extensively with PostgreSQL, MySQL, and MongoDB to ensure efficient data storage and retrieval. My technical skills include advanced Python programming, object-oriented design patterns, and test-driven development using pytest and unittest frameworks. I have deep knowledge of containerization technologies like Docker and orchestration with Kubernetes, enabling seamless deployment and scaling of applications. I'm proficient in cloud platforms, particularly AWS services including EC2, RDS, Lambda, and S3. I excel at code optimization, performance tuning, and implementing caching strategies using Redis and Memcached. My experience with asynchronous programming using asyncio and Celery helps me build high-performance applications that can handle concurrent requests efficiently."""
            },
            {
                "name": "Data Scientist", 
                "description": """I am a data scientist with extensive experience in machine learning, statistical analysis, and predictive modeling. My expertise covers the entire data science pipeline from data collection and preprocessing to model deployment and monitoring. I specialize in supervised and unsupervised learning algorithms, including linear regression, decision trees, random forests, support vector machines, and neural networks. My technical toolkit includes Python libraries such as pandas, NumPy, scikit-learn, TensorFlow, and PyTorch for data manipulation and machine learning. I'm proficient in statistical analysis using R and have experience with big data technologies like Spark and Hadoop for processing large datasets. I excel at data visualization using matplotlib, seaborn, and Plotly to create compelling insights and presentations. I have deep knowledge of feature engineering, dimensionality reduction techniques like PCA and t-SNE, and model evaluation metrics. My experience includes working with time series analysis, natural language processing, and computer vision projects."""
            },
            {
                "name": "DevOps Engineer",
                "description": """I am a DevOps engineer specializing in cloud infrastructure, automation, and continuous integration/continuous deployment (CI/CD) practices. My expertise spans across multiple cloud platforms including AWS, Google Cloud Platform, and Microsoft Azure, where I design and implement scalable, secure, and cost-effective infrastructure solutions. My core competencies include Infrastructure as Code (IaC) using Terraform, CloudFormation, and Ansible to automate infrastructure provisioning and management. I'm proficient in containerization technologies, particularly Docker and Kubernetes, enabling microservices architectures and efficient resource utilization. I have extensive experience with container orchestration, service mesh technologies like Istio, and monitoring solutions. I excel in building robust CI/CD pipelines using Jenkins, GitLab CI, GitHub Actions, and Azure DevOps to automate testing, building, and deployment processes. My expertise includes implementing blue-green deployments, canary releases, and rollback strategies to ensure zero-downtime deployments."""
            },
            {
                "name": "Frontend Developer",
                "description": """I am a frontend developer specializing in modern web technologies and user experience design. My expertise includes React, Vue.js, Angular, and vanilla JavaScript for building responsive and interactive web applications. I have extensive experience with TypeScript, HTML5, CSS3, and modern CSS frameworks like Tailwind CSS and Bootstrap. I specialize in component-based architecture, state management using Redux, Vuex, and Context API, and building scalable frontend applications. My skills include responsive design, cross-browser compatibility, accessibility standards (WCAG), and performance optimization techniques. I'm proficient in build tools like Webpack, Vite, and Parcel, and have experience with testing frameworks including Jest, Cypress, and Testing Library. I work closely with designers to implement pixel-perfect designs and ensure excellent user experience across all devices and platforms. I also have knowledge of backend integration, RESTful APIs, GraphQL, and modern deployment practices using CI/CD pipelines."""
            },
            {
                "name": "Security Expert",
                "description": """I am a cybersecurity expert with comprehensive experience in information security, penetration testing, and compliance frameworks. My expertise covers network security, application security, cloud security, and incident response. I specialize in vulnerability assessments, security audits, and implementing security best practices across organizations. My technical skills include penetration testing tools like Metasploit, Nmap, Burp Suite, and OWASP ZAP for identifying and exploiting security vulnerabilities. I have extensive knowledge of encryption technologies, PKI infrastructure, identity and access management (IAM), and multi-factor authentication systems. I'm experienced in compliance frameworks including SOC 2, ISO 27001, GDPR, and HIPAA, helping organizations meet regulatory requirements. My expertise includes security monitoring using SIEM tools, threat intelligence, malware analysis, and digital forensics. I also specialize in secure coding practices, security architecture design, and training development teams on security awareness and best practices."""
            },
            {
                "name": "Mobile Developer",
                "description": """I am a mobile application developer with expertise in both native and cross-platform development. My experience includes iOS development using Swift and Objective-C, Android development using Kotlin and Java, and cross-platform development using React Native and Flutter. I specialize in creating user-friendly mobile applications with excellent performance and intuitive user interfaces. My technical skills include mobile UI/UX design principles, responsive layouts, and platform-specific design guidelines. I have extensive experience with mobile app architecture patterns like MVVM, MVP, and Clean Architecture, ensuring maintainable and scalable codebases. I'm proficient in mobile-specific technologies including push notifications, location services, camera integration, offline data synchronization, and mobile payment systems. I have experience with app store deployment processes, app store optimization (ASO), and mobile analytics integration. I also work with backend integration, RESTful APIs, real-time communication using WebSockets, and mobile security best practices including data encryption and secure authentication."""
            },
            {
                "name": "Database Expert",
                "description": """I am a database expert specializing in database design, optimization, and administration across multiple database systems. My expertise includes relational databases like PostgreSQL, MySQL, and SQL Server, as well as NoSQL databases including MongoDB, Cassandra, and Redis. I specialize in database schema design, query optimization, indexing strategies, and performance tuning to ensure efficient data operations. My technical skills include advanced SQL programming, stored procedures, triggers, and database functions. I have extensive experience with database administration tasks including backup and recovery, replication, clustering, and high availability configurations. I'm proficient in data modeling, normalization techniques, and designing scalable database architectures for high-traffic applications. I also have expertise in data warehousing, ETL processes, and business intelligence solutions. My experience includes database security implementation, access control, data encryption, and compliance with data protection regulations. I work with database monitoring tools, performance analysis, and capacity planning to ensure optimal database performance and reliability."""
            },
            {
                "name": "AI Engineer",
                "description": """I am an artificial intelligence engineer with deep expertise in machine learning, deep learning, and AI system development. My experience spans across computer vision, natural language processing, reinforcement learning, and generative AI technologies. I specialize in designing and implementing AI models using frameworks like TensorFlow, PyTorch, and Keras for various applications including image recognition, text analysis, and predictive modeling. My technical skills include neural network architectures, convolutional neural networks (CNNs), recurrent neural networks (RNNs), transformers, and attention mechanisms. I have extensive experience with model training, hyperparameter tuning, and optimization techniques to achieve high-performance AI systems. I'm proficient in MLOps practices including model versioning, automated training pipelines, model deployment, and monitoring in production environments. I also have expertise in data preprocessing, feature engineering, and working with large-scale datasets. My experience includes AI ethics, bias detection and mitigation, and ensuring responsible AI development practices."""
            },
            {
                "name": "Cloud Architect",
                "description": """I am a cloud solutions architect with comprehensive experience in designing and implementing scalable, secure, and cost-effective cloud infrastructures. My expertise spans across major cloud platforms including Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP). I specialize in cloud migration strategies, hybrid cloud solutions, and multi-cloud architectures. My technical skills include Infrastructure as Code (IaC) using Terraform, CloudFormation, and ARM templates for automated infrastructure provisioning. I have extensive experience with containerization using Docker and orchestration with Kubernetes, enabling microservices architectures and efficient resource utilization. I'm proficient in serverless computing, API gateways, and event-driven architectures using services like AWS Lambda, Azure Functions, and Google Cloud Functions. I also specialize in cloud security, implementing identity and access management (IAM), network security, data encryption, and compliance frameworks. My expertise includes cost optimization strategies, performance monitoring, disaster recovery planning, and ensuring high availability and scalability of cloud-based systems."""
            },
            {
                "name": "QA Engineer",
                "description": """I am a quality assurance engineer with extensive experience in software testing, test automation, and quality management processes. My expertise includes manual testing, automated testing, performance testing, and security testing across web, mobile, and API applications. I specialize in test planning, test case design, and implementing comprehensive testing strategies to ensure software quality and reliability. My technical skills include automation frameworks like Selenium, Cypress, TestNG, and Jest for creating robust automated test suites. I have extensive experience with API testing using tools like Postman, REST Assured, and SoapUI, ensuring proper functionality and integration of web services. I'm proficient in performance testing using JMeter, LoadRunner, and K6 to identify bottlenecks and ensure applications can handle expected load. I also have expertise in mobile testing, cross-browser testing, accessibility testing, and usability testing. My experience includes continuous integration and continuous testing (CI/CT) practices, integrating automated tests into CI/CD pipelines, and implementing quality gates to maintain high code quality standards."""
            }
        ]
        
        # Create 100 agents (10 variations of each base description)
        for i in range(100):
            base_idx = i % len(base_descriptions)
            variation = i // len(base_descriptions) + 1
            base_desc = base_descriptions[base_idx]
            
            # Add variation-specific details to the description
            varied_description = base_desc["description"] + f" I have {3 + variation * 2} years of specialized experience and have worked on {10 + variation * 5} major projects. My current focus includes emerging technologies and advanced {base_desc['name'].lower()} practices, with expertise level {variation} certification."
            
            agent = {
                "@context": "https://projectnanda.org/agentfacts/v1",
                "id": f"did:nanda:agent:desc-{i+1:03d}",
                "agent_id": f"desc-{i+1:03d}",
                "agent_name": f"{base_desc['name']} {variation}",
                "structure_type": "description",
                "capabilities": {
                    "full_description": varied_description,
                    "search_method": "text_search",
                    "specialization_level": f"level_{variation}",
                    "experience_years": (variation * 2) + 3
                },
                "description": varied_description[:200] + "...",  # Truncated for display
                "created_at": datetime.utcnow()
            }
            agents.append(agent)
        
        return agents
    
    def create_structure_3_embeddings(self) -> List[Dict[str, Any]]:
        """Structure 3: Embedded descriptions using Voyage AI (100 agents)"""
        print("🔄 Creating embeddings using Voyage AI...")
        
        # For now, we'll simulate embeddings since we need Voyage AI API
        # In production, you would use: voyageai.embed(text, model="voyage-large-2")
        
        agents = []
        
        # Base embedding templates (same specializations as other structures)
        base_embedding_agents = [
            {
                "name": "Python Developer",
                "description": """Senior Python developer specializing in web applications, REST APIs, Django, Flask, FastAPI, database optimization, PostgreSQL, MySQL, MongoDB, Docker, Kubernetes, AWS cloud services, microservices architecture, test-driven development, performance optimization, caching strategies, asynchronous programming, DevOps practices, CI/CD pipelines, security implementation, authentication, authorization, code optimization, API design, third-party integrations."""
            },
            {
                "name": "Data Scientist",
                "description": """Data scientist expert in machine learning, statistical analysis, predictive modeling, supervised learning, unsupervised learning, neural networks, Python pandas NumPy scikit-learn TensorFlow PyTorch, big data Spark Hadoop, data visualization matplotlib seaborn, feature engineering, dimensionality reduction, time series analysis, natural language processing, computer vision, A/B testing, experimental design, MLOps, model deployment, AWS SageMaker."""
            },
            {
                "name": "DevOps Engineer", 
                "description": """DevOps engineer specializing in cloud infrastructure automation, AWS Google Cloud Azure, Infrastructure as Code Terraform CloudFormation Ansible, containerization Docker Kubernetes, microservices orchestration, CI/CD pipelines Jenkins GitLab GitHub Actions, blue-green deployments, monitoring Prometheus Grafana ELK stack, security best practices, network security, performance optimization, auto-scaling, cost optimization, disaster recovery."""
            },
            {
                "name": "Frontend Developer",
                "description": """Frontend developer expert in React Vue.js Angular JavaScript TypeScript HTML5 CSS3 responsive design, component-based architecture, state management Redux Vuex, build tools Webpack Vite, testing frameworks Jest Cypress, user experience design, cross-browser compatibility, accessibility standards WCAG, performance optimization, mobile-first development, progressive web applications, API integration GraphQL REST, modern deployment practices."""
            },
            {
                "name": "Security Expert",
                "description": """Cybersecurity expert specializing in penetration testing, vulnerability assessments, network security, application security, cloud security, incident response, encryption technologies, PKI infrastructure, identity access management IAM, multi-factor authentication, compliance frameworks SOC2 ISO27001 GDPR HIPAA, security monitoring SIEM tools, threat intelligence, malware analysis, digital forensics, secure coding practices, security architecture design."""
            },
            {
                "name": "Mobile Developer",
                "description": """Mobile application developer expert in iOS Swift Objective-C, Android Kotlin Java, cross-platform React Native Flutter, mobile UI/UX design, responsive layouts, platform-specific guidelines, app architecture MVVM MVP Clean Architecture, push notifications, location services, camera integration, offline synchronization, mobile payments, app store deployment, mobile analytics, backend integration WebSockets, mobile security data encryption."""
            },
            {
                "name": "Database Expert",
                "description": """Database expert specializing in PostgreSQL MySQL SQL Server MongoDB Cassandra Redis, database design optimization, query optimization, indexing strategies, performance tuning, advanced SQL programming, stored procedures triggers, database administration backup recovery, replication clustering high availability, data modeling normalization, scalable architectures, data warehousing ETL processes, business intelligence, database security access control, data encryption compliance."""
            },
            {
                "name": "AI Engineer",
                "description": """Artificial intelligence engineer expert in machine learning deep learning, computer vision natural language processing, reinforcement learning generative AI, TensorFlow PyTorch Keras, neural networks CNNs RNNs transformers, attention mechanisms, model training hyperparameter tuning, optimization techniques, MLOps practices model versioning, automated training pipelines, model deployment monitoring, data preprocessing feature engineering, large-scale datasets, AI ethics bias detection mitigation."""
            },
            {
                "name": "Cloud Architect",
                "description": """Cloud solutions architect expert in AWS Microsoft Azure Google Cloud Platform, cloud migration strategies, hybrid cloud multi-cloud architectures, Infrastructure as Code Terraform CloudFormation ARM templates, containerization Docker Kubernetes orchestration, serverless computing API gateways, event-driven architectures AWS Lambda Azure Functions, cloud security IAM network security, data encryption compliance, cost optimization performance monitoring, disaster recovery high availability."""
            },
            {
                "name": "QA Engineer",
                "description": """Quality assurance engineer expert in software testing, test automation, performance testing, security testing, web mobile API applications, test planning test case design, comprehensive testing strategies, automation frameworks Selenium Cypress TestNG Jest, API testing Postman REST Assured SoapUI, performance testing JMeter LoadRunner K6, mobile testing cross-browser testing, accessibility testing usability testing, continuous integration continuous testing CI/CT practices, quality gates."""
            }
        ]
        
        # Create 100 agents (10 variations of each base embedding agent)
        for i in range(100):
            base_idx = i % len(base_embedding_agents)
            variation = i // len(base_embedding_agents) + 1
            base_agent = base_embedding_agents[base_idx]
            
            # Add variation-specific terms to the description for embedding
            varied_description = base_agent["description"] + f" specialization level {variation}, {3 + variation * 2} years experience, {10 + variation * 5} projects completed, advanced expertise certification level {variation}, emerging technologies focus, industry best practices implementation."
            
            agent = {
                "@context": "https://projectnanda.org/agentfacts/v1",
                "id": f"did:nanda:agent:embed-{i+1:03d}",
                "agent_id": f"embed-{i+1:03d}",
                "agent_name": f"{base_agent['name']} {variation}",
                "structure_type": "embedding",
                "capabilities": {
                    "description_embedding": self._simulate_embedding(varied_description),
                    "description_text": varied_description,
                    "search_method": "vector_similarity",
                    "embedding_model": "voyage-large-2-simulated",
                    "specialization_level": f"level_{variation}",
                    "experience_years": (variation * 2) + 3
                },
                "description": varied_description[:200] + "...",
                "created_at": datetime.utcnow()
            }
            agents.append(agent)
        
        return agents
    
    def _simulate_embedding(self, text: str) -> List[float]:
        """Simulate embedding vector (in production, use Voyage AI)"""
        # Simple hash-based simulation for testing
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to 384-dimensional vector (Voyage AI embedding size)
        embedding = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0  # Normalize to 0-1
            embedding.append(val)
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[:min(384-len(embedding), len(embedding))])
        
        return embedding[:384]
    
    def populate_test_structures(self):
        """Populate MongoDB with all 3 capability structures"""
        print("🔄 Populating test capability structures...")
        
        # Clear existing test data
        self.mongo_facts.collection.delete_many({"structure_type": {"$exists": True}})
        
        # Create and insert all structures
        all_agents = []
        
        # Structure 1: Keywords
        keywords_agents = self.create_structure_1_keywords()
        all_agents.extend(keywords_agents)
        print(f"✅ Created {len(keywords_agents)} keyword-based agents")
        
        # Structure 2: Descriptions
        description_agents = self.create_structure_2_descriptions()
        all_agents.extend(description_agents)
        print(f"✅ Created {len(description_agents)} description-based agents")
        
        # Structure 3: Embeddings
        embedding_agents = self.create_structure_3_embeddings()
        all_agents.extend(embedding_agents)
        print(f"✅ Created {len(embedding_agents)} embedding-based agents")
        
        # Insert all agents
        if all_agents:
            result = self.mongo_facts.collection.insert_many(all_agents)
            print(f"✅ Inserted {len(result.inserted_ids)} test agents")
        
        return len(all_agents)
    
    def test_search_accuracy_speed(self):
        """Test search accuracy and speed for each structure"""
        print("\n🧪 Testing Search Accuracy and Speed...")
        
        test_queries = [
            "python web development",
            "machine learning data analysis", 
            "cloud infrastructure kubernetes",
            "frontend react javascript",
            "cybersecurity penetration testing"
        ]
        
        results = {
            "keywords": {"times": [], "results": []},
            "description": {"times": [], "results": []}, 
            "embedding": {"times": [], "results": []}
        }
        
        for query in test_queries:
            print(f"\n🔍 Testing query: '{query}'")
            
            # Test each structure type
            for structure_type in ["keywords", "description", "embedding"]:
                start_time = time.time()
                
                # Search agents of this structure type
                search_results = self._search_by_structure(query, structure_type)
                
                search_time = time.time() - start_time
                results[structure_type]["times"].append(search_time)
                results[structure_type]["results"].append(len(search_results))
                
                print(f"  {structure_type:12}: {len(search_results)} results in {search_time:.3f}s")
        
        # Calculate averages
        print("\n📊 Performance Summary:")
        for structure_type, data in results.items():
            avg_time = sum(data["times"]) / len(data["times"])
            avg_results = sum(data["results"]) / len(data["results"])
            print(f"  {structure_type:12}: {avg_time:.3f}s avg, {avg_results:.1f} results avg")
        
        return results
    
    def _search_by_structure(self, query: str, structure_type: str) -> List[Dict[str, Any]]:
        """Search agents by specific structure type"""
        if structure_type == "keywords":
            # Keyword matching
            query_words = query.lower().split()
            pipeline = [
                {"$match": {"structure_type": "keywords"}},
                {"$addFields": {
                    "score": {
                        "$size": {
                            "$setIntersection": [
                                {"$map": {"input": "$capabilities.keywords", "as": "kw", "in": {"$toLower": "$$kw"}}},
                                query_words
                            ]
                        }
                    }
                }},
                {"$match": {"score": {"$gt": 0}}},
                {"$sort": {"score": -1}},
                {"$limit": 10}
            ]
            
        elif structure_type == "description":
            # Text search on descriptions
            pipeline = [
                {"$match": {
                    "structure_type": "description",
                    "$text": {"$search": query}
                }},
                {"$addFields": {"score": {"$meta": "textScore"}}},
                {"$sort": {"score": {"$meta": "textScore"}}},
                {"$limit": 10}
            ]
            
        elif structure_type == "embedding":
            # Simulated vector similarity (in production, use vector search)
            query_embedding = self._simulate_embedding(query)
            pipeline = [
                {"$match": {"structure_type": "embedding"}},
                {"$addFields": {
                    "score": {
                        "$reduce": {
                            "input": {"$range": [0, {"$size": "$capabilities.description_embedding"}]},
                            "initialValue": 0,
                            "in": {
                                "$add": [
                                    "$$value",
                                    {"$multiply": [
                                        {"$arrayElemAt": ["$capabilities.description_embedding", "$$this"]},
                                        {"$arrayElemAt": [query_embedding, "$$this"]}
                                    ]}
                                ]
                            }
                        }
                    }
                }},
                {"$sort": {"score": -1}},
                {"$limit": 10}
            ]
        
        return list(self.mongo_facts.collection.aggregate(pipeline))


if __name__ == "__main__":
    print("🧪 Testing 3 Different Capability Structures")
    
    tester = CapabilityStructureTester()
    
    # Populate test structures
    total_agents = tester.populate_test_structures()
    print(f"\n✅ Total test agents created: {total_agents}")
    
    # Test accuracy and speed
    results = tester.test_search_accuracy_speed()
    
    print("\n🎯 Test completed! Ready for accuracy and speed analysis.")
