#!/usr/bin/env python3
"""
Agent Discovery System - Intelligent search and recommendation for the agent ecosystem
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .task_analyzer import TaskAnalyzer, TaskAnalysis
from .agent_ranker import AgentRanker, AgentScore
from ..core.registry_client import RegistryClient


@dataclass
class DiscoveryResult:
    """Result of agent discovery process"""
    task_analysis: TaskAnalysis
    recommended_agents: List[AgentScore]
    total_agents_evaluated: int
    search_time_seconds: float
    suggestions: List[str]


class AgentDiscovery:
    """Main discovery system that coordinates task analysis and agent ranking"""

    def __init__(self, registry_client: Optional[RegistryClient] = None):
        self.registry_client = registry_client or RegistryClient()
        self.task_analyzer = TaskAnalyzer()
        self.agent_ranker = AgentRanker()
        self.performance_cache = {}

    def discover_agents(self, task_description: str, limit: int = 5,
                       min_score: float = 0.3, filters: Dict[str, Any] = None) -> DiscoveryResult:
        """Main entry point for agent discovery"""
        import time
        start_time = time.time()

        # Analyze the task
        task_analysis = self.task_analyzer.analyze_task(task_description)

        # Get available agents
        agents = self._get_relevant_agents(task_analysis, filters)

        # Get performance data
        performance_data = self._get_performance_data()

        # Rank agents
        agent_scores = self.agent_ranker.rank_agents(agents, task_analysis, performance_data)

        # Get top recommendations
        recommendations = self.agent_ranker.get_top_recommendations(
            agent_scores, limit, min_score
        )

        # Generate suggestions
        suggestions = self._generate_suggestions(task_analysis, recommendations)

        search_time = time.time() - start_time

        return DiscoveryResult(
            task_analysis=task_analysis,
            recommended_agents=recommendations,
            total_agents_evaluated=len(agents),
            search_time_seconds=search_time,
            suggestions=suggestions
        )

    def search_agents_by_capabilities(self, capabilities: List[str],
                                    domain: str = None) -> List[Dict[str, Any]]:
        """Search agents by specific capabilities"""
        filters = {"capabilities": capabilities}
        if domain:
            filters["domain"] = domain

        return self.registry_client.search_agents(capabilities=capabilities)

    def search_agents_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Search agents by domain expertise"""
        return self.registry_client.search_agents(query=domain)

    def get_agent_details(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent"""
        return self.registry_client.get_agent_metadata(agent_id)

    def _make_agent_hashable(self, agent: Dict[str, Any]) -> tuple:
        """Convert agent dict to hashable tuple, handling lists properly"""
        hashable_items = []
        for key, value in sorted(agent.items()):
            if isinstance(value, list):
                # Convert lists to tuples to make them hashable
                hashable_items.append((key, tuple(value)))
            elif isinstance(value, dict):
                # Convert nested dicts to sorted tuples
                hashable_items.append((key, tuple(sorted(value.items()))))
            else:
                hashable_items.append((key, value))
        return tuple(hashable_items)

    def _convert_hashable_to_dict(self, hashable_agent: tuple) -> Dict[str, Any]:
        """Convert hashable tuple back to agent dictionary"""
        agent_dict = {}
        for key, value in hashable_agent:
            if isinstance(value, tuple) and key in ['capabilities', 'expertise', 'tags']:
                # Convert tuples back to lists for known list fields
                agent_dict[key] = list(value)
            elif isinstance(value, tuple) and len(value) > 0 and isinstance(value[0], tuple):
                # Convert nested tuples back to dicts
                agent_dict[key] = dict(value)
            else:
                agent_dict[key] = value
        return agent_dict

    def _get_relevant_agents(self, task_analysis: TaskAnalysis,
                            filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get agents relevant to the task"""

        # Start with capability-based search
        agents = set()

        # Search by required capabilities
        if task_analysis.required_capabilities:
            cap_agents = self.registry_client.search_agents(
                capabilities=task_analysis.required_capabilities
            )
            # Handle both dict and string responses
            for agent in cap_agents:
                if isinstance(agent, dict):
                    agents.update([self._make_agent_hashable(agent)])
                elif isinstance(agent, str):
                    # Create a basic dict from string agent ID
                    agent_dict = {"agent_id": agent, "description": "Agent from registry"}
                    agents.update([self._make_agent_hashable(agent_dict)])

        # Search by domain
        if task_analysis.domain and task_analysis.domain != "general":
            domain_agents = self.registry_client.search_agents(
                query=task_analysis.domain
            )
            # Handle both dict and string responses
            for agent in domain_agents:
                if isinstance(agent, dict):
                    agents.update([self._make_agent_hashable(agent)])
                elif isinstance(agent, str):
                    # Create a basic dict from string agent ID
                    agent_dict = {"agent_id": agent, "description": "Agent from registry"}
                    agents.update([self._make_agent_hashable(agent_dict)])

        # Search by keywords
        if task_analysis.keywords:
            keyword_query = " ".join(task_analysis.keywords[:3])  # Top 3 keywords
            keyword_agents = self.registry_client.search_agents(query=keyword_query)
            # Handle both dict and string responses
            for agent in keyword_agents:
                if isinstance(agent, dict):
                    agents.update([self._make_agent_hashable(agent)])
                elif isinstance(agent, str):
                    # Create a basic dict from string agent ID
                    agent_dict = {"agent_id": agent, "description": "Agent from registry"}
                    agents.update([self._make_agent_hashable(agent_dict)])

        # Convert back to list of dictionaries
        agent_list = [self._convert_hashable_to_dict(agent) for agent in agents]

        # Apply additional filters
        if filters:
            agent_list = self._apply_filters(agent_list, filters)

        # If no specific matches, get general agents
        if not agent_list:
            agent_list = self.registry_client.list_agents()

        return agent_list

    def _apply_filters(self, agents: List[Dict[str, Any]],
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply additional filters to agent list"""
        filtered = agents

        if "status" in filters:
            filtered = [a for a in filtered if a.get("status") == filters["status"]]

        if "min_score" in filters:
            # This would require pre-scoring, so skip for now
            pass

        if "exclude_agents" in filters:
            exclude_set = set(filters["exclude_agents"])
            filtered = [a for a in filtered if a.get("agent_id") not in exclude_set]

        if "domain" in filters:
            domain_filter = filters["domain"].lower()
            filtered = [a for a in filtered
                       if a.get("domain", "").lower() == domain_filter]

        return filtered

    def _get_performance_data(self) -> Dict[str, Any]:
        """Get cached performance data for agents"""
        # This would typically come from a telemetry system
        # For now, return mock data or cached data
        return self.performance_cache

    def update_performance_data(self, agent_id: str, performance_metrics: Dict[str, Any]):
        """Update performance data for an agent"""
        self.performance_cache[agent_id] = performance_metrics

    def _generate_suggestions(self, task_analysis: TaskAnalysis,
                            recommendations: List[AgentScore]) -> List[str]:
        """Generate helpful suggestions based on discovery results"""
        suggestions = []

        if not recommendations:
            suggestions.extend([
                "No agents found matching your requirements",
                f"Try searching for agents with '{task_analysis.domain}' domain expertise",
                "Consider breaking down your task into smaller components",
                "Check if your required capabilities are too specific"
            ])
        elif len(recommendations) == 1:
            suggestions.append("Only one agent found - consider broadening your search criteria")
        elif task_analysis.complexity == "complex":
            suggestions.extend([
                "This appears to be a complex task",
                "Consider using multiple agents for different components",
                "Review the top agents' capabilities to ensure full coverage"
            ])

        # Add suggestions based on task type
        if task_analysis.task_type == "data_analysis":
            suggestions.append("For data analysis tasks, ensure agents have visualization capabilities")
        elif task_analysis.task_type == "automation":
            suggestions.append("For automation, look for agents with workflow management features")

        # Add performance-based suggestions
        if recommendations:
            top_score = recommendations[0].score
            if top_score < 0.7:
                suggestions.append("Match confidence is moderate - review agent details carefully")

        return suggestions

    def explain_recommendations(self, discovery_result: DiscoveryResult) -> str:
        """Generate detailed explanation of the discovery process and results"""
        lines = []

        # Task analysis summary
        lines.append("=== Task Analysis ===")
        lines.append(f"Task Type: {discovery_result.task_analysis.task_type}")
        lines.append(f"Domain: {discovery_result.task_analysis.domain}")
        lines.append(f"Complexity: {discovery_result.task_analysis.complexity}")
        lines.append(f"Required Capabilities: {', '.join(discovery_result.task_analysis.required_capabilities)}")
        lines.append(f"Key Keywords: {', '.join(discovery_result.task_analysis.keywords[:5])}")
        lines.append(f"Analysis Confidence: {discovery_result.task_analysis.confidence:.2f}")
        lines.append("")

        # Search results summary
        lines.append("=== Search Results ===")
        lines.append(f"Total Agents Evaluated: {discovery_result.total_agents_evaluated}")
        lines.append(f"Agents Recommended: {len(discovery_result.recommended_agents)}")
        lines.append(f"Search Time: {discovery_result.search_time_seconds:.2f} seconds")
        lines.append("")

        # Detailed agent recommendations
        if discovery_result.recommended_agents:
            lines.append("=== Recommended Agents ===")
            for i, agent_score in enumerate(discovery_result.recommended_agents, 1):
                lines.append(f"\n{i}. Agent: {agent_score.agent_id}")
                lines.append(f"   Score: {agent_score.score:.2f}")
                lines.append(f"   Confidence: {agent_score.confidence:.2f}")
                if agent_score.match_reasons:
                    lines.append("   Match Reasons:")
                    for reason in agent_score.match_reasons:
                        lines.append(f"     - {reason}")
        else:
            lines.append("=== No Agents Found ===")

        # Suggestions
        if discovery_result.suggestions:
            lines.append("\n=== Suggestions ===")
            for suggestion in discovery_result.suggestions:
                lines.append(f"- {suggestion}")

        return "\n".join(lines)

    def get_similar_agents(self, agent_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Find agents similar to the given agent"""
        target_agent = self.registry_client.get_agent_metadata(agent_id)
        if not target_agent:
            return []

        # Create a pseudo-task based on the agent's characteristics
        task_desc = f"Task requiring {target_agent.get('domain', 'general')} domain expertise"
        if target_agent.get('capabilities'):
            task_desc += f" with capabilities: {', '.join(target_agent['capabilities'])}"

        # Discover similar agents
        result = self.discover_agents(task_desc, limit=limit + 1)  # +1 to exclude self

        # Filter out the original agent
        similar = [
            agent for agent in result.recommended_agents
            if agent.agent_id != agent_id
        ]

        return similar[:limit]