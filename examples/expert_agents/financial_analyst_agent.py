#!/usr/bin/env python3
"""
Financial Analyst Expert Agent with AgentFacts Integration
Demonstrates AgentFacts-based registration and capability-driven discovery
"""

import os
import sys

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def create_financial_analyst_handler():
    """Create financial analyst response handler"""

    def financial_analyst_handler(message_text: str, conversation_id: str) -> str:
        """Handle financial analysis requests"""

        message_lower = message_text.lower()

        # Financial analysis patterns
        if any(word in message_lower for word in ["analyze", "analysis", "examine"]):
            if any(word in message_lower for word in ["stock", "equity", "shares"]):
                return "I'll perform a comprehensive equity analysis including fundamental metrics, technical indicators, and market position assessment."
            elif any(word in message_lower for word in ["portfolio", "investment"]):
                return "Conducting portfolio analysis with risk metrics, diversification assessment, and performance attribution analysis."
            elif any(word in message_lower for word in ["market", "sector"]):
                return "Analyzing market conditions with sector rotation patterns, economic indicators, and trend analysis."
            else:
                return "I can analyze various financial instruments including equities, bonds, derivatives, and portfolios. Please specify the asset type."

        elif any(word in message_lower for word in ["risk", "volatility", "var"]):
            return "Performing risk assessment using VaR models, stress testing, and scenario analysis to quantify potential downside exposure."

        elif any(word in message_lower for word in ["valuation", "value", "worth"]):
            return "Conducting valuation using DCF models, comparable company analysis, and precedent transactions to determine fair value."

        elif any(word in message_lower for word in ["forecast", "predict", "projection"]):
            return "Creating financial forecasts using time-series analysis, regression models, and scenario planning methodologies."

        elif any(word in message_lower for word in ["ratio", "metrics", "kpi"]):
            return "Calculating key financial ratios including liquidity, profitability, efficiency, and leverage metrics with industry comparisons."

        elif "?" in message_text:
            return f"As a financial analyst, I can help with: {message_text}. Would you like me to provide detailed analysis methodology?"

        else:
            return f"Financial analysis perspective on: {message_text}. I can provide quantitative analysis, risk assessment, and investment recommendations."

    return financial_analyst_handler

def create_financial_query_handler():
    """Create financial query handler for /query commands"""

    def financial_query_handler(query_text: str, conversation_id: str) -> str:
        """Handle financial queries"""

        query_lower = query_text.lower()

        if "market outlook" in query_lower:
            return "Current market outlook shows mixed signals with elevated volatility. Key factors: inflation trends, central bank policy, and geopolitical risks."

        elif "best investment" in query_lower:
            return "Investment recommendations require analysis of your risk profile, time horizon, and objectives. I can assess specific opportunities."

        elif "recession" in query_lower:
            return "Recession indicators include yield curve inversion, employment trends, and consumer spending patterns. Current probability requires detailed analysis."

        elif "cryptocurrency" in query_lower or "crypto" in query_lower:
            return "Cryptocurrency analysis involves technical analysis, adoption metrics, regulatory environment, and correlation with traditional assets."

        elif "dividend" in query_lower:
            return "Dividend analysis includes yield sustainability, payout ratios, growth history, and sector comparison for income-focused strategies."

        else:
            return f"Financial analysis of: {query_text}. I can provide detailed research with quantitative models and risk assessment."

    return financial_query_handler

def main():
    """Main function to start the financial analyst agent"""

    # Set agent configuration
    agent_id = os.getenv("AGENT_ID", "financial_analyst")
    port = int(os.getenv("PORT", "7004"))

    # Create adapter
    adapter = StreamlinedAdapter(agent_id)

    # Set AgentFacts capabilities
    capabilities = CapabilityTemplates.financial_analyst("general")
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="Professional financial analyst with expertise in equity research, portfolio analysis, and risk assessment. Provides quantitative analysis and investment insights.",
        tags=["expert", "finance", "quantitative", "equity_research", "portfolio_analysis"]
    )

    # Create and attach handlers
    analyst_handler = create_financial_analyst_handler()
    query_handler = create_financial_query_handler()

    adapter.set_message_handler(analyst_handler)
    adapter.set_query_handler(query_handler)

    # Add custom commands
    def financial_analysis_command(args: str, conversation_id: str) -> str:
        if not args.strip():
            return "Usage: /analyze <asset/portfolio> - Perform comprehensive financial analysis"
        return f"Initiating financial analysis of {args}: fundamental analysis, technical indicators, risk metrics, and valuation models."

    def risk_assessment_command(args: str, conversation_id: str) -> str:
        if not args.strip():
            return "Usage: /risk <investment> - Conduct risk assessment analysis"
        return f"Risk assessment for {args}: VaR calculation, stress testing, correlation analysis, and downside protection strategies."

    adapter.add_command_handler("analyze", financial_analysis_command)
    adapter.add_command_handler("risk", risk_assessment_command)

    # Enable conversation control (prevent infinite financial debates)
    adapter.enable_conversation_control(max_exchanges=6, stop_keywords=['thanks', 'done', 'sufficient'])

    # Start AgentFacts server
    try:
        facts_url = adapter.start_agent_facts_server(port + 1000)
        print(f"📋 AgentFacts URL: {facts_url}")
    except Exception as e:
        print(f"⚠️ AgentFacts server failed to start: {e}")

    print(f"""
💰 Financial Analyst Agent Starting...
=====================================
Agent ID: {agent_id}
Port: {port}
Specialization: Financial Analysis & Research
=====================================

Capabilities:
✅ Equity research and analysis
✅ Portfolio optimization and risk assessment
✅ Market analysis and forecasting
✅ Valuation models (DCF, Comparable, etc.)
✅ Financial ratio analysis
✅ Risk management strategies

Commands:
- /analyze <asset> - Comprehensive financial analysis
- /risk <investment> - Risk assessment analysis
- /query <question> - Financial research queries

Example A2A Usage:
- "@financial_analyst analyze AAPL stock performance"
- "@financial_analyst assess portfolio risk for tech sector"
- "@financial_analyst provide market outlook for Q4"

🎯 Discovery Keywords: financial_analysis, market_research, risk_assessment, portfolio_analysis
    """)

    # Start the server
    try:
        # Disable registry registration if PUBLIC_URL not set (for testing)
        register_with_registry = bool(os.getenv("PUBLIC_URL"))
        if not register_with_registry:
            print("⚠️ PUBLIC_URL not set - starting without registry registration")

        adapter.start_server(register_with_registry=register_with_registry)
    except KeyboardInterrupt:
        print("\n💰 Financial Analyst Agent stopped")

if __name__ == "__main__":
    main()