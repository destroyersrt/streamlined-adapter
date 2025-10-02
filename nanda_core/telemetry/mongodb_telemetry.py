#!/usr/bin/env python3
"""
MongoDB Telemetry Storage - Structured telemetry data collection
"""

import os
from typing import Dict, List, Any, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, asdict

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed. Using system environment variables only.")


@dataclass
class QueryTelemetry:
    """Structured telemetry data for a single query"""
    # Query Information
    query_id: str
    timestamp: datetime
    agent_id: str
    session_id: str
    
    # Query Details
    query_text: str
    query_type: str  # "search", "a2a", "system"
    conversation_id: str
    
    # Search Performance
    search_time: float
    agents_found: int
    search_method: str  # "mongodb", "registry", "fallback"
    
    # Results
    top_agents: List[Dict[str, Any]]  # Top 5 agents with scores
    result_quality_score: float  # 0-1 based on relevance
    
    # System Metrics
    memory_usage_mb: float
    cpu_usage_percent: float
    response_time: float
    
    # Context
    user_location: Optional[str] = None
    user_agent: Optional[str] = None
    error_message: Optional[str] = None
    success: bool = True


@dataclass
class AgentPerformanceMetrics:
    """Agent performance metrics over time"""
    agent_id: str
    timestamp: datetime
    period: str  # "hourly", "daily", "weekly"
    
    # Query Statistics
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_response_time: float
    
    # Search Performance
    average_search_time: float
    average_agents_found: float
    mongodb_searches: int
    registry_searches: int
    fallback_searches: int
    
    # Quality Metrics
    average_result_quality: float
    user_satisfaction_score: float  # Based on follow-up queries
    
    # System Health
    average_memory_usage: float
    average_cpu_usage: float
    uptime_percentage: float
    error_rate: float


