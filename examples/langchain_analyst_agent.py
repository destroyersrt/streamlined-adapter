#!/usr/bin/env python3
"""
LangChain + Anthropic Document Analysis Agent

A real-world example showing how to integrate LangChain and Anthropic Claude
with the new simple NANDA adapter for document analysis and Q&A.
"""

import os
import sys
from typing import Dict, Any

# Add the streamlined adapter to the path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# LangChain imports
try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_anthropic import ChatAnthropic
    from langchain_core.runnables import RunnablePassthrough
except ImportError:
    print("❌ LangChain packages not installed. Install with:")
    print("   pip install langchain-core langchain-anthropic")
    sys.exit(1)

# NANDA adapter import
from nanda_core.core.adapter import NANDA


class DocumentAnalyst:
    """LangChain-powered document analyst using Anthropic Claude"""
    
    def __init__(self):
        # Initialize Anthropic Claude via LangChain
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,
            max_tokens=1024
        )
        
        # Create analysis prompt template
        self.analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional document analyst. Analyze the given text and provide:
1. **Summary**: Brief overview of the content
2. **Key Points**: 3-5 main points or findings  
3. **Analysis**: Your professional assessment
4. **Recommendations**: Actionable suggestions if applicable

Be concise but thorough. Format your response clearly with headers."""),
            ("human", "Analyze this text: {text}")
        ])
        
        # Create Q&A prompt template
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful assistant that answers questions based on context.
If you don't have enough information to answer, say so clearly.
Provide accurate, helpful responses."""),
            ("human", "Question: {question}\n\nContext: {context}")
        ])
        
        # Create analysis chain
        self.analysis_chain = (
            self.analysis_prompt 
            | self.llm 
            | StrOutputParser()
        )
        
        # Create Q&A chain  
        self.qa_chain = (
            self.qa_prompt
            | self.llm
            | StrOutputParser()
        )
        
        # Store recent documents for Q&A
        self.document_store = {}
        
        print("📊 LangChain Document Analyst initialized with Claude 3.5 Sonnet")
    
    def analyze_document(self, text: str, doc_id: str = None) -> str:
        """Analyze a document and return structured analysis"""
        try:
            # Store document for later Q&A
            if doc_id:
                self.document_store[doc_id] = text
            
            # Run analysis chain
            analysis = self.analysis_chain.invoke({"text": text})
            return analysis
            
        except Exception as e:
            return f"Error analyzing document: {str(e)}"
    
    def answer_question(self, question: str, context: str = None, doc_id: str = None) -> str:
        """Answer questions about documents"""
        try:
            # Use provided context or retrieve from store
            if context is None and doc_id and doc_id in self.document_store:
                context = self.document_store[doc_id]
            elif context is None:
                return "No context provided. Please provide text or specify a document ID."
            
            # Run Q&A chain
            answer = self.qa_chain.invoke({
                "question": question,
                "context": context
            })
            return answer
            
        except Exception as e:
            return f"Error answering question: {str(e)}"


def create_analyst_agent_logic(analyst: DocumentAnalyst):
    """Create the agent logic function for NANDA"""
    
    def analyst_logic(message: str, conversation_id: str) -> str:
        """Process messages using LangChain + Anthropic"""
        
        # Handle different command types
        message_lower = message.lower().strip()
        
        # Document analysis command
        if message.startswith("analyze:"):
            text = message[8:].strip()
            if not text:
                return "Please provide text to analyze. Format: analyze: <your text>"
            
            analysis = analyst.analyze_document(text, doc_id=conversation_id)
            return f"📊 **Document Analysis**\n\n{analysis}"
        
        # Question answering command
        elif message.startswith("question:"):
            question = message[9:].strip()
            if not question:
                return "Please provide a question. Format: question: <your question>"
            
            # Try to use conversation context
            answer = analyst.answer_question(question, doc_id=conversation_id)
            return f"❓ **Q&A Response**\n\n{answer}"
        
        # Help command
        elif "help" in message_lower:
            return """📊 **Document Analyst Agent**

I can help you analyze documents and answer questions using LangChain + Anthropic Claude.

**Commands:**
• `analyze: <text>` - Analyze any document or text
• `question: <question>` - Ask questions about previously analyzed text
• `help` - Show this help message

**Examples:**
• `analyze: This quarterly report shows revenue increased by 15%...`
• `question: What was the revenue increase percentage?`

I use Claude 3.5 Sonnet for professional document analysis."""
        
        # Default: treat as general question
        else:
            answer = analyst.answer_question(message)
            return f"💬 {answer}"
    
    return analyst_logic


def main():
    """Main function to start the LangChain analyst agent"""
    
    # Check for required API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("   Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        sys.exit(1)
    
    # Initialize the document analyst
    print("🔄 Initializing LangChain Document Analyst...")
    analyst = DocumentAnalyst()
    
    # Create agent logic
    agent_logic = create_analyst_agent_logic(analyst)
    
    # Create NANDA agent with the new simple API
    nanda = NANDA(
        agent_id="langchain_analyst",
        agent_logic=agent_logic,
        port=6020,
        enable_telemetry=True  # Enable to track usage
    )
    
    print("""
🚀 LangChain Document Analyst Agent
=====================================
Agent ID: langchain_analyst
Port: 6020
Model: Claude 3.5 Sonnet via LangChain
=====================================

📝 **How to use:**
• Send: 'help' for commands
• Send: 'analyze: <your document text>'
• Send: 'question: <your question>'

🔗 **Agent Communication:**
• Send: '@other_agent message' to talk to other agents
• Send: '/status' for system status

💡 **Example:**
analyze: This is a quarterly business report showing 15% revenue growth...
question: What was the revenue growth percentage?
    """)
    
    # Start the agent
    try:
        nanda.start(register=False)  # Set to True if you have a registry
    except KeyboardInterrupt:
        print("\n🛑 Analyst agent stopped")


if __name__ == "__main__":
    main()

