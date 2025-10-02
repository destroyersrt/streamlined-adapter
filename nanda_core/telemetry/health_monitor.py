#!/usr/bin/env python3
"""
Health Monitor for system and application health checks
"""

import requests
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    name: str
    status: HealthStatus
    message: str
    timestamp: str
    response_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class HealthMonitor:
    """Monitors system and application health"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.health_checks = {}
        self.check_history = {}
        self.lock = threading.Lock()

        # Health check configurations
        self.check_configs = {
            "registry_connectivity": {
                "interval": 300,  # 5 minutes
                "timeout": 10,
                "enabled": True
            },
            "memory_usage": {
                "interval": 60,  # 1 minute
                "threshold_warning": 80,
                "threshold_critical": 90,
                "enabled": True
            },
            "disk_space": {
                "interval": 300,  # 5 minutes
                "threshold_warning": 85,
                "threshold_critical": 95,
                "enabled": True
            },
            "response_time": {
                "interval": 60,  # 1 minute
                "threshold_warning": 5.0,  # seconds
                "threshold_critical": 10.0,
                "enabled": True
            }
        }

    def run_health_check(self, check_name: str) -> HealthCheck:
        """Run a specific health check"""
        start_time = time.time()

        try:
            if check_name == "registry_connectivity":
                return self._check_registry_connectivity()
            elif check_name == "memory_usage":
                return self._check_memory_usage()
            elif check_name == "disk_space":
                return self._check_disk_space()
            elif check_name == "response_time":
                return self._check_response_time()
            else:
                return HealthCheck(
                    name=check_name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Unknown health check: {check_name}",
                    timestamp=datetime.now().isoformat()
                )
        except Exception as e:
            return HealthCheck(
                name=check_name,
                status=HealthStatus.CRITICAL,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time
            )

    def run_all_health_checks(self) -> Dict[str, HealthCheck]:
        """Run all enabled health checks"""
        results = {}

        for check_name, config in self.check_configs.items():
            if config.get("enabled", True):
                results[check_name] = self.run_health_check(check_name)

        with self.lock:
            self.health_checks.update(results)

        return results

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        with self.lock:
            checks = dict(self.health_checks)

        if not checks:
            return {
                "overall_status": HealthStatus.UNKNOWN.value,
                "message": "No health checks available",
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id
            }

        # Determine overall status
        statuses = [check.status for check in checks.values()]

        if HealthStatus.CRITICAL in statuses:
            overall_status = HealthStatus.CRITICAL
        elif HealthStatus.WARNING in statuses:
            overall_status = HealthStatus.WARNING
        elif all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
        else:
            overall_status = HealthStatus.WARNING

        # Generate summary message
        healthy_count = sum(1 for s in statuses if s == HealthStatus.HEALTHY)
        warning_count = sum(1 for s in statuses if s == HealthStatus.WARNING)
        critical_count = sum(1 for s in statuses if s == HealthStatus.CRITICAL)

        message = f"{healthy_count} healthy, {warning_count} warnings, {critical_count} critical"

        return {
            "overall_status": overall_status.value,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "agent_id": self.agent_id,
            "checks": {name: {
                "status": check.status.value,
                "message": check.message,
                "timestamp": check.timestamp,
                "response_time": check.response_time
            } for name, check in checks.items()},
            "summary": {
                "total_checks": len(checks),
                "healthy": healthy_count,
                "warnings": warning_count,
                "critical": critical_count
            }
        }

    def update_health_metrics(self):
        """Update health metrics (called periodically)"""
        current_time = time.time()

        for check_name, config in self.check_configs.items():
            if not config.get("enabled", True):
                continue

            # Check if it's time to run this health check
            last_check_time = getattr(self, f"_last_{check_name}_check", 0)
            interval = config.get("interval", 300)

            if current_time - last_check_time >= interval:
                check_result = self.run_health_check(check_name)

                with self.lock:
                    self.health_checks[check_name] = check_result

                    # Store in history
                    if check_name not in self.check_history:
                        self.check_history[check_name] = []

                    self.check_history[check_name].append(check_result)

                    # Keep only last 100 results per check
                    if len(self.check_history[check_name]) > 100:
                        self.check_history[check_name] = self.check_history[check_name][-100:]

                setattr(self, f"_last_{check_name}_check", current_time)

    def _check_registry_connectivity(self) -> HealthCheck:
        """Check connectivity to the registry"""
        registry_url = self._get_registry_url()
        start_time = time.time()

        try:
            response = requests.get(f"{registry_url}/health", timeout=10, verify=False)
            response_time = time.time() - start_time

            if response.status_code == 200:
                return HealthCheck(
                    name="registry_connectivity",
                    status=HealthStatus.HEALTHY,
                    message="Registry is accessible",
                    timestamp=datetime.now().isoformat(),
                    response_time=response_time
                )
            else:
                return HealthCheck(
                    name="registry_connectivity",
                    status=HealthStatus.WARNING,
                    message=f"Registry returned status {response.status_code}",
                    timestamp=datetime.now().isoformat(),
                    response_time=response_time
                )

        except requests.RequestException as e:
            return HealthCheck(
                name="registry_connectivity",
                status=HealthStatus.CRITICAL,
                message=f"Cannot connect to registry: {str(e)}",
                timestamp=datetime.now().isoformat(),
                response_time=time.time() - start_time
            )

    def _check_memory_usage(self) -> HealthCheck:
        """Check memory usage"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            percent = memory.percent

            config = self.check_configs["memory_usage"]
            warning_threshold = config.get("threshold_warning", 80)
            critical_threshold = config.get("threshold_critical", 90)

            if percent >= critical_threshold:
                status = HealthStatus.CRITICAL
                message = f"Memory usage critical: {percent:.1f}%"
            elif percent >= warning_threshold:
                status = HealthStatus.WARNING
                message = f"Memory usage high: {percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Memory usage normal: {percent:.1f}%"

            return HealthCheck(
                name="memory_usage",
                status=status,
                message=message,
                timestamp=datetime.now().isoformat(),
                details={
                    "percent": percent,
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used
                }
            )

        except ImportError:
            return HealthCheck(
                name="memory_usage",
                status=HealthStatus.UNKNOWN,
                message="psutil not available for memory monitoring",
                timestamp=datetime.now().isoformat()
            )

    def _check_disk_space(self) -> HealthCheck:
        """Check disk space usage"""
        try:
            import psutil
            disk = psutil.disk_usage('/')
            percent = (disk.used / disk.total) * 100

            config = self.check_configs["disk_space"]
            warning_threshold = config.get("threshold_warning", 85)
            critical_threshold = config.get("threshold_critical", 95)

            if percent >= critical_threshold:
                status = HealthStatus.CRITICAL
                message = f"Disk space critical: {percent:.1f}%"
            elif percent >= warning_threshold:
                status = HealthStatus.WARNING
                message = f"Disk space high: {percent:.1f}%"
            else:
                status = HealthStatus.HEALTHY
                message = f"Disk space normal: {percent:.1f}%"

            return HealthCheck(
                name="disk_space",
                status=status,
                message=message,
                timestamp=datetime.now().isoformat(),
                details={
                    "percent": percent,
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free
                }
            )

        except ImportError:
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.UNKNOWN,
                message="psutil not available for disk monitoring",
                timestamp=datetime.now().isoformat()
            )

    def _check_response_time(self) -> HealthCheck:
        """Check average response time"""
        # This would typically use data from the telemetry system
        # For now, return a placeholder
        config = self.check_configs["response_time"]
        warning_threshold = config.get("threshold_warning", 5.0)
        critical_threshold = config.get("threshold_critical", 10.0)

        # Mock response time - in real implementation, get from telemetry
        avg_response_time = 2.5  # Mock value

        if avg_response_time >= critical_threshold:
            status = HealthStatus.CRITICAL
            message = f"Response time critical: {avg_response_time:.2f}s"
        elif avg_response_time >= warning_threshold:
            status = HealthStatus.WARNING
            message = f"Response time high: {avg_response_time:.2f}s"
        else:
            status = HealthStatus.HEALTHY
            message = f"Response time normal: {avg_response_time:.2f}s"

        return HealthCheck(
            name="response_time",
            status=status,
            message=message,
            timestamp=datetime.now().isoformat(),
            details={"avg_response_time": avg_response_time}
        )

    def _get_registry_url(self) -> str:
        """Get registry URL"""
        try:
            import os
            if os.path.exists("registry_url.txt"):
                with open("registry_url.txt", "r") as f:
                    return f.read().strip()
        except:
            pass
        return "http://capregistry.duckdns.org:6900"

    def get_health_history(self, check_name: str, hours: int = 24) -> List[HealthCheck]:
        """Get health check history"""
        if check_name not in self.check_history:
            return []

        cutoff_time = datetime.now() - timedelta(hours=hours)

        with self.lock:
            return [
                check for check in self.check_history[check_name]
                if datetime.fromisoformat(check.timestamp) > cutoff_time
            ]

    def add_custom_health_check(self, name: str, check_function, config: Dict[str, Any]):
        """Add a custom health check"""
        self.check_configs[name] = config
        # Store the check function for later use
        setattr(self, f"_check_{name}", check_function)