class MongoDBTelemetryStorage:
    """MongoDB storage for structured telemetry data"""
    
    def __init__(self, mongodb_uri: str = None, database_name: str = "nanda_telemetry"):
        self.mongodb_uri = mongodb_uri or os.getenv("MONGODB_TELEMETRY_URI", "mongodb://localhost:27017/")
        self.database_name = database_name
        self.client = None
        self.db = None
        self.queries_collection = None
        self.metrics_collection = None
        self._connect()
    
    def _connect(self):
        """Connect to MongoDB and setup collections"""
        try:
            self.client = MongoClient(self.mongodb_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database_name]
            
            # Collections
            self.queries_collection = self.db.query_telemetry
            self.metrics_collection = self.db.agent_metrics
            
            # Test connection
            self.client.admin.command('ping')
            
            # Create indexes for better performance
            self._create_indexes()
            
            print(f"✅ Connected to MongoDB telemetry database: {self.database_name}")
            
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB telemetry: {e}")
            raise
    
    def _create_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Query telemetry indexes
            self.queries_collection.create_index([("agent_id", ASCENDING), ("timestamp", DESCENDING)])
            self.queries_collection.create_index([("query_type", ASCENDING), ("timestamp", DESCENDING)])
            self.queries_collection.create_index([("session_id", ASCENDING)])
            self.queries_collection.create_index([("conversation_id", ASCENDING)])
            self.queries_collection.create_index([("search_time", DESCENDING)])
            self.queries_collection.create_index([("result_quality_score", DESCENDING)])
            
            # Agent metrics indexes
            self.metrics_collection.create_index([("agent_id", ASCENDING), ("period", ASCENDING), ("timestamp", DESCENDING)])
            self.metrics_collection.create_index([("timestamp", DESCENDING)])
            
            print("✅ Created telemetry indexes")
            
        except Exception as e:
            print(f"⚠️ Index creation warning: {e}")
    
    def store_query_telemetry(self, telemetry: QueryTelemetry):
        """Store query telemetry data"""
        try:
            doc = asdict(telemetry)
            # Convert datetime to ISO string for MongoDB
            doc['timestamp'] = telemetry.timestamp.isoformat()
            
            result = self.queries_collection.insert_one(doc)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error storing query telemetry: {e}")
            return None
    
    def store_agent_metrics(self, metrics: AgentPerformanceMetrics):
        """Store agent performance metrics"""
        try:
            doc = asdict(metrics)
            # Convert datetime to ISO string for MongoDB
            doc['timestamp'] = metrics.timestamp.isoformat()
            
            # Upsert based on agent_id, period, and timestamp (rounded to hour/day)
            query = {
                "agent_id": metrics.agent_id,
                "period": metrics.period,
                "timestamp": doc['timestamp']
            }
            
            result = self.metrics_collection.replace_one(query, doc, upsert=True)
            return result.upserted_id or result.modified_count
            
        except Exception as e:
            print(f"❌ Error storing agent metrics: {e}")
            return None
    
    def get_query_analytics(self, agent_id: str = None, hours: int = 24) -> Dict[str, Any]:
        """Get query analytics for the specified time period"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Build query filter
            query_filter = {"timestamp": {"$gte": cutoff_time.isoformat()}}
            if agent_id:
                query_filter["agent_id"] = agent_id
            
            # Aggregation pipeline
            pipeline = [
                {"$match": query_filter},
                {"$group": {
                    "_id": None,
                    "total_queries": {"$sum": 1},
                    "successful_queries": {"$sum": {"$cond": ["$success", 1, 0]}},
                    "failed_queries": {"$sum": {"$cond": ["$success", 0, 1]}},
                    "avg_search_time": {"$avg": "$search_time"},
                    "avg_response_time": {"$avg": "$response_time"},
                    "avg_agents_found": {"$avg": "$agents_found"},
                    "avg_result_quality": {"$avg": "$result_quality_score"},
                    "mongodb_searches": {"$sum": {"$cond": [{"$eq": ["$search_method", "mongodb"]}, 1, 0]}},
                    "registry_searches": {"$sum": {"$cond": [{"$eq": ["$search_method", "registry"]}, 1, 0]}},
                    "fallback_searches": {"$sum": {"$cond": [{"$eq": ["$search_method", "fallback"]}, 1, 0]}},
                    "unique_sessions": {"$addToSet": "$session_id"},
                    "query_types": {"$addToSet": "$query_type"}
                }},
                {"$project": {
                    "_id": 0,
                    "total_queries": 1,
                    "successful_queries": 1,
                    "failed_queries": 1,
                    "success_rate": {"$divide": ["$successful_queries", "$total_queries"]},
                    "avg_search_time": {"$round": ["$avg_search_time", 3]},
                    "avg_response_time": {"$round": ["$avg_response_time", 3]},
                    "avg_agents_found": {"$round": ["$avg_agents_found", 1]},
                    "avg_result_quality": {"$round": ["$avg_result_quality", 3]},
                    "search_method_distribution": {
                        "mongodb": "$mongodb_searches",
                        "registry": "$registry_searches", 
                        "fallback": "$fallback_searches"
                    },
                    "unique_sessions": {"$size": "$unique_sessions"},
                    "query_types": 1
                }}
            ]
            
            result = list(self.queries_collection.aggregate(pipeline))
            
            if result:
                analytics = result[0]
                analytics["time_period_hours"] = hours
                analytics["agent_id"] = agent_id or "all_agents"
                analytics["generated_at"] = datetime.utcnow().isoformat()
                return analytics
            else:
                return {
                    "total_queries": 0,
                    "message": "No data found for the specified period",
                    "time_period_hours": hours,
                    "agent_id": agent_id or "all_agents"
                }
                
        except Exception as e:
            print(f"❌ Error getting query analytics: {e}")
            return {"error": str(e)}
    
    def get_search_performance_trends(self, agent_id: str = None, days: int = 7) -> List[Dict[str, Any]]:
        """Get search performance trends over time"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            
            query_filter = {"timestamp": {"$gte": cutoff_time.isoformat()}}
            if agent_id:
                query_filter["agent_id"] = agent_id
            
            pipeline = [
                {"$match": query_filter},
                {"$group": {
                    "_id": {
                        "date": {"$dateToString": {"format": "%Y-%m-%d", "date": {"$dateFromString": {"dateString": "$timestamp"}}}},
                        "hour": {"$dateToString": {"format": "%H", "date": {"$dateFromString": {"dateString": "$timestamp"}}}}
                    },
                    "queries": {"$sum": 1},
                    "avg_search_time": {"$avg": "$search_time"},
                    "avg_agents_found": {"$avg": "$agents_found"},
                    "avg_quality": {"$avg": "$result_quality_score"},
                    "success_rate": {"$avg": {"$cond": ["$success", 1, 0]}}
                }},
                {"$sort": {"_id.date": 1, "_id.hour": 1}},
                {"$project": {
                    "_id": 0,
                    "datetime": {"$concat": ["$_id.date", "T", "$_id.hour", ":00:00Z"]},
                    "queries": 1,
                    "avg_search_time": {"$round": ["$avg_search_time", 3]},
                    "avg_agents_found": {"$round": ["$avg_agents_found", 1]},
                    "avg_quality": {"$round": ["$avg_quality", 3]},
                    "success_rate": {"$round": ["$success_rate", 3]}
                }}
            ]
            
            return list(self.queries_collection.aggregate(pipeline))
            
        except Exception as e:
            print(f"❌ Error getting performance trends: {e}")
            return []
    
    def get_top_queries(self, agent_id: str = None, hours: int = 24, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common queries"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            query_filter = {"timestamp": {"$gte": cutoff_time.isoformat()}}
            if agent_id:
                query_filter["agent_id"] = agent_id
            
            pipeline = [
                {"$match": query_filter},
                {"$group": {
                    "_id": "$query_text",
                    "count": {"$sum": 1},
                    "avg_search_time": {"$avg": "$search_time"},
                    "avg_agents_found": {"$avg": "$agents_found"},
                    "avg_quality": {"$avg": "$result_quality_score"},
                    "last_queried": {"$max": "$timestamp"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": limit},
                {"$project": {
                    "_id": 0,
                    "query_text": "$_id",
                    "count": 1,
                    "avg_search_time": {"$round": ["$avg_search_time", 3]},
                    "avg_agents_found": {"$round": ["$avg_agents_found", 1]},
                    "avg_quality": {"$round": ["$avg_quality", 3]},
                    "last_queried": 1
                }}
            ]
            
            return list(self.queries_collection.aggregate(pipeline))
            
        except Exception as e:
            print(f"❌ Error getting top queries: {e}")
            return []
    
    def get_agent_comparison(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Compare performance across different agents"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            pipeline = [
                {"$match": {"timestamp": {"$gte": cutoff_time.isoformat()}}},
                {"$group": {
                    "_id": "$agent_id",
                    "total_queries": {"$sum": 1},
                    "success_rate": {"$avg": {"$cond": ["$success", 1, 0]}},
                    "avg_search_time": {"$avg": "$search_time"},
                    "avg_response_time": {"$avg": "$response_time"},
                    "avg_agents_found": {"$avg": "$agents_found"},
                    "avg_quality": {"$avg": "$result_quality_score"},
                    "unique_sessions": {"$addToSet": "$session_id"}
                }},
                {"$project": {
                    "_id": 0,
                    "agent_id": "$_id",
                    "total_queries": 1,
                    "success_rate": {"$round": ["$success_rate", 3]},
                    "avg_search_time": {"$round": ["$avg_search_time", 3]},
                    "avg_response_time": {"$round": ["$avg_response_time", 3]},
                    "avg_agents_found": {"$round": ["$avg_agents_found", 1]},
                    "avg_quality": {"$round": ["$avg_quality", 3]},
                    "unique_sessions": {"$size": "$unique_sessions"}
                }},
                {"$sort": {"total_queries": -1}}
            ]
            
            return list(self.queries_collection.aggregate(pipeline))
            
        except Exception as e:
            print(f"❌ Error getting agent comparison: {e}")
            return []
    
    def cleanup_old_data(self, days_to_keep: int = 30):
        """Clean up old telemetry data"""
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Delete old query telemetry
            query_result = self.queries_collection.delete_many({
                "timestamp": {"$lt": cutoff_time.isoformat()}
            })
            
            # Delete old metrics
            metrics_result = self.metrics_collection.delete_many({
                "timestamp": {"$lt": cutoff_time.isoformat()}
            })
            
            print(f"🧹 Cleaned up {query_result.deleted_count} old query records")
            print(f"🧹 Cleaned up {metrics_result.deleted_count} old metric records")
            
            return {
                "queries_deleted": query_result.deleted_count,
                "metrics_deleted": metrics_result.deleted_count
            }
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return {"error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the telemetry collections"""
        try:
            query_stats = self.db.command("collStats", "query_telemetry")
            metrics_stats = self.db.command("collStats", "agent_metrics")
            
            return {
                "query_telemetry": {
                    "documents": query_stats.get("count", 0),
                    "size_mb": round(query_stats.get("size", 0) / (1024 * 1024), 2),
                    "avg_doc_size": query_stats.get("avgObjSize", 0)
                },
                "agent_metrics": {
                    "documents": metrics_stats.get("count", 0),
                    "size_mb": round(metrics_stats.get("size", 0) / (1024 * 1024), 2),
                    "avg_doc_size": metrics_stats.get("avgObjSize", 0)
                },
                "total_size_mb": round((query_stats.get("size", 0) + metrics_stats.get("size", 0)) / (1024 * 1024), 2)
            }
            
        except Exception as e:
            print(f"❌ Error getting collection stats: {e}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test the MongoDB telemetry system
    print("🧪 Testing MongoDB Telemetry Storage")
    
    try:
        # Initialize storage
        telemetry_db = MongoDBTelemetryStorage()
        
        # Create sample query telemetry
        sample_query = QueryTelemetry(
            query_id="test_001",
            timestamp=datetime.utcnow(),
            agent_id="enhanced-data-scientist",
            session_id="test_session_123",
            query_text="python expert",
            query_type="search",
            conversation_id="test_conv_456",
            search_time=0.75,
            agents_found=5,
            search_method="mongodb",
            top_agents=[
                {"agent_id": "python-expert", "score": 0.95},
                {"agent_id": "data-scientist", "score": 0.85}
            ],
            result_quality_score=0.9,
            memory_usage_mb=128.5,
            cpu_usage_percent=15.2,
            response_time=0.8,
            success=True
        )
        
        # Store sample data
        query_id = telemetry_db.store_query_telemetry(sample_query)
        print(f"✅ Stored query telemetry: {query_id}")
        
        # Get analytics
        analytics = telemetry_db.get_query_analytics(hours=1)
        print(f"📊 Analytics: {analytics}")
        
        # Get collection stats
        stats = telemetry_db.get_collection_stats()
        print(f"📈 Collection stats: {stats}")
        
        print("✅ MongoDB telemetry system test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
