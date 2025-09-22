#!/usr/bin/env python3
"""
Agent Ranking System for scoring and recommending agents based on task fit
"""

from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass
class AgentScore:
    """Score result for an agent"""
    agent_id: str
    score: float
    confidence: float
    match_reasons: List[str]
    metadata: Dict[str, Any]


class AgentRanker:
    """Ranks agents based on their suitability for specific tasks"""

    def __init__(self):
        # Scoring weights for different factors
        self.weights = {
            "capability_match": 0.35,
            "domain_match": 0.25,
            "keyword_match": 0.20,
            "performance": 0.10,
            "availability": 0.05,
            "load": 0.05
        }

    def rank_agents(self, agents: List[Dict[str, Any]], task_analysis: Any,
                   performance_data: Dict[str, Any] = None) -> List[AgentScore]:
        """Rank agents based on task requirements"""

        agent_scores = []

        for agent in agents:
            score_result = self._score_agent(agent, task_analysis, performance_data)
            agent_scores.append(score_result)

        # Sort by score (descending)
        agent_scores.sort(key=lambda x: x.score, reverse=True)

        return agent_scores

    def _score_agent(self, agent: Dict[str, Any], task_analysis: Any,
                    performance_data: Dict[str, Any] = None) -> AgentScore:
        """Calculate comprehensive score for a single agent"""

        agent_id = agent.get("agent_id", "unknown")
        match_reasons = []

        # Calculate individual scores
        capability_score = self._score_capabilities(agent, task_analysis, match_reasons)
        domain_score = self._score_domain(agent, task_analysis, match_reasons)
        keyword_score = self._score_keywords(agent, task_analysis, match_reasons)
        performance_score = self._score_performance(agent, performance_data)
        availability_score = self._score_availability(agent)
        load_score = self._score_load(agent)

        # Calculate weighted total score
        total_score = (
            capability_score * self.weights["capability_match"] +
            domain_score * self.weights["domain_match"] +
            keyword_score * self.weights["keyword_match"] +
            performance_score * self.weights["performance"] +
            availability_score * self.weights["availability"] +
            load_score * self.weights["load"]
        )

        # Calculate confidence based on available data quality
        confidence = self._calculate_confidence(agent, task_analysis)

        return AgentScore(
            agent_id=agent_id,
            score=total_score,
            confidence=confidence,
            match_reasons=match_reasons,
            metadata={
                "capability_score": capability_score,
                "domain_score": domain_score,
                "keyword_score": keyword_score,
                "performance_score": performance_score,
                "availability_score": availability_score,
                "load_score": load_score
            }
        )

    def _score_capabilities(self, agent: Dict[str, Any], task_analysis: Any,
                          match_reasons: List[str]) -> float:
        """Score based on capability matching"""
        agent_capabilities = set(agent.get("capabilities", []))
        required_capabilities = set(task_analysis.required_capabilities)

        if not required_capabilities:
            return 0.7  # Neutral score when no specific requirements

        if not agent_capabilities:
            return 0.3  # Low score for agents with no declared capabilities

        # Calculate overlap
        matching_caps = agent_capabilities.intersection(required_capabilities)
        match_ratio = len(matching_caps) / len(required_capabilities)

        if matching_caps:
            match_reasons.append(f"Matching capabilities: {', '.join(matching_caps)}")

        # Bonus for having more relevant capabilities than required
        if len(matching_caps) == len(required_capabilities):
            extra_relevant = len(agent_capabilities) - len(required_capabilities)
            bonus = min(0.2, extra_relevant * 0.05)
            match_ratio += bonus

        return min(1.0, match_ratio)

    def _score_domain(self, agent: Dict[str, Any], task_analysis: Any,
                     match_reasons: List[str]) -> float:
        """Score based on domain expertise"""
        agent_domain = agent.get("domain", "").lower()
        task_domain = task_analysis.domain.lower()

        if task_domain == "general":
            return 0.7  # Neutral score for general tasks

        if not agent_domain or agent_domain == "general":
            return 0.5  # Moderate score for general agents

        if agent_domain == task_domain:
            match_reasons.append(f"Domain expertise: {task_domain}")
            return 1.0

        # Check for related domains
        domain_similarity = self._calculate_domain_similarity(agent_domain, task_domain)
        if domain_similarity > 0.5:
            match_reasons.append(f"Related domain: {agent_domain}")

        return domain_similarity

    def _score_keywords(self, agent: Dict[str, Any], task_analysis: Any,
                       match_reasons: List[str]) -> float:
        """Score based on keyword matching"""
        agent_keywords = set(word.lower() for word in agent.get("keywords", []))
        agent_description = agent.get("description", "").lower()
        task_keywords = set(word.lower() for word in task_analysis.keywords)

        if not task_keywords:
            return 0.7  # Neutral score when no keywords

        # Direct keyword matches
        direct_matches = agent_keywords.intersection(task_keywords)

        # Keywords found in description
        description_matches = set()
        for keyword in task_keywords:
            if keyword in agent_description:
                description_matches.add(keyword)

        all_matches = direct_matches.union(description_matches)

        if all_matches:
            match_reasons.append(f"Keyword matches: {', '.join(all_matches)}")

        match_ratio = len(all_matches) / len(task_keywords) if task_keywords else 0
        return min(1.0, match_ratio)

    def _score_performance(self, agent: Dict[str, Any],
                          performance_data: Dict[str, Any] = None) -> float:
        """Score based on historical performance"""
        if not performance_data:
            return 0.7  # Neutral score without performance data

        agent_id = agent.get("agent_id")
        if agent_id not in performance_data:
            return 0.7

        perf = performance_data[agent_id]

        # Consider multiple performance metrics
        success_rate = perf.get("success_rate", 0.7)
        avg_response_time = perf.get("avg_response_time", 5.0)  # seconds
        reliability = perf.get("reliability", 0.7)

        # Normalize response time (lower is better)
        time_score = max(0.0, 1.0 - (avg_response_time / 30.0))  # 30s max

        # Combine metrics
        performance_score = (success_rate * 0.5 + time_score * 0.3 + reliability * 0.2)

        return min(1.0, performance_score)

    def _score_availability(self, agent: Dict[str, Any]) -> float:
        """Score based on agent availability"""
        status = agent.get("status", "unknown").lower()
        last_seen_str = agent.get("last_seen")

        if status == "offline":
            return 0.0
        elif status == "busy":
            return 0.3
        elif status == "available" or status == "online":
            return 1.0

        # If no explicit status, check last seen
        if last_seen_str:
            try:
                last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                time_diff = datetime.now() - last_seen.replace(tzinfo=None)

                if time_diff < timedelta(minutes=5):
                    return 1.0
                elif time_diff < timedelta(hours=1):
                    return 0.8
                elif time_diff < timedelta(days=1):
                    return 0.5
                else:
                    return 0.2
            except:
                pass

        return 0.5  # Default for unknown availability

    def _score_load(self, agent: Dict[str, Any]) -> float:
        """Score based on current agent load"""
        current_load = agent.get("current_load", 0.5)  # 0.0 to 1.0

        # Lower load is better
        return 1.0 - current_load

    def _calculate_domain_similarity(self, domain1: str, domain2: str) -> float:
        """Calculate similarity between domains"""
        related_domains = {
            "technology": ["software", "it", "programming", "tech"],
            "finance": ["banking", "trading", "accounting", "fintech"],
            "healthcare": ["medical", "clinical", "pharmaceutical"],
            "marketing": ["advertising", "sales", "promotion"],
            "education": ["learning", "training", "academic"]
        }

        for main_domain, related in related_domains.items():
            if domain1 in related and domain2 in related:
                return 0.8
            elif (domain1 == main_domain and domain2 in related) or \
                 (domain2 == main_domain and domain1 in related):
                return 0.9

        return 0.2  # Low similarity for unrelated domains

    def _calculate_confidence(self, agent: Dict[str, Any], task_analysis: Any) -> float:
        """Calculate confidence in the scoring"""
        confidence = 0.5  # Base confidence

        # Increase confidence based on available agent metadata
        if agent.get("capabilities"):
            confidence += 0.2
        if agent.get("description"):
            confidence += 0.1
        if agent.get("domain"):
            confidence += 0.1
        if agent.get("last_seen"):
            confidence += 0.05
        if agent.get("status"):
            confidence += 0.05

        # Factor in task analysis confidence
        confidence *= task_analysis.confidence

        return min(1.0, confidence)

    def get_top_recommendations(self, agent_scores: List[AgentScore],
                              limit: int = 5, min_score: float = 0.3) -> List[AgentScore]:
        """Get top agent recommendations with filtering"""

        # Filter by minimum score and confidence
        filtered = [
            score for score in agent_scores
            if score.score >= min_score and score.confidence >= 0.4
        ]

        return filtered[:limit]

    def explain_ranking(self, agent_score: AgentScore) -> str:
        """Generate human-readable explanation for agent ranking"""
        explanations = []

        explanations.append(f"Overall score: {agent_score.score:.2f} (confidence: {agent_score.confidence:.2f})")

        if agent_score.match_reasons:
            explanations.append("Match reasons:")
            for reason in agent_score.match_reasons:
                explanations.append(f"  - {reason}")

        # Add detailed score breakdown
        metadata = agent_score.metadata
        explanations.append("Score breakdown:")
        explanations.append(f"  - Capability match: {metadata.get('capability_score', 0):.2f}")
        explanations.append(f"  - Domain expertise: {metadata.get('domain_score', 0):.2f}")
        explanations.append(f"  - Keyword relevance: {metadata.get('keyword_score', 0):.2f}")
        explanations.append(f"  - Performance: {metadata.get('performance_score', 0):.2f}")
        explanations.append(f"  - Availability: {metadata.get('availability_score', 0):.2f}")
        explanations.append(f"  - Load: {metadata.get('load_score', 0):.2f}")

        return "\n".join(explanations)