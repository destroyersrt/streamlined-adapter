#!/usr/bin/env python3
"""
Marketing Strategist Expert Agent
Demonstrates marketing strategy, campaign planning, and customer analysis expertise
"""

import os
import sys

# Add the streamlined adapter to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from nanda_core.core.adapter import StreamlinedAdapter
from nanda_core.core.agent_facts import CapabilityTemplates

def create_marketing_strategist_handler():
    """Create marketing strategist response handler"""

    def marketing_strategist_handler(message_text: str, conversation_id: str) -> str:
        """Handle marketing strategy and campaign requests"""

        message_lower = message_text.lower()

        # Marketing strategy patterns
        if any(word in message_lower for word in ["campaign", "marketing campaign", "promotion"]):
            if any(word in message_lower for word in ["digital", "online", "social media"]):
                return "Developing integrated digital marketing campaign with social media strategy, content calendar, SEO optimization, and performance tracking across platforms."
            elif any(word in message_lower for word in ["launch", "product launch"]):
                return "Creating comprehensive product launch strategy with pre-launch buzz, influencer partnerships, PR coordination, and multi-channel campaign execution."
            elif any(word in message_lower for word in ["email", "newsletter"]):
                return "Designing email marketing campaign with segmentation strategy, A/B testing, automation workflows, and conversion optimization."
            else:
                return "Developing multi-channel marketing campaign with target audience analysis, messaging strategy, channel selection, and ROI measurement."

        elif any(word in message_lower for word in ["audience", "target", "segmentation", "persona"]):
            return "Conducting audience segmentation with demographic analysis, behavioral profiling, customer journey mapping, and persona development."

        elif any(word in message_lower for word in ["brand", "branding", "positioning"]):
            return "Developing brand positioning strategy with competitive analysis, value proposition refinement, brand messaging, and market differentiation."

        elif any(word in message_lower for word in ["content", "content strategy", "storytelling"]):
            return "Creating content marketing strategy with editorial calendar, SEO optimization, multi-format content planning, and engagement metrics."

        elif any(word in message_lower for word in ["analytics", "metrics", "roi", "performance"]):
            return "Implementing marketing analytics with KPI tracking, attribution modeling, customer lifetime value analysis, and campaign performance optimization."

        elif any(word in message_lower for word in ["competitive", "competition", "competitor"]):
            return "Conducting competitive analysis with market positioning assessment, competitive messaging review, and strategic opportunity identification."

        elif any(word in message_lower for word in ["budget", "spend", "allocation"]):
            return "Optimizing marketing budget allocation across channels with cost-per-acquisition analysis, channel performance review, and ROI maximization strategies."

        elif "?" in message_text:
            return f"Marketing strategy consultation: {message_text}. I can provide data-driven recommendations with market insights and competitive analysis."

        else:
            return f"Strategic marketing approach for: {message_text}. I'll develop comprehensive strategies with customer-centric focus and measurable outcomes."

    return marketing_strategist_handler

def main():
    """Main function to start the marketing strategist agent"""

    # Set agent configuration
    agent_id = os.getenv("AGENT_ID", "marketing_strategist")
    port = int(os.getenv("PORT", "7008"))

    # Create adapter
    adapter = StreamlinedAdapter(agent_id)

    # Set AgentFacts capabilities
    capabilities = CapabilityTemplates.marketing_specialist("strategy")
    adapter.set_agent_capabilities(
        capabilities=capabilities,
        description="Strategic marketing expert specializing in campaign development, brand positioning, and customer acquisition. Expert in digital marketing, analytics, and growth strategies.",
        tags=["expert", "marketing", "strategy", "digital_marketing", "brand_positioning", "analytics"]
    )

    # Create and attach handlers
    marketing_handler = create_marketing_strategist_handler()

    def marketing_query_handler(query_text: str, conversation_id: str) -> str:
        """Handle marketing strategy queries"""
        query_lower = query_text.lower()

        if "increase conversion" in query_lower:
            return "Conversion optimization strategy: landing page optimization, A/B testing, user experience improvements, and funnel analysis for higher conversion rates."
        elif "customer acquisition" in query_lower:
            return "Customer acquisition strategy: multi-channel approach, lead generation optimization, customer lifetime value focus, and cost-effective scaling."
        elif "brand awareness" in query_lower:
            return "Brand awareness campaign: content marketing, influencer partnerships, PR strategy, and social media amplification for increased visibility."
        elif "market research" in query_lower:
            return "Market research methodology: customer surveys, focus groups, competitive analysis, and trend identification for strategic insights."
        else:
            return f"Marketing strategy insights for: {query_text}. I'll provide actionable recommendations with industry best practices and data-driven approach."

    adapter.set_message_handler(marketing_handler)
    adapter.set_query_handler(marketing_query_handler)

    # Add custom commands
    def campaign_strategy_command(args: str, conversation_id: str) -> str:
        if not args.strip():
            return "Usage: /campaign <product/service> - Develop comprehensive campaign strategy"
        return f"Campaign strategy for {args}: audience targeting, messaging framework, channel selection, creative concepts, and performance metrics."

    def audience_analysis_command(args: str, conversation_id: str) -> str:
        if not args.strip():
            return "Usage: /audience <market/product> - Conduct audience analysis and segmentation"
        return f"Audience analysis for {args}: demographic profiling, behavioral segmentation, persona development, and engagement preferences."

    adapter.add_command_handler("campaign", campaign_strategy_command)
    adapter.add_command_handler("audience", audience_analysis_command)

    # Enable conversation control
    adapter.enable_conversation_control(max_exchanges=7, stop_keywords=['approved', 'finalized', 'complete'])

    # Start AgentFacts server
    try:
        facts_url = adapter.start_agent_facts_server(port + 1000)
        print(f"📋 AgentFacts URL: {facts_url}")
    except Exception as e:
        print(f"⚠️ AgentFacts server failed to start: {e}")

    print(f"""
📈 Marketing Strategist Agent Starting...
========================================
Agent ID: {agent_id}
Port: {port}
Specialization: Marketing Strategy & Campaign Development
========================================

Capabilities:
✅ Campaign strategy and planning
✅ Brand positioning and messaging
✅ Audience segmentation and targeting
✅ Digital marketing optimization
✅ Content strategy development
✅ Marketing analytics and ROI
✅ Competitive analysis
✅ Customer acquisition strategies

Commands:
- /campaign <product> - Comprehensive campaign strategy
- /audience <market> - Audience analysis and segmentation
- /query <question> - Marketing strategy consultation

Example A2A Usage:
- "@marketing_strategist develop campaign for new product launch"
- "@marketing_strategist analyze target audience for B2B software"
- "@marketing_strategist optimize conversion rates for e-commerce"

🎯 Discovery Keywords: marketing_strategy, campaign_planning, brand_positioning, customer_acquisition
    """)

    # Start the server
    try:
        # Disable registry registration if PUBLIC_URL not set (for testing)
        register_with_registry = bool(os.getenv("PUBLIC_URL"))
        if not register_with_registry:
            print("⚠️ PUBLIC_URL not set - starting without registry registration")

        adapter.start_server(register_with_registry=register_with_registry)
    except KeyboardInterrupt:
        print("\n📈 Marketing Strategist Agent stopped")

if __name__ == "__main__":
    main()