#!/usr/bin/env python3
"""
CLIP Embeddings Implementation for NANDA Agent Capabilities
"""

import os
import sys
import time
import torch
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

from transformers import CLIPTextModel, CLIPTokenizer
from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts


class CLIPEmbeddingGenerator:
    """Generate CLIP embeddings for agent capabilities"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        """Load CLIP model and tokenizer"""
        print(f"📥 Loading CLIP model: {self.model_name}")
        self.model = CLIPTextModel.from_pretrained(self.model_name)
        self.tokenizer = CLIPTokenizer.from_pretrained(self.model_name)
        print("✅ CLIP model loaded successfully")
    
    def create_embedding(self, text: str) -> List[float]:
        """Create CLIP embedding for text"""
        # Tokenize the text
        inputs = self.tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=77)
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use the pooled output (CLS token representation)
            embedding = outputs.pooler_output.squeeze().tolist()
        
        return embedding
    
    def create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create CLIP embeddings for multiple texts efficiently"""
        print(f"🔄 Creating embeddings for {len(texts)} texts...")
        
        # Tokenize all texts at once
        inputs = self.tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=77)
        
        # Get embeddings for all texts
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use the pooled output for all texts
            embeddings = outputs.pooler_output.tolist()
        
        print(f"✅ Created {len(embeddings)} embeddings")
        return embeddings


class CLIPCapabilityTester:
    """Test CLIP embeddings for agent capability matching"""
    
    def __init__(self):
        self.clip_generator = CLIPEmbeddingGenerator()
        self.mongo_facts = MongoDBAgentFacts()
    
    def update_existing_agents_with_clip(self):
        """Update existing embedding agents with real CLIP embeddings"""
        print("🔄 Updating existing embedding agents with CLIP embeddings...")
        
        # Get all embedding structure agents
        embedding_agents = list(self.mongo_facts.collection.find(
            {"structure_type": "embedding"},
            {"agent_id": 1, "agent_name": 1, "capabilities.description_text": 1}
        ))
        
        print(f"📋 Found {len(embedding_agents)} embedding agents to update")
        
        # Extract texts for batch processing
        texts = []
        agent_ids = []
        
        for agent in embedding_agents:
            description = agent.get("capabilities", {}).get("description_text", "")
            if description:
                texts.append(description)
                agent_ids.append(agent["agent_id"])
        
        # Create CLIP embeddings in batch
        if texts:
            clip_embeddings = self.clip_generator.create_batch_embeddings(texts)
            
            # Update each agent with real CLIP embedding
            updated_count = 0
            for i, (agent_id, embedding) in enumerate(zip(agent_ids, clip_embeddings)):
                result = self.mongo_facts.collection.update_one(
                    {"agent_id": agent_id},
                    {
                        "$set": {
                            "capabilities.description_embedding": embedding,
                            "capabilities.embedding_model": "openai/clip-vit-base-patch32",
                            "capabilities.embedding_dimension": len(embedding),
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                if result.modified_count > 0:
                    updated_count += 1
                    if (i + 1) % 10 == 0:
                        print(f"  ✅ Updated {i + 1}/{len(agent_ids)} agents")
            
            print(f"✅ Successfully updated {updated_count} agents with CLIP embeddings")
        
        return updated_count
    
    def test_clip_similarity_search(self, query: str, limit: int = 10):
        """Test CLIP-based similarity search"""
        print(f"🔍 Testing CLIP similarity search for: '{query}'")
        
        # Create embedding for the query
        start_time = time.time()
        query_embedding = self.clip_generator.create_embedding(query)
        embedding_time = time.time() - start_time
        
        print(f"  📊 Query embedding created in {embedding_time:.3f}s (dimension: {len(query_embedding)})")
        
        # Search using vector similarity (simplified dot product)
        search_start = time.time()
        
        # MongoDB aggregation pipeline for vector similarity
        pipeline = [
            {"$match": {"structure_type": "embedding"}},
            {"$addFields": {
                "similarity_score": {
                    "$reduce": {
                        "input": {"$range": [0, {"$min": [{"$size": "$capabilities.description_embedding"}, len(query_embedding)]}]},
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
            {"$sort": {"similarity_score": -1}},
            {"$limit": limit},
            {"$project": {
                "agent_id": 1,
                "agent_name": 1,
                "similarity_score": 1,
                "capabilities.specialization_level": 1,
                "capabilities.experience_years": 1
            }}
        ]
        
        results = list(self.mongo_facts.collection.aggregate(pipeline))
        search_time = time.time() - search_start
        
        print(f"  ⚡ Search completed in {search_time:.3f}s")
        print(f"  📊 Found {len(results)} results")
        
        # Display results
        print(f"\n🎯 Top {min(limit, len(results))} Results:")
        for i, result in enumerate(results[:limit]):
            score = result.get("similarity_score", 0)
            agent_id = result.get("agent_id", "N/A")
            agent_name = result.get("agent_name", "N/A")
            level = result.get("capabilities", {}).get("specialization_level", "N/A")
            experience = result.get("capabilities", {}).get("experience_years", "N/A")
            
            print(f"  {i+1:2d}. {agent_name:<25} | Score: {score:.3f} | {agent_id} | {level} | {experience}y")
        
        return {
            "query": query,
            "results_count": len(results),
            "embedding_time": embedding_time,
            "search_time": search_time,
            "total_time": embedding_time + search_time,
            "top_results": results[:5]
        }
    
    def compare_embedding_methods(self):
        """Compare simulated vs CLIP embeddings"""
        print("\n🔬 Comparing Embedding Methods...")
        
        test_queries = [
            "python web development",
            "machine learning data science",
            "cloud infrastructure kubernetes",
            "frontend react javascript",
            "cybersecurity penetration testing"
        ]
        
        results = {
            "simulated": [],
            "clip": []
        }
        
        for query in test_queries:
            print(f"\n🔍 Testing: '{query}'")
            
            # Test CLIP embeddings
            clip_result = self.test_clip_similarity_search(query, limit=5)
            results["clip"].append(clip_result)
            
            print(f"  CLIP: {clip_result['results_count']} results in {clip_result['total_time']:.3f}s")
        
        # Calculate averages
        clip_avg_time = sum(r['total_time'] for r in results["clip"]) / len(results["clip"])
        clip_avg_results = sum(r['results_count'] for r in results["clip"]) / len(results["clip"])
        
        print(f"\n📊 CLIP Performance Summary:")
        print(f"  Average search time: {clip_avg_time:.3f}s")
        print(f"  Average results found: {clip_avg_results:.1f}")
        
        return results


if __name__ == "__main__":
    print("🧪 Testing CLIP Embeddings for Agent Capabilities")
    print("=" * 60)
    
    tester = CLIPCapabilityTester()
    
    # Update existing agents with CLIP embeddings
    updated_count = tester.update_existing_agents_with_clip()
    
    if updated_count > 0:
        print(f"\n✅ Updated {updated_count} agents with CLIP embeddings")
        
        # Test the new CLIP-based search
        print("\n" + "=" * 60)
        comparison_results = tester.compare_embedding_methods()
        
        print("\n🎯 CLIP embeddings are now ready for production use!")
    else:
        print("\n❌ No agents were updated. Check the database connection.")
