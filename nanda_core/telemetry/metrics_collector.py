#!/usr/bin/env python3
"""
Metrics Collector for detailed performance and usage metrics
"""

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

import threading
import time
from datetime import datetime
from typing import Dict, Any, List
from collections import deque, defaultdict


class MetricsCollector:
    """Collects system and application metrics"""

    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.metrics_history = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.custom_metrics = defaultdict(list)
        self.running = False
        self.collector_thread = None
        self.lock = threading.Lock()

    def start_collection(self):
        """Start automatic metrics collection"""
        if not self.running:
            self.running = True
            self.collector_thread = threading.Thread(target=self._collect_loop, daemon=True)
            self.collector_thread.start()

    def stop_collection(self):
        """Stop automatic metrics collection"""
        self.running = False
        if self.collector_thread:
            self.collector_thread.join(timeout=5)

    def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        if not HAS_PSUTIL:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": "psutil not available"
            }

        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            # Network stats (if available)
            try:
                network = psutil.net_io_counters()
                network_stats = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            except:
                network_stats = {}

            return {
                "timestamp": datetime.now().isoformat(),
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                },
                "network": network_stats,
                "process": self._get_process_metrics()
            }
        except Exception as e:
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }

    def _get_process_metrics(self) -> Dict[str, Any]:
        """Get metrics for the current process"""
        if not HAS_PSUTIL:
            return {}

        try:
            process = psutil.Process()
            with process.oneshot():
                return {
                    "pid": process.pid,
                    "cpu_percent": process.cpu_percent(),
                    "memory_info": {
                        "rss": process.memory_info().rss,
                        "vms": process.memory_info().vms
                    },
                    "memory_percent": process.memory_percent(),
                    "num_threads": process.num_threads(),
                    "create_time": process.create_time(),
                    "status": process.status()
                }
        except:
            return {}

    def add_custom_metric(self, name: str, value: Any, tags: Dict[str, str] = None):
        """Add a custom metric"""
        with self.lock:
            metric_entry = {
                "timestamp": datetime.now().isoformat(),
                "value": value,
                "tags": tags or {}
            }
            self.custom_metrics[name].append(metric_entry)

            # Keep only last 1000 entries per metric
            if len(self.custom_metrics[name]) > 1000:
                self.custom_metrics[name] = self.custom_metrics[name][-1000:]

    def get_metric_summary(self, metric_name: str, window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary statistics for a metric over time window"""
        if metric_name not in self.custom_metrics:
            return {}

        cutoff_time = datetime.now().timestamp() - (window_minutes * 60)

        with self.lock:
            recent_values = []
            for entry in self.custom_metrics[metric_name]:
                try:
                    timestamp = datetime.fromisoformat(entry["timestamp"]).timestamp()
                    if timestamp > cutoff_time and isinstance(entry["value"], (int, float)):
                        recent_values.append(entry["value"])
                except:
                    continue

        if not recent_values:
            return {"count": 0}

        return {
            "count": len(recent_values),
            "min": min(recent_values),
            "max": max(recent_values),
            "avg": sum(recent_values) / len(recent_values),
            "sum": sum(recent_values)
        }

    def get_system_health_score(self) -> float:
        """Calculate overall system health score (0-1)"""
        if not self.metrics_history:
            return 0.8  # Default score

        latest = self.metrics_history[-1]
        if "error" in latest:
            return 0.3

        score = 1.0

        # CPU health (lower usage is better)
        cpu_percent = latest.get("cpu", {}).get("percent", 50)
        if cpu_percent > 90:
            score -= 0.3
        elif cpu_percent > 70:
            score -= 0.2
        elif cpu_percent > 50:
            score -= 0.1

        # Memory health
        memory_percent = latest.get("memory", {}).get("percent", 50)
        if memory_percent > 90:
            score -= 0.3
        elif memory_percent > 80:
            score -= 0.2
        elif memory_percent > 70:
            score -= 0.1

        # Disk health
        disk_percent = latest.get("disk", {}).get("percent", 50)
        if disk_percent > 95:
            score -= 0.2
        elif disk_percent > 85:
            score -= 0.1

        return max(0.0, score)

    def get_performance_trends(self, hours: int = 24) -> Dict[str, List[Any]]:
        """Get performance trends over time"""
        trends = {
            "timestamps": [],
            "cpu_percent": [],
            "memory_percent": [],
            "disk_percent": [],
            "health_score": []
        }

        cutoff_time = datetime.now().timestamp() - (hours * 3600)

        for metrics in self.metrics_history:
            try:
                timestamp = datetime.fromisoformat(metrics["timestamp"]).timestamp()
                if timestamp > cutoff_time:
                    trends["timestamps"].append(metrics["timestamp"])
                    trends["cpu_percent"].append(metrics.get("cpu", {}).get("percent", 0))
                    trends["memory_percent"].append(metrics.get("memory", {}).get("percent", 0))
                    trends["disk_percent"].append(metrics.get("disk", {}).get("percent", 0))

                    # Calculate health score for this point
                    health_score = self._calculate_point_health_score(metrics)
                    trends["health_score"].append(health_score)
            except:
                continue

        return trends

    def _calculate_point_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate health score for a single metrics point"""
        if "error" in metrics:
            return 0.3

        score = 1.0
        cpu_percent = metrics.get("cpu", {}).get("percent", 50)
        memory_percent = metrics.get("memory", {}).get("percent", 50)
        disk_percent = metrics.get("disk", {}).get("percent", 50)

        # Simple scoring based on resource usage
        score -= max(0, (cpu_percent - 50) / 100)  # Penalty for high CPU
        score -= max(0, (memory_percent - 70) / 60)  # Penalty for high memory
        score -= max(0, (disk_percent - 80) / 40)  # Penalty for high disk

        return max(0.0, min(1.0, score))

    def _collect_loop(self):
        """Main collection loop"""
        while self.running:
            try:
                metrics = self.collect_system_metrics()
                with self.lock:
                    self.metrics_history.append(metrics)

                time.sleep(self.collection_interval)
            except Exception as e:
                print(f"Metrics collection error: {e}")
                time.sleep(self.collection_interval)

    def export_metrics(self, format: str = "json") -> str:
        """Export collected metrics"""
        import json

        with self.lock:
            data = {
                "system_metrics": list(self.metrics_history),
                "custom_metrics": dict(self.custom_metrics),
                "export_timestamp": datetime.now().isoformat()
            }

        if format.lower() == "json":
            return json.dumps(data, indent=2)
        else:
            return str(data)

    def get_alerts(self) -> List[Dict[str, Any]]:
        """Get system alerts based on thresholds"""
        alerts = []

        if not self.metrics_history:
            return alerts

        latest = self.metrics_history[-1]

        # CPU alerts
        cpu_percent = latest.get("cpu", {}).get("percent", 0)
        if cpu_percent > 90:
            alerts.append({
                "type": "cpu_high",
                "severity": "critical",
                "message": f"CPU usage at {cpu_percent:.1f}%",
                "value": cpu_percent
            })
        elif cpu_percent > 70:
            alerts.append({
                "type": "cpu_medium",
                "severity": "warning",
                "message": f"CPU usage at {cpu_percent:.1f}%",
                "value": cpu_percent
            })

        # Memory alerts
        memory_percent = latest.get("memory", {}).get("percent", 0)
        if memory_percent > 90:
            alerts.append({
                "type": "memory_high",
                "severity": "critical",
                "message": f"Memory usage at {memory_percent:.1f}%",
                "value": memory_percent
            })
        elif memory_percent > 80:
            alerts.append({
                "type": "memory_medium",
                "severity": "warning",
                "message": f"Memory usage at {memory_percent:.1f}%",
                "value": memory_percent
            })

        # Disk alerts
        disk_percent = latest.get("disk", {}).get("percent", 0)
        if disk_percent > 95:
            alerts.append({
                "type": "disk_full",
                "severity": "critical",
                "message": f"Disk usage at {disk_percent:.1f}%",
                "value": disk_percent
            })
        elif disk_percent > 85:
            alerts.append({
                "type": "disk_high",
                "severity": "warning",
                "message": f"Disk usage at {disk_percent:.1f}%",
                "value": disk_percent
            })

        return alerts