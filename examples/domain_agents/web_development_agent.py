#!/usr/bin/env python3
"""
Web Development Domain Agent

This agent specializes in full-stack web development, including React, Node.js, and modern web technologies.
It can answer domain-specific questions about web development, performance optimization, and deployment.
"""

import os
import sys
import json
from typing import Dict, Any

# Add the parent directory to the path so we can import nanda_core
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nanda_core.core.adapter import NANDA

class WebDevelopmentAgent:
    """Web Development domain expert agent"""
    
    def __init__(self, agent_id: str, structure_type: str):
        self.agent_id = agent_id
        self.structure_type = structure_type
        
        # Domain-specific knowledge base
        self.knowledge_base = {
            "react_optimization": "To optimize React applications: 1) Use React.memo() for component memoization, 2) Implement useMemo() and useCallback() for expensive calculations, 3) Code splitting with React.lazy() and Suspense, 4) Optimize bundle size with tree shaking, 5) Use React DevTools Profiler to identify bottlenecks.",
            
            "serverless_architecture": "Serverless architecture in web development involves using cloud functions (AWS Lambda, Vercel Functions) for backend logic. Benefits include automatic scaling, pay-per-use pricing, and reduced infrastructure management. Consider cold starts, vendor lock-in, and debugging challenges.",
            
            "api_security": "RESTful API security best practices: 1) Use HTTPS everywhere, 2) Implement proper authentication (JWT, OAuth), 3) Input validation and sanitization, 4) Rate limiting and throttling, 5) CORS configuration, 6) SQL injection prevention, 7) Regular security audits and dependency updates.",
            
            "cicd_webapp": "For web app CI/CD: 1) Use Git workflows (feature branches, pull requests), 2) Automated testing (unit, integration, e2e), 3) Build automation (webpack, Vite), 4) Deployment pipelines (GitHub Actions, GitLab CI), 5) Environment management (staging, production), 6) Monitoring and rollback strategies.",
            
            "state_management": "For complex front-end state management: 1) Redux Toolkit for predictable state updates, 2) Zustand for simpler state needs, 3) React Query for server state, 4) Context API for component tree state, 5) Consider state colocation and avoid over-engineering."
        }
        
        # Capability structure based on type
        if structure_type == "keywords":
            self.capabilities = {
                "keywords": ["web development", "full stack", "react", "node.js", "javascript", "api"],
                "search_method": "keyword_match"
            }
        elif structure_type == "description":
            self.capabilities = {
                "description_text": "Skilled in front-end and back-end web development, including frameworks like React and Node.js. Expert in modern JavaScript, API development, database integration, and deployment strategies.",
                "search_method": "text_search"
            }
        elif structure_type == "embedding":
            self.capabilities = {
                "description_text": "Comprehensive full-stack web developer with expertise in modern JavaScript frameworks, server-side technologies, database design, API architecture, performance optimization, security best practices, and DevOps for web applications.",
                "search_method": "embedding_search"
            }
    
    def agent_logic(self, message: str, conversation_id: str) -> str:
        """Process incoming messages and provide web development expertise"""
        
        message_lower = message.lower()
        
        # Handle domain-specific questions
        if "react" in message_lower and ("optimize" in message_lower or "performance" in message_lower):
            return f"💻 Web Dev Expert ({self.structure_type}): {self.knowledge_base['react_optimization']}"
        
        elif "serverless" in message_lower or "serverless architecture" in message_lower:
            return f"💻 Web Dev Expert ({self.structure_type}): {self.knowledge_base['serverless_architecture']}"
        
        elif "security" in message_lower and ("api" in message_lower or "restful" in message_lower):
            return f"💻 Web Dev Expert ({self.structure_type}): {self.knowledge_base['api_security']}"
        
        elif "ci/cd" in message_lower or "continuous integration" in message_lower or "deployment" in message_lower:
            return f"💻 Web Dev Expert ({self.structure_type}): {self.knowledge_base['cicd_webapp']}"
        
        elif "state management" in message_lower or ("state" in message_lower and "front" in message_lower):
            return f"💻 Web Dev Expert ({self.structure_type}): {self.knowledge_base['state_management']}"
        
        # General web development response
        elif any(keyword in message_lower for keyword in ["web", "frontend", "backend", "javascript", "react", "node", "api", "html", "css"]):
            return f"💻 Web Dev Expert ({self.structure_type}): I specialize in full-stack web development. I can help with React, Node.js, API design, database integration, performance optimization, security, and deployment. What web development challenge are you facing?"
        
        # Default response
        return f"💻 Web Dev Expert ({self.structure_type}): Hello! I'm a full-stack web development specialist. I can help with modern JavaScript frameworks, server-side development, API architecture, and deployment strategies. How can I assist with your web development project?"

def main():
    """Main function to run the web development agent"""
    
    # Get agent configuration from environment or command line
    agent_id = os.getenv("AGENT_ID", "web-dev-agent-001")
    structure_type = os.getenv("STRUCTURE_TYPE", "keywords")  # keywords, description, or embedding
    port = int(os.getenv("PORT", "6000"))
    
    print(f"🚀 Starting Web Development Agent: {agent_id}")
    print(f"📊 Structure Type: {structure_type}")
    print(f"🔌 Port: {port}")
    
    # Create the domain agent
    domain_agent = WebDevelopmentAgent(agent_id, structure_type)
    
    # Create and start the NANDA agent
    nanda = NANDA(
        agent_id=agent_id,
        agent_logic=domain_agent.agent_logic,
        port=port,
        registry_url="http://capregistry.duckdns.org:6900"
    )
    
    # Add domain-specific metadata for registration
    nanda.metadata = {
        "domain": "web_development",
        "specialization": "Full-Stack Web Development",
        "capabilities": domain_agent.capabilities,
        "structure_type": structure_type,
        "description": f"Skilled in front-end and back-end web development, including frameworks like React and Node.js. ({structure_type} structure)",
        "tags": ["web-development", "full-stack", "react", "nodejs", "javascript", "api"]
    }
    
    print(f"🎯 Agent ready to serve web development expertise!")
    nanda.run()

if __name__ == "__main__":
    main()
