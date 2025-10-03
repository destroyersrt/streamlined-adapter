#!/usr/bin/env python3
"""
Main Telemetry System for comprehensive monitoring and metrics collection
"""

import json
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from .metrics_collector import MetricsCollector
from .health_monitor import HealthMonitor
from .mongodb_telemetry import MongoDBTelemetryStorage, QueryTelemetry


@dataclass
class TelemetryEvent:
    """Structure for telemetry events"""
    timestamp: str
    event_type: str
    agent_id: str
    data: Dict[str, Any]
    session_id: Optional[str] = None


class TelemetrySystem:
    """Comprehensive telemetry system for monitoring and analytics"""

    def __init__(self, agent_id: str, log_dir: str = "telemetry_logs"):
        self.agent_id = agent_id
        self.log_dir = log_dir
        self.session_id = self._generate_session_id()

        # Initialize components
        self.metrics_collector = MetricsCollector()
        self.health_monitor = HealthMonitor(agent_id)

        # Event storage
        self.event_queue = deque(maxlen=10000)  # Keep last 10k events in memory
        self.event_counts = defaultdict(int)

        # Performance tracking
        self.response_times = deque(maxlen=1000)  # Last 1000 response times
        self.error_counts = defaultdict(int)

        # Threading for async operations
        self.lock = threading.Lock()
        self.background_thread = None
        self.running = False

        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)

        # DISABLED: Agents should NOT connect directly to MongoDB
        # Telemetry should go through registry API or be file-based only
        self.mongodb_telemetry = None
        self.use_mongodb_telemetry = False
        print("📝 Using file-based telemetry storage (proper architecture)")

        # Start background processing
        self.start()

    def start(self):
        """Start the telemetry system"""
        if not self.running:
            self.running = True
            self.background_thread = threading.Thread(target=self._background_worker, daemon=True)
            self.background_thread.start()
            self.log_event("system", "telemetry_started", {"agent_id": self.agent_id})

    def stop(self):
        """Stop the telemetry system"""
        if self.running:
            self.running = False
            self.log_event("system", "telemetry_stopped", {"agent_id": self.agent_id})
            if self.background_thread:
                self.background_thread.join(timeout=5)

    def log_event(self, event_type: str, event_name: str, data: Dict[str, Any] = None):
        """Log a telemetry event"""
        event = TelemetryEvent(
            timestamp=datetime.now().isoformat(),
            event_type=event_type,
            agent_id=self.agent_id,
            data=data or {},
            session_id=self.session_id
        )

        with self.lock:
            self.event_queue.append(event)
            self.event_counts[f"{event_type}:{event_name}"] += 1

        # Write to disk asynchronously
        self._write_event_to_disk(event)

    def log_message_received(self, agent_id: str, conversation_id: str, message_type: str = "text"):
        """Log when a message is received"""
        self.log_event("message", "received", {
            "conversation_id": conversation_id,
            "message_type": message_type,
            "target_agent": agent_id
        })

    def log_message_sent(self, target_agent_id: str, conversation_id: str, success: bool = True):
        """Log when a message is sent to another agent"""
        self.log_event("message", "sent", {
            "target_agent_id": target_agent_id,
            "conversation_id": conversation_id,
            "success": success
        })

    def log_mcp_query(self, server_name: str, query: str, success: bool = True, response_time: float = None):
        """Log MCP server queries"""
        data = {
            "server_name": server_name,
            "query_length": len(query),
            "success": success
        }
        if response_time:
            data["response_time"] = response_time

        self.log_event("mcp", "query", data)

    def log_agent_discovery(self, task_description: str, agents_found: int, search_time: float):
        """Log agent discovery operations"""
        self.log_event("discovery", "search", {
            "task_length": len(task_description),
            "agents_found": agents_found,
            "search_time": search_time
        })

    def log_structured_query(self, query_text: str, query_type: str, conversation_id: str,
                           search_time: float, agents_found: int, search_method: str,
                           top_agents: List[Dict[str, Any]], result_quality_score: float,
                           response_time: float, success: bool = True, error_message: str = None):
        """Log structured query telemetry to MongoDB"""
        if not self.use_mongodb_telemetry:
            return
        
        try:
            import uuid
            import psutil
            
            # Get system metrics
            process = psutil.Process()
            memory_usage = process.memory_info().rss / (1024 * 1024)  # MB
            cpu_usage = process.cpu_percent()
            
            # Create structured telemetry
            query_telemetry = QueryTelemetry(
                query_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                agent_id=self.agent_id,
                session_id=self.session_id,
                query_text=query_text,
                query_type=query_type,
                conversation_id=conversation_id,
                search_time=search_time,
                agents_found=agents_found,
                search_method=search_method,
                top_agents=top_agents,
                result_quality_score=result_quality_score,
                memory_usage_mb=memory_usage,
                cpu_usage_percent=cpu_usage,
                response_time=response_time,
                success=success,
                error_message=error_message
            )
            
            # Store in MongoDB
            self.mongodb_telemetry.store_query_telemetry(query_telemetry)
            
        except Exception as e:
            print(f"⚠️ Error logging structured query telemetry: {e}")

    def log_error(self, error_message: str, context: Dict[str, Any] = None):
        """Log errors and exceptions"""
        with self.lock:
            self.error_counts[error_message] += 1

        self.log_event("error", "exception", {
            "error_message": error_message,
            "context": context or {},
            "error_count": self.error_counts[error_message]
        })

    def log_response_time(self, duration_seconds: float, operation: str = "message_handling"):
        """Log response times for performance monitoring"""
        with self.lock:
            self.response_times.append(duration_seconds)

        self.log_event("performance", "response_time", {
            "duration_seconds": duration_seconds,
            "operation": operation
        })

    def log_registry_interaction(self, operation: str, success: bool = True, response_time: float = None):
        """Log interactions with the registry"""
        data = {
            "operation": operation,
            "success": success
        }
        if response_time:
            data["response_time"] = response_time

        self.log_event("registry", "interaction", data)

    def get_metrics_summary(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get summary of metrics for the specified time window"""
        cutoff_time = datetime.now() - timedelta(hours=time_window_hours)

        with self.lock:
            # Filter events within time window
            recent_events = [
                event for event in self.event_queue
                if datetime.fromisoformat(event.timestamp) > cutoff_time
            ]

        # Aggregate metrics
        metrics = {
            "time_window_hours": time_window_hours,
            "total_events": len(recent_events),
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        }

        # Event type breakdown
        event_types = defaultdict(int)
        for event in recent_events:
            event_types[event.event_type] += 1
        metrics["event_types"] = dict(event_types)

        # Message statistics
        message_events = [e for e in recent_events if e.event_type == "message"]
        metrics["message_stats"] = {
            "total_messages": len(message_events),
            "messages_received": len([e for e in message_events if "received" in e.data.get("event_name", "")]),
            "messages_sent": len([e for e in message_events if "sent" in e.data.get("event_name", "")])
        }

        # Performance metrics
        if self.response_times:
            times = list(self.response_times)
            metrics["performance"] = {
                "avg_response_time": sum(times) / len(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "total_requests": len(times)
            }

        # Error statistics
        error_events = [e for e in recent_events if e.event_type == "error"]
        metrics["error_stats"] = {
            "total_errors": len(error_events),
            "unique_errors": len(set(e.data.get("error_message", "") for e in error_events))
        }

        # Health status
        metrics["health"] = self.health_monitor.get_health_status()

        return metrics

    def get_performance_data(self) -> Dict[str, Any]:
        """Get performance data for agent ranking"""
        if not self.response_times:
            return {
                "success_rate": 0.8,  # Default values
                "avg_response_time": 5.0,
                "reliability": 0.8
            }

        times = list(self.response_times)
        recent_events = list(self.event_queue)[-1000:]  # Last 1000 events

        # Calculate success rate
        error_events = [e for e in recent_events if e.event_type == "error"]
        total_operations = len(recent_events)
        success_rate = (total_operations - len(error_events)) / max(total_operations, 1)

        # Calculate reliability based on consistent performance
        time_variance = self._calculate_variance(times)
        reliability = max(0.0, 1.0 - (time_variance / 10.0))  # Normalize variance

        return {
            "success_rate": success_rate,
            "avg_response_time": sum(times) / len(times),
            "reliability": reliability,
            "total_operations": total_operations,
            "error_count": len(error_events)
        }

    def export_metrics(self, format: str = "json", time_window_hours: int = 24) -> str:
        """Export metrics in the specified format"""
        metrics = self.get_metrics_summary(time_window_hours)

        if format.lower() == "json":
            return json.dumps(metrics, indent=2)
        elif format.lower() == "csv":
            return self._metrics_to_csv(metrics)
        else:
            return str(metrics)

    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_monitor.get_health_status()

    def _generate_session_id(self) -> str:
        """Generate a unique session ID"""
        import uuid
        return f"{self.agent_id}_{int(time.time())}_{str(uuid.uuid4())[:8]}"

    def _write_event_to_disk(self, event: TelemetryEvent):
        """Write event to disk storage"""
        try:
            # Create date-based log file
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = os.path.join(self.log_dir, f"events_{date_str}.jsonl")

            with open(log_file, "a") as f:
                f.write(json.dumps(asdict(event)) + "\n")

        except Exception as e:
            # Don't let telemetry errors break the main application
            print(f"Telemetry write error: {e}")

    def _background_worker(self):
        """Background worker for periodic tasks"""
        while self.running:
            try:
                # Update health metrics every minute
                self.health_monitor.update_health_metrics()

                # Log system metrics every 5 minutes
                if int(time.time()) % 300 == 0:
                    self.log_event("system", "health_check", self.get_health_status())

                time.sleep(60)  # Check every minute

            except Exception as e:
                print(f"Telemetry background worker error: {e}")
                time.sleep(60)

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance

    def _metrics_to_csv(self, metrics: Dict[str, Any]) -> str:
        """Convert metrics to CSV format"""
        lines = ["metric,value"]

        def flatten_dict(d, prefix=""):
            for k, v in d.items():
                key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    lines.extend(flatten_dict(v, key))
                else:
                    lines.append(f"{key},{v}")

        flatten_dict(metrics)
        return "\n".join(lines)

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()