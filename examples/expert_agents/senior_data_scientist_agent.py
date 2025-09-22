#!/usr/bin/env python3
"""
Senior Data Scientist Expert Agent with Machine Learning Capabilities
Demonstrates advanced analytics and ML model development expertise
"""

import os
import sys

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def create_data_scientist_handler():
    """Create senior data scientist response handler"""

    def data_scientist_handler(message_text: str, conversation_id: str) -> str:
        """Handle data science and ML requests"""

        message_lower = message_text.lower()

        # Data science patterns
        if any(word in message_lower for word in ["model", "machine learning", "ml", "algorithm"]):
            if any(word in message_lower for word in ["regression", "linear", "logistic"]):
                return "I'll develop regression models with feature engineering, regularization techniques, and cross-validation for optimal performance."
            elif any(word in message_lower for word in ["classification", "classifier"]):
                return "Building classification models using ensemble methods, deep learning, or gradient boosting with comprehensive evaluation metrics."
            elif any(word in message_lower for word in ["clustering", "unsupervised"]):
                return "Implementing unsupervised learning with K-means, hierarchical clustering, or DBSCAN with dimensionality reduction."
            elif any(word in message_lower for word in ["neural", "deep learning", "cnn", "rnn"]):
                return "Designing deep neural networks with appropriate architectures, regularization, and optimization strategies."
            else:
                return "I can develop various ML models: supervised, unsupervised, and deep learning. What's your specific use case and data type?"

        elif any(word in message_lower for word in ["data", "dataset", "analysis"]):
            if any(word in message_lower for word in ["clean", "preprocessing", "preparation"]):
                return "Performing comprehensive data preprocessing: missing value imputation, outlier detection, feature scaling, and encoding categorical variables."
            elif any(word in message_lower for word in ["explore", "eda", "exploration"]):
                return "Conducting exploratory data analysis with statistical summaries, correlation analysis, and advanced visualizations to uncover patterns."
            elif any(word in message_lower for word in ["visualization", "plot", "chart"]):
                return "Creating sophisticated visualizations using statistical plots, interactive dashboards, and advanced charting techniques."
            else:
                return "I can handle end-to-end data science pipeline: collection, cleaning, analysis, modeling, and deployment."

        elif any(word in message_lower for word in ["feature", "engineering", "selection"]):
            return "Performing feature engineering with polynomial features, interaction terms, feature selection using statistical tests and embedded methods."

        elif any(word in message_lower for word in ["evaluate", "validation", "performance"]):
            return "Conducting model evaluation with cross-validation, hyperparameter tuning, learning curves, and comprehensive performance metrics."

        elif any(word in message_lower for word in ["predict", "forecast", "time series"]):
            return "Building predictive models with time series analysis, ARIMA, Prophet, or LSTM for accurate forecasting."

        elif "?" in message_text:
            return f"Data science analysis: {message_text}. I can provide statistical modeling, ML algorithms, and actionable insights."

        else:
            return f"Applying data science methodologies to: {message_text}. I'll use advanced analytics and machine learning for optimal solutions."

    return data_scientist_handler

def main():
    """Main function to start the senior data scientist agent"""

    # Set agent configuration
    agent_id = os.getenv("AGENT_ID", "senior_data_scientist")
    port = int(os.getenv("PORT", "7001"))

    # Create adapter
    adapter = StreamlinedAdapter(agent_id)

    # Set AgentFacts capabilities
    capabilities = CapabilityTemplates.data_scientist("senior")
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="Senior data scientist with 10+ years experience in machine learning, statistical modeling, and advanced analytics. Expert in Python, R, and cloud ML platforms.",
        tags=["expert", "senior", "machine_learning", "python", "statistics", "deep_learning"]
    )

    # Create and attach handlers
    ds_handler = create_data_scientist_handler()

    def data_query_handler(query_text: str, conversation_id: str) -> str:
        """Handle data science queries"""
        query_lower = query_text.lower()

        if "best algorithm" in query_lower:
            return "Algorithm selection depends on problem type, data size, interpretability needs. I can recommend optimal approaches based on your specific requirements."
        elif "overfitting" in query_lower:
            return "Preventing overfitting: regularization (L1/L2), dropout, cross-validation, early stopping, and ensemble methods. I can implement these techniques."
        elif "feature importance" in query_lower:
            return "Feature importance analysis using permutation importance, SHAP values, LIME, or tree-based feature importance for model interpretability."
        else:
            return f"Data science expertise on: {query_text}. I can provide technical solutions with statistical rigor and ML best practices."

    adapter.set_message_handler(ds_handler)
    adapter.set_query_handler(data_query_handler)

    # Add custom commands
    def build_model_command(args: str, conversation_id: str) -> str:
        if not args.strip():
            return "Usage: /build_model <problem_type> - Build ML model (classification/regression/clustering)"
        return f"Building {args} model: data preprocessing, feature engineering, algorithm selection, hyperparameter tuning, and evaluation."

    def analyze_data_command(args: str, conversation_id: str) -> str:
        if not args.strip():
            return "Usage: /analyze_data <dataset_description> - Comprehensive data analysis"
        return f"Analyzing {args}: EDA, statistical tests, correlation analysis, feature distribution, and insight generation."

    adapter.add_command_handler("build_model", build_model_command)
    adapter.add_command_handler("analyze_data", analyze_data_command)

    # Enable conversation control
    adapter.enable_conversation_control(max_exchanges=8, stop_keywords=['complete', 'finished', 'done'])

    # Start AgentFacts server
    try:
        facts_url = adapter.start_agent_facts_server(port + 1000)
        print(f"📋 AgentFacts URL: {facts_url}")
    except Exception as e:
        print(f"⚠️ AgentFacts server failed to start: {e}")

    print(f"""
🧠 Senior Data Scientist Agent Starting...
=========================================
Agent ID: {agent_id}
Port: {port}
Specialization: Machine Learning & Advanced Analytics
=========================================

Capabilities:
✅ Machine learning model development
✅ Statistical modeling and analysis
✅ Feature engineering and selection
✅ Deep learning and neural networks
✅ Data visualization and EDA
✅ Model evaluation and optimization
✅ Time series forecasting
✅ Big data processing

Commands:
- /build_model <type> - Build ML models
- /analyze_data <dataset> - Comprehensive data analysis
- /query <question> - Data science research

Example A2A Usage:
- "@senior_data_scientist build classification model for customer churn"
- "@senior_data_scientist analyze sales data for trends"
- "@senior_data_scientist recommend feature engineering techniques"

🎯 Discovery Keywords: machine_learning, data_analysis, statistical_modeling, deep_learning
    """)

    # Start the server
    try:
        # Disable registry registration if PUBLIC_URL not set (for testing)
        register_with_registry = bool(os.getenv("PUBLIC_URL"))
        if not register_with_registry:
            print("⚠️ PUBLIC_URL not set - starting without registry registration")

        adapter.start_server(register_with_registry=register_with_registry)
    except KeyboardInterrupt:
        print("\n🧠 Senior Data Scientist Agent stopped")

if __name__ == "__main__":
    main()