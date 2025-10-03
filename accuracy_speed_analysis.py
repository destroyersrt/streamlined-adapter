#!/usr/bin/env python3
"""
Detailed Accuracy and Speed Analysis for 3 Capability Structures
"""

import os
import sys
import time
import json
import statistics
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv not installed")

from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts


class AccuracySpeedAnalyzer:
    """Comprehensive accuracy and speed analysis for capability structures"""
    
    def __init__(self):
        self.mongo_facts = MongoDBAgentFacts()
        self.test_results = {}
    
    def run_comprehensive_analysis(self):
        """Run comprehensive accuracy and speed analysis"""
        print("🔬 Starting Comprehensive Accuracy & Speed Analysis")
        print("=" * 60)
        
        # Test queries with expected results for accuracy measurement
        test_scenarios = [
            {
                "query": "python web development",
                "expected_specializations": ["Python Developer"],
                "category": "exact_match"
            },
            {
                "query": "machine learning artificial intelligence",
                "expected_specializations": ["Data Scientist", "AI Engineer"],
                "category": "multi_match"
            },
            {
                "query": "kubernetes docker containers",
                "expected_specializations": ["DevOps Engineer", "Cloud Architect"],
                "category": "multi_match"
            },
            {
                "query": "react frontend javascript",
                "expected_specializations": ["Frontend Developer"],
                "category": "exact_match"
            },
            {
                "query": "security penetration testing",
                "expected_specializations": ["Security Expert"],
                "category": "exact_match"
            },
            {
                "query": "mobile app development",
                "expected_specializations": ["Mobile Developer"],
                "category": "exact_match"
            },
            {
                "query": "database optimization sql",
                "expected_specializations": ["Database Expert"],
                "category": "exact_match"
            },
            {
                "query": "quality assurance testing",
                "expected_specializations": ["QA Engineer"],
                "category": "exact_match"
            },
            {
                "query": "web development backend",
                "expected_specializations": ["Python Developer", "Frontend Developer"],
                "category": "broad_match"
            },
            {
                "query": "cloud computing infrastructure",
                "expected_specializations": ["DevOps Engineer", "Cloud Architect"],
                "category": "broad_match"
            }
        ]
        
        # Run analysis for each structure type
        structure_results = {}
        
        for structure_type in ["keywords", "description", "embedding"]:
            print(f"\n🧪 Testing Structure: {structure_type.upper()}")
            print("-" * 40)
            
            structure_results[structure_type] = {
                "accuracy_scores": [],
                "speed_scores": [],
                "precision_scores": [],
                "recall_scores": [],
                "scenario_results": []
            }
            
            for scenario in test_scenarios:
                result = self._test_scenario(scenario, structure_type)
                structure_results[structure_type]["scenario_results"].append(result)
                structure_results[structure_type]["accuracy_scores"].append(result["accuracy"])
                structure_results[structure_type]["speed_scores"].append(result["speed"])
                structure_results[structure_type]["precision_scores"].append(result["precision"])
                structure_results[structure_type]["recall_scores"].append(result["recall"])
                
                print(f"  {scenario['query'][:30]:30} | "
                      f"Acc: {result['accuracy']:.2f} | "
                      f"Prec: {result['precision']:.2f} | "
                      f"Rec: {result['recall']:.2f} | "
                      f"Speed: {result['speed']:.3f}s")
        
        # Generate comprehensive report
        self._generate_comprehensive_report(structure_results, test_scenarios)
        
        return structure_results
    
    def _test_scenario(self, scenario: Dict[str, Any], structure_type: str) -> Dict[str, float]:
        """Test a single scenario for accuracy and speed"""
        query = scenario["query"]
        expected_specs = scenario["expected_specializations"]
        
        # Measure search speed
        start_time = time.time()
        search_results = self._search_by_structure(query, structure_type, limit=20)
        search_time = time.time() - start_time
        
        # Calculate accuracy metrics
        found_specs = self._extract_specializations(search_results)
        
        # Precision: What fraction of retrieved agents are relevant?
        relevant_retrieved = len(set(found_specs) & set(expected_specs))
        precision = relevant_retrieved / len(found_specs) if found_specs else 0
        
        # Recall: What fraction of relevant agents were retrieved?
        recall = relevant_retrieved / len(expected_specs) if expected_specs else 0
        
        # F1 Score (harmonic mean of precision and recall)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Overall accuracy (custom metric considering ranking)
        accuracy = self._calculate_ranking_accuracy(search_results, expected_specs)
        
        return {
            "query": query,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "speed": search_time,
            "results_count": len(search_results),
            "found_specializations": found_specs,
            "expected_specializations": expected_specs
        }
    
    def _search_by_structure(self, query: str, structure_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search agents by specific structure type"""
        if structure_type == "keywords":
            # Keyword matching with scoring
            query_words = [word.lower() for word in query.split()]
            pipeline = [
                {"$match": {"structure_type": "keywords"}},
                {"$addFields": {
                    "score": {
                        "$size": {
                            "$setIntersection": [
                                {"$map": {"input": "$capabilities.keywords", "as": "kw", "in": {"$toLower": "$$kw"}}},
                                query_words
                            ]
                        }
                    }
                }},
                {"$match": {"score": {"$gt": 0}}},
                {"$sort": {"score": -1, "capabilities.experience_years": -1}},
                {"$limit": limit}
            ]
            
        elif structure_type == "description":
            # Text search on descriptions with text score
            pipeline = [
                {"$match": {
                    "structure_type": "description",
                    "$text": {"$search": query}
                }},
                {"$addFields": {"score": {"$meta": "textScore"}}},
                {"$sort": {"score": {"$meta": "textScore"}, "capabilities.experience_years": -1}},
                {"$limit": limit}
            ]
            
        elif structure_type == "embedding":
            # Simulated vector similarity with enhanced scoring
            query_embedding = self._simulate_embedding(query)
            pipeline = [
                {"$match": {"structure_type": "embedding"}},
                {"$addFields": {
                    "score": {
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
                {"$sort": {"score": -1, "capabilities.experience_years": -1}},
                {"$limit": limit}
            ]
        
        return list(self.mongo_facts.collection.aggregate(pipeline))
    
    def _simulate_embedding(self, text: str) -> List[float]:
        """Simulate embedding vector (same as in capability_structures_test.py)"""
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to 384-dimensional vector
        embedding = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad to 384 dimensions
        while len(embedding) < 384:
            embedding.extend(embedding[:min(384-len(embedding), len(embedding))])
        
        return embedding[:384]
    
    def _extract_specializations(self, search_results: List[Dict[str, Any]]) -> List[str]:
        """Extract unique specializations from search results"""
        specializations = []
        for result in search_results:
            agent_name = result.get("agent_name", "")
            # Extract base specialization (remove variation number)
            base_name = " ".join(agent_name.split()[:-1]) if agent_name else ""
            if base_name and base_name not in specializations:
                specializations.append(base_name)
        return specializations
    
    def _calculate_ranking_accuracy(self, search_results: List[Dict[str, Any]], expected_specs: List[str]) -> float:
        """Calculate accuracy considering ranking position"""
        if not search_results or not expected_specs:
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        for i, result in enumerate(search_results[:10]):  # Top 10 results
            agent_name = result.get("agent_name", "")
            base_name = " ".join(agent_name.split()[:-1]) if agent_name else ""
            
            # Weight decreases with position (1.0, 0.9, 0.8, ...)
            weight = max(0.1, 1.0 - (i * 0.1))
            total_weight += weight
            
            if base_name in expected_specs:
                score += weight
        
        return score / total_weight if total_weight > 0 else 0.0
    
    def _generate_comprehensive_report(self, results: Dict[str, Any], scenarios: List[Dict[str, Any]]):
        """Generate comprehensive analysis report"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE ANALYSIS REPORT")
        print("=" * 80)
        
        # Overall Performance Summary
        print("\n🎯 OVERALL PERFORMANCE SUMMARY")
        print("-" * 50)
        
        summary_table = []
        for structure_type, data in results.items():
            avg_accuracy = statistics.mean(data["accuracy_scores"])
            avg_precision = statistics.mean(data["precision_scores"])
            avg_recall = statistics.mean(data["recall_scores"])
            avg_speed = statistics.mean(data["speed_scores"])
            std_speed = statistics.stdev(data["speed_scores"]) if len(data["speed_scores"]) > 1 else 0
            
            summary_table.append({
                "Structure": structure_type.capitalize(),
                "Accuracy": f"{avg_accuracy:.3f}",
                "Precision": f"{avg_precision:.3f}",
                "Recall": f"{avg_recall:.3f}",
                "Avg Speed": f"{avg_speed:.3f}s",
                "Speed StdDev": f"{std_speed:.3f}s"
            })
        
        # Print summary table
        headers = ["Structure", "Accuracy", "Precision", "Recall", "Avg Speed", "Speed StdDev"]
        print(f"{'Structure':<12} {'Accuracy':<10} {'Precision':<10} {'Recall':<8} {'Avg Speed':<10} {'Speed StdDev':<12}")
        print("-" * 70)
        for row in summary_table:
            print(f"{row['Structure']:<12} {row['Accuracy']:<10} {row['Precision']:<10} {row['Recall']:<8} {row['Avg Speed']:<10} {row['Speed StdDev']:<12}")
        
        # Category-wise Analysis
        print("\n📈 CATEGORY-WISE ANALYSIS")
        print("-" * 50)
        
        categories = {}
        for i, scenario in enumerate(scenarios):
            category = scenario["category"]
            if category not in categories:
                categories[category] = {"keywords": [], "description": [], "embedding": []}
            
            for structure_type in ["keywords", "description", "embedding"]:
                result = results[structure_type]["scenario_results"][i]
                categories[category][structure_type].append(result["accuracy"])
        
        for category, cat_data in categories.items():
            print(f"\n{category.replace('_', ' ').title()}:")
            for structure_type, accuracies in cat_data.items():
                avg_acc = statistics.mean(accuracies) if accuracies else 0
                print(f"  {structure_type.capitalize():<12}: {avg_acc:.3f}")
        
        # Speed Analysis
        print("\n⚡ SPEED ANALYSIS")
        print("-" * 50)
        
        for structure_type, data in results.items():
            speeds = data["speed_scores"]
            print(f"\n{structure_type.capitalize()}:")
            print(f"  Min Speed:    {min(speeds):.3f}s")
            print(f"  Max Speed:    {max(speeds):.3f}s")
            print(f"  Median Speed: {statistics.median(speeds):.3f}s")
            print(f"  95th %ile:    {sorted(speeds)[int(0.95 * len(speeds))]:.3f}s")
        
        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        print("-" * 50)
        
        # Find best performing structure for each metric
        best_accuracy = max(results.keys(), key=lambda x: statistics.mean(results[x]["accuracy_scores"]))
        best_speed = min(results.keys(), key=lambda x: statistics.mean(results[x]["speed_scores"]))
        best_precision = max(results.keys(), key=lambda x: statistics.mean(results[x]["precision_scores"]))
        
        print(f"🎯 Best Accuracy:  {best_accuracy.capitalize()} ({statistics.mean(results[best_accuracy]['accuracy_scores']):.3f})")
        print(f"⚡ Fastest:        {best_speed.capitalize()} ({statistics.mean(results[best_speed]['speed_scores']):.3f}s)")
        print(f"🔍 Best Precision: {best_precision.capitalize()} ({statistics.mean(results[best_precision]['precision_scores']):.3f})")
        
        # Overall recommendation
        print(f"\n🏆 OVERALL RECOMMENDATION:")
        
        # Calculate composite score (accuracy * 0.5 + (1/speed) * 0.3 + precision * 0.2)
        composite_scores = {}
        for structure_type, data in results.items():
            accuracy = statistics.mean(data["accuracy_scores"])
            speed_score = 1 / statistics.mean(data["speed_scores"])  # Inverse for speed (faster = better)
            precision = statistics.mean(data["precision_scores"])
            
            composite = (accuracy * 0.5) + (speed_score * 0.3) + (precision * 0.2)
            composite_scores[structure_type] = composite
        
        best_overall = max(composite_scores.keys(), key=lambda x: composite_scores[x])
        print(f"   {best_overall.capitalize()} structure provides the best balance of accuracy, speed, and precision.")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"capability_analysis_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "summary": summary_table,
                "detailed_results": results,
                "composite_scores": composite_scores,
                "recommendations": {
                    "best_accuracy": best_accuracy,
                    "best_speed": best_speed,
                    "best_precision": best_precision,
                    "best_overall": best_overall
                }
            }, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")


if __name__ == "__main__":
    analyzer = AccuracySpeedAnalyzer()
    results = analyzer.run_comprehensive_analysis()
