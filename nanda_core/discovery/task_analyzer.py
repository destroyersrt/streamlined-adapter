#!/usr/bin/env python3
"""
Task Analyzer for understanding user intent and task requirements
"""

import re
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from anthropic import Anthropic


@dataclass
class TaskAnalysis:
    """Result of task analysis"""
    task_type: str
    complexity: str  # 'simple', 'medium', 'complex'
    domain: str
    keywords: List[str]
    required_capabilities: List[str]
    confidence: float
    description: str


class TaskAnalyzer:
    """Analyzes tasks to understand requirements and extract relevant features"""

    def __init__(self):
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

        # Predefined task patterns
        self.task_patterns = {
            "data_analysis": [
                r"analyz(e|ing|sis)", r"data", r"statistics", r"chart", r"graph",
                r"report", r"dashboard", r"metrics", r"kpi"
            ],
            "web_scraping": [
                r"scrap(e|ing)", r"extract", r"crawl", r"fetch", r"website",
                r"html", r"parse", r"web"
            ],
            "file_management": [
                r"file", r"folder", r"directory", r"organize", r"manage",
                r"upload", r"download", r"storage"
            ],
            "communication": [
                r"email", r"message", r"send", r"notify", r"alert",
                r"slack", r"discord", r"teams"
            ],
            "code_generation": [
                r"code", r"program", r"script", r"function", r"api",
                r"development", r"software", r"programming"
            ],
            "research": [
                r"research", r"search", r"find", r"lookup", r"investigate",
                r"study", r"explore", r"discover"
            ],
            "automation": [
                r"automat(e|ion)", r"workflow", r"process", r"schedule",
                r"trigger", r"batch", r"recurring"
            ]
        }

        self.complexity_indicators = {
            "simple": [
                r"simple", r"basic", r"quick", r"easy", r"straightforward"
            ],
            "complex": [
                r"complex", r"advanced", r"sophisticated", r"comprehensive",
                r"detailed", r"multi-step", r"enterprise"
            ]
        }

    def analyze_task(self, task_description: str) -> TaskAnalysis:
        """Analyze a task description and extract requirements"""

        # Clean and prepare text
        text = task_description.lower().strip()

        # Extract task type
        task_type = self._identify_task_type(text)

        # Determine complexity
        complexity = self._assess_complexity(text)

        # Extract domain
        domain = self._extract_domain(text)

        # Extract keywords
        keywords = self._extract_keywords(text)

        # Identify required capabilities
        capabilities = self._identify_capabilities(text, task_type)

        # Use Claude for enhanced analysis if available
        enhanced_analysis = self._enhance_with_claude(task_description)

        if enhanced_analysis:
            capabilities.extend(enhanced_analysis.get("capabilities", []))
            keywords.extend(enhanced_analysis.get("keywords", []))
            if enhanced_analysis.get("domain"):
                domain = enhanced_analysis["domain"]

        # Remove duplicates
        capabilities = list(set(capabilities))
        keywords = list(set(keywords))

        # Calculate confidence score
        confidence = self._calculate_confidence(text, task_type, complexity)

        return TaskAnalysis(
            task_type=task_type,
            complexity=complexity,
            domain=domain,
            keywords=keywords,
            required_capabilities=capabilities,
            confidence=confidence,
            description=task_description
        )

    def _identify_task_type(self, text: str) -> str:
        """Identify the primary task type"""
        scores = {}

        for task_type, patterns in self.task_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, text))
                score += matches
            scores[task_type] = score

        if not scores or max(scores.values()) == 0:
            return "general"

        return max(scores, key=scores.get)

    def _assess_complexity(self, text: str) -> str:
        """Assess task complexity based on indicators"""
        simple_score = 0
        complex_score = 0

        for pattern in self.complexity_indicators["simple"]:
            simple_score += len(re.findall(pattern, text))

        for pattern in self.complexity_indicators["complex"]:
            complex_score += len(re.findall(pattern, text))

        # Default to medium if no clear indicators
        if simple_score > complex_score:
            return "simple"
        elif complex_score > simple_score:
            return "complex"
        else:
            # Analyze length and structure as fallback
            word_count = len(text.split())
            if word_count < 10:
                return "simple"
            elif word_count > 50:
                return "complex"
            else:
                return "medium"

    def _extract_domain(self, text: str) -> str:
        """Extract the domain/industry context"""
        domain_keywords = {
            "finance": [r"financial", r"banking", r"investment", r"trading", r"accounting"],
            "healthcare": [r"medical", r"health", r"patient", r"hospital", r"clinical"],
            "technology": [r"software", r"tech", r"programming", r"development", r"it"],
            "marketing": [r"marketing", r"advertising", r"campaign", r"promotion", r"brand"],
            "education": [r"education", r"learning", r"teaching", r"student", r"course"],
            "ecommerce": [r"shop", r"store", r"product", r"order", r"payment", r"cart"],
            "logistics": [r"shipping", r"delivery", r"transport", r"warehouse", r"supply"]
        }

        for domain, patterns in domain_keywords.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return domain

        return "general"

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from the text"""
        # Remove stop words and extract meaningful terms
        stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "up", "about", "into", "through", "during",
            "before", "after", "above", "below", "between", "among", "under", "over",
            "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
            "do", "does", "did", "will", "would", "could", "should", "may", "might",
            "can", "must", "shall", "i", "you", "he", "she", "it", "we", "they",
            "me", "him", "her", "us", "them", "my", "your", "his", "its", "our", "their"
        }

        words = re.findall(r'\b\w+\b', text)
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Return top keywords by frequency
        from collections import Counter
        word_counts = Counter(keywords)
        return [word for word, count in word_counts.most_common(10)]

    def _identify_capabilities(self, text: str, task_type: str) -> List[str]:
        """Identify required agent capabilities"""
        capabilities = []

        # Base capabilities by task type
        task_capabilities = {
            "data_analysis": ["analytics", "visualization", "statistics", "reporting"],
            "web_scraping": ["web_access", "html_parsing", "data_extraction"],
            "file_management": ["file_operations", "storage_access", "organization"],
            "communication": ["messaging", "notifications", "email"],
            "code_generation": ["programming", "code_review", "debugging"],
            "research": ["search", "information_gathering", "synthesis"],
            "automation": ["workflow_management", "scheduling", "integration"]
        }

        capabilities.extend(task_capabilities.get(task_type, []))

        # Additional capability detection
        capability_patterns = {
            "api_integration": [r"api", r"integration", r"connect", r"webhook"],
            "database": [r"database", r"sql", r"query", r"store", r"retrieve"],
            "machine_learning": [r"ml", r"machine learning", r"ai", r"model", r"predict"],
            "image_processing": [r"image", r"photo", r"picture", r"visual", r"ocr"],
            "document_processing": [r"document", r"pdf", r"word", r"text", r"parse"],
            "real_time": [r"real.?time", r"live", r"streaming", r"instant"],
            "security": [r"secure", r"encrypt", r"auth", r"permission", r"access"]
        }

        for capability, patterns in capability_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    capabilities.append(capability)
                    break

        return capabilities

    def _enhance_with_claude(self, task_description: str) -> Optional[Dict[str, Any]]:
        """Use Claude to enhance task analysis"""
        try:
            if not self.anthropic.api_key:
                return None

            prompt = f"""Analyze the following task description and extract:
1. Primary domain/industry
2. Required capabilities (technical skills, integrations, etc.)
3. Important keywords
4. Task complexity (simple/medium/complex)

Task: {task_description}

Respond with JSON format:
{{
    "domain": "domain_name",
    "capabilities": ["capability1", "capability2"],
    "keywords": ["keyword1", "keyword2"],
    "complexity": "simple|medium|complex"
}}"""

            response = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            return json.loads(response.content[0].text)

        except Exception as e:
            # Claude enhancement failed, falling back to basic analysis
            # (This is expected if ANTHROPIC_API_KEY is not set)
            return None

    def _calculate_confidence(self, text: str, task_type: str, complexity: str) -> float:
        """Calculate confidence score for the analysis"""
        score = 0.5  # Base confidence

        # Increase confidence based on text length and clarity
        word_count = len(text.split())
        if word_count >= 5:
            score += 0.2
        if word_count >= 15:
            score += 0.1

        # Increase confidence if task type was clearly identified
        if task_type != "general":
            score += 0.2

        # Normalize to 0-1 range
        return min(1.0, score)