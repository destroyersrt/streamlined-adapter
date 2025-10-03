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
        # Simplified scoring - only capability matching matters
        self.weights = {
            "capability_match": 1.0,
            "domain_match": 0.0,
            "keyword_match": 0.0,
            "performance": 0.0,
            "availability": 0.0,
            "load": 0.0
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

    def _normalize_registry_score(self, registry_score: float, agent: Dict[str, Any], match_reasons: List[str]) -> float:
        """Normalize registry scores to consistent 0-1 scale"""
        
        structure_type = agent.get('structure_type', 'unknown')
        
        if structure_type == 'embedding':
            # Embedding scores are already 0-1 (cosine similarity)
            normalized = min(1.0, max(0.0, registry_score))
            match_reasons.append(f"Cosine similarity: {registry_score:.3f}")
            
        elif structure_type == 'keywords':
            # Keywords scores are raw match counts (typically 0-5)
            # Normalize to 0-1 scale with sigmoid-like curve
            if registry_score <= 0:
                normalized = 0.0
            elif registry_score >= 4.0:
                normalized = 0.95  # Cap at 0.95 for very high matches
            else:
                # Scale 0-4 to 0.0-0.95
                normalized = (registry_score / 4.0) * 0.95
            match_reasons.append(f"Keyword matches: {registry_score:.2f} → {normalized:.2f}")
            
        elif structure_type == 'description':
            # Description scores are text similarity (typically 0-5)
            # Similar normalization as keywords
            if registry_score <= 0:
                normalized = 0.0
            elif registry_score >= 4.0:
                normalized = 0.95
            else:
                normalized = (registry_score / 4.0) * 0.95
            match_reasons.append(f"Text similarity: {registry_score:.2f} → {normalized:.2f}")
            
        else:
            # Unknown structure type - conservative normalization
            normalized = min(0.8, registry_score / 5.0) if registry_score > 0 else 0.0
            match_reasons.append(f"Registry score: {registry_score:.2f} → {normalized:.2f}")
        
        return normalized

    def _score_agent(self, agent: Dict[str, Any], task_analysis: Any,
                    performance_data: Dict[str, Any] = None) -> AgentScore:
        """Calculate comprehensive score for a single agent"""

        agent_id = agent.get("agent_id", "unknown")
        match_reasons = []

        # Check if agent already has a score from registry search
        registry_score = agent.get('score', None)
        
        if registry_score is not None:
            # Use and normalize registry score for consistency
            normalized_score = self._normalize_registry_score(registry_score, agent, match_reasons)
            capability_score = normalized_score
        else:
            # Calculate our own capability score
            capability_score = self._score_capabilities(agent, task_analysis, match_reasons)
        
        # Other scores (currently weighted to 0, but kept for future use)
        domain_score = self._score_domain(agent, task_analysis, match_reasons)
        keyword_score = self._score_keywords(agent, task_analysis, match_reasons)
        performance_score = self._score_performance(agent, performance_data)
        availability_score = self._score_availability(agent)
        load_score = self._score_load(agent)

        # Calculate weighted total score (currently only capability_score matters)
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
                "load_score": load_score,
                "registry_score": registry_score,
                "normalized_score": capability_score if registry_score else None
            }
        )

    def _score_capabilities(self, agent: Dict[str, Any], task_analysis: Any,
                          match_reasons: List[str]) -> float:
        """Score based on capability matching - simplified and more aggressive"""
        
        # Get agent capabilities from different sources
        agent_capabilities = set()
        
        # From capabilities field
        if "capabilities" in agent:
            caps = agent["capabilities"]
            if isinstance(caps, dict) and "technical_skills" in caps:
                agent_capabilities.update(caps["technical_skills"])
            elif isinstance(caps, list):
                agent_capabilities.update(caps)
        
        # From specialization and description (keyword matching)
        specialization = agent.get("specialization", "").lower()
        description = agent.get("description", "").lower()
        
        # Extract keywords from task
        task_keywords = set()
        if hasattr(task_analysis, 'keywords') and task_analysis.keywords:
            task_keywords.update(word.lower() for word in task_analysis.keywords)
        if hasattr(task_analysis, 'required_capabilities') and task_analysis.required_capabilities:
            task_keywords.update(word.lower() for word in task_analysis.required_capabilities)
        
        if not task_keywords:
            return 0.5  # Neutral score when no specific requirements
            
        # Calculate matches
        capability_matches = set()
        keyword_matches = set()
        
        # Direct capability matches
        for cap in agent_capabilities:
            cap_lower = cap.lower()
            for keyword in task_keywords:
                if keyword in cap_lower or cap_lower in keyword:
                    capability_matches.add(keyword)
        
        # Keyword matches in specialization/description
        for keyword in task_keywords:
            if keyword in specialization or keyword in description:
                keyword_matches.add(keyword)
        
        all_matches = capability_matches.union(keyword_matches)
        
        if all_matches:
            match_reasons.append(f"Matching capabilities: {', '.join(all_matches)}")
        
        # Calculate score based on match ratio
        if not task_keywords:
            return 0.5
            
        match_ratio = len(all_matches) / len(task_keywords)
        
        # Boost score for good matches
        if match_ratio >= 0.8:  # 80%+ match
            return min(1.0, 0.8 + (match_ratio - 0.8) * 2)  # 0.8 to 1.0
        elif match_ratio >= 0.5:  # 50%+ match  
            return 0.5 + (match_ratio - 0.5) * 1.0  # 0.5 to 0.8
        elif match_ratio >= 0.2:  # 20%+ match
            return 0.2 + (match_ratio - 0.2) * 1.0  # 0.2 to 0.5
        else:
            return match_ratio  # 0.0 to 0.2

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
            if score.score >= min_score and score.confidence >= 0.3
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