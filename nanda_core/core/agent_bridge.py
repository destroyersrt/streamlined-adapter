#!/usr/bin/env python3
"""
Enhanced Agent Bridge for A2A Communication with Semantic Search

Clean bridge with telemetry, semantic search, and agent discovery.
"""

import os
import uuid
import logging
import requests
import time
import json
from typing import Callable, Optional, Dict, Any, List
from python_a2a import A2AServer, A2AClient, Message, TextContent, MessageRole, Metadata

# Configure logger to capture conversation logs
logger = logging.getLogger(__name__)


class SimpleAgentBridge(A2AServer):
    """Enhanced Agent Bridge with semantic search and telemetry"""
    
    def __init__(self, 
                 agent_id: str, 
                 agent_logic: Callable[[str, str], str],
                 registry_url: Optional[str] = None,
                 telemetry = None,
                 url: Optional[str] = None):
        super().__init__(url=url)  # Pass URL to A2AServer
        self.agent_id = agent_id
        self.agent_logic = agent_logic
        self.registry_url = registry_url
        self.telemetry = telemetry
        
        # Initialize discovery system if registry is available
        self.discovery = None
        self.registry_client = None
        if registry_url:
            try:
                from ..discovery.agent_discovery import AgentDiscovery
                from .registry_client import RegistryClient
                self.registry_client = RegistryClient(registry_url)
                self.discovery = AgentDiscovery(self.registry_client)
                print(f"🔍 Agent discovery enabled for {agent_id}")
            except ImportError as e:
                print(f"⚠️ Discovery system not available: {e}")
        
    def handle_message(self, msg: Message) -> Message:
        """Handle incoming messages with enhanced features"""
        start_time = time.time()
        conversation_id = msg.conversation_id or str(uuid.uuid4())
        
        # Log telemetry
        if self.telemetry:
            self.telemetry.log_message_received(self.agent_id, conversation_id)
        
        # Only handle text content
        if not isinstance(msg.content, TextContent):
            return self._create_response(
                msg, conversation_id, 
                "Only text messages supported"
            )
        
        user_text = msg.content.text.strip()
        
        # Handle semantic search queries with '?' command
        if user_text.startswith('?'):
            return self._handle_search_query(user_text[1:].strip(), msg, conversation_id)
        
        # Check if this is an agent-to-agent message in our simple format
        if user_text.startswith("FROM:") and "TO:" in user_text and "MESSAGE:" in user_text:
            return self._handle_incoming_agent_message(user_text, msg, conversation_id)
        
        # Check for @agent-id mentions for A2A communication
        if user_text.startswith("@") and " " in user_text:
            return self._handle_agent_mention(user_text, msg, conversation_id)
        
        logger.info(f"📨 [{self.agent_id}] Received: {user_text}")
        
        # Handle different message types
        try:
            if user_text.startswith("@"):
                # Agent-to-agent message (outgoing)
                return self._handle_agent_message(user_text, msg, conversation_id)
            elif user_text.startswith("/"):
                # System command
                return self._handle_command(user_text, msg, conversation_id)
            else:
                # Regular message - use agent logic
                if self.telemetry:
                    self.telemetry.log_message_received(self.agent_id, conversation_id)
                
                response = self.agent_logic(user_text, conversation_id)
                return self._create_response(msg, conversation_id, response)
                
        except Exception as e:
            return self._create_response(
                msg, conversation_id, 
                f"Error: {str(e)}"
            )
    
    def _handle_incoming_agent_message(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle incoming messages from other agents"""
        try:
            lines = user_text.strip().split('\n')
            from_agent = ""
            to_agent = ""
            message_content = ""
            
            for line in lines:
                if line.startswith("FROM:"):
                    from_agent = line[5:].strip()
                elif line.startswith("TO:"):
                    to_agent = line[3:].strip()
                elif line.startswith("MESSAGE:"):
                    message_content = line[8:].strip()
            
            logger.info(f"📨 [{self.agent_id}] ← [{from_agent}]: {message_content}")
            
            # Check if this is a reply (don't respond to replies to avoid infinite loops)
            if message_content.startswith("Response to "):
                logger.info(f"🔄 [{self.agent_id}] Received reply from {from_agent}, displaying to user")
                # Display the reply to user but don't respond back to avoid loops
                return self._create_response(
                    msg, conversation_id, 
                    f"[{from_agent}] {message_content[len('Response to ' + self.agent_id + ': '):]}"
                )
            
            # Process the message through our agent logic
            if self.telemetry:
                self.telemetry.log_message_received(self.agent_id, conversation_id)
            
            response = self.agent_logic(message_content, conversation_id)
            
            # Send response back
            return self._create_response(
                msg, conversation_id, 
                f"Response to {from_agent}: {response}"
            )
            
        except Exception as e:
            logger.error(f"❌ [{self.agent_id}] Error processing incoming agent message: {e}")
            return self._create_response(
                msg, conversation_id,
                f"Error processing message from agent: {str(e)}"
            )

    def _handle_agent_message(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle messages to other agents (@agent_id message)"""
        parts = user_text.split(" ", 1)
        if len(parts) <= 1:
            return self._create_response(
                msg, conversation_id,
                "Invalid format. Use '@agent_id message'"
            )
        
        target_agent = parts[0][1:]  # Remove @
        message_text = parts[1]
        
        logger.info(f"🔄 [{self.agent_id}] Sending to {target_agent}: {message_text}")
        
        # Look up target agent and send message
        result = self._send_to_agent(target_agent, message_text, conversation_id)
        return self._create_response(msg, conversation_id, result)
    
    def _handle_command(self, user_text: str, msg: Message, conversation_id: str) -> Message:
        """Handle system commands"""
        parts = user_text.split(" ", 1)
        command = parts[0][1:] if len(parts) > 0 else ""
        args = parts[1] if len(parts) > 1 else ""
        
        if command == "help":
            help_text = """Available commands:
/help - Show this help
/ping - Test agent responsiveness  
/status - Show agent status
@agent_id message - Send message to another agent"""
            return self._create_response(msg, conversation_id, help_text)
        
        elif command == "ping":
            return self._create_response(msg, conversation_id, "Pong!")
        
        elif command == "status":
            status = f"Agent: {self.agent_id}, Status: Running"
            if self.registry_url:
                status += f", Registry: {self.registry_url}"
            return self._create_response(msg, conversation_id, status)
        
        else:
            return self._create_response(
                msg, conversation_id,
                f"Unknown command: {command}. Use /help for available commands"
            )
    
    def _send_to_agent(self, target_agent_id: str, message_text: str, conversation_id: str) -> str:
        """Send message to another agent"""
        try:
            # Look up agent URL
            agent_url = self._lookup_agent(target_agent_id)
            if not agent_url:
                return f"Agent {target_agent_id} not found"
            
            # Ensure URL has /a2a endpoint
            if not agent_url.endswith('/a2a'):
                agent_url = f"{agent_url}/a2a"
            
            logger.info(f"📤 [{self.agent_id}] → [{target_agent_id}]: {message_text}")
            
            # Create simple message with metadata
            simple_message = f"FROM: {self.agent_id}\nTO: {target_agent_id}\nMESSAGE: {message_text}"
            
            # Send message using A2A client
            client = A2AClient(agent_url, timeout=30)
            response = client.send_message(
                Message(
                    role=MessageRole.USER,
                    content=TextContent(text=simple_message),
                    conversation_id=conversation_id,
                    metadata=Metadata(custom_fields={
                        'from_agent_id': self.agent_id,
                        'to_agent_id': target_agent_id,
                        'message_type': 'agent_to_agent'
                    })
                )
            )
            
            if self.telemetry:
                self.telemetry.log_message_sent(target_agent_id, conversation_id, success=True)
            
            # Extract the actual response content from the target agent
            logger.info(f"🔍 [{self.agent_id}] Response type: {type(response)}, has parts: {hasattr(response, 'parts') if response else 'None'}")
            if response:
                if hasattr(response, 'parts') and response.parts:
                    response_text = response.parts[0].text
                    logger.info(f"✅ [{self.agent_id}] Received response from {target_agent_id}: {response_text[:100]}...")
                    return f"[{target_agent_id}] {response_text}"
                else:
                    logger.info(f"✅ [{self.agent_id}] Response has no parts, full response: {str(response)[:200]}...")
                    return f"[{target_agent_id}] {str(response)}"
            else:
                logger.info(f"✅ [{self.agent_id}] Message delivered to {target_agent_id}, no response")
                return f"Message sent to {target_agent_id}: {message_text}"
            
        except Exception as e:
            return f"❌ Error sending to {target_agent_id}: {str(e)}"
    
    def _lookup_agent(self, agent_id: str) -> Optional[str]:
        """Look up agent URL in registry or use local discovery"""
        
        # Try registry lookup if available
        if self.registry_url:
            try:
                response = requests.get(f"{self.registry_url}/lookup/{agent_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    agent_url = data.get("agent_url")
                    logger.info(f"🌐 Found {agent_id} in registry: {agent_url}")
                    return agent_url
            except Exception as e:
                logger.warning(f"🌐 Registry lookup failed: {e}")
        
        # Fallback to local discovery (for testing)
        local_agents = {
            "test_agent": "http://localhost:6000",
            "pirate_agent": "http://localhost:6001", 
            "helpful_agent": "http://localhost:6002",
            "echo_agent": "http://localhost:6003",
            "simple_test_agent": "http://localhost:6005",
            "agent_alpha": "http://localhost:6010",
            "agent_beta": "http://localhost:6011"
        }
        
        if agent_id in local_agents:
            logger.info(f"🏠 Found {agent_id} locally: {local_agents[agent_id]}")
            return local_agents[agent_id]
        
        return None
    
    def _create_response(self, original_msg: Message, conversation_id: str, text: str) -> Message:
        """Create a response message"""
        return Message(
            role=MessageRole.AGENT,
            content=TextContent(text=f"[{self.agent_id}] {text}"),
            parent_message_id=original_msg.message_id,
            conversation_id=conversation_id
        )
    
    def _handle_search_query(self, query: str, original_msg: Message, conversation_id: str) -> Message:
        """Handle semantic search queries with '?' command"""
        if not self.discovery:
            return self._create_response(
                original_msg, conversation_id,
                "🔍 Agent discovery not available. Registry connection required."
            )
        
        if not query:
            return self._create_response(
                original_msg, conversation_id,
                "🔍 Usage: ? <search query>\n"
                "🔍 Structure-specific: ?keywords <query> | ?description <query> | ?embedding <query>\n"
                "Example: ? Find me a data scientist\n"
                "Example: ?keywords python expert\n"
                "Example: ?description data analysis specialist"
            )
        
        try:
            # Log telemetry for search
            search_start = time.time()
            
            # Check for structure-specific search vs direct question
            structure_type = None
            is_direct_question = True
            
            if query.startswith("keywords "):
                structure_type = "keywords"
                query = query[9:].strip()
                is_direct_question = False
            elif query.startswith("description "):
                structure_type = "description"
                query = query[12:].strip()
                is_direct_question = False
            elif query.startswith("embedding "):
                structure_type = "embedding"
                query = query[10:].strip()
                is_direct_question = False
            
            # Handle direct questions with new flow (1 question → 15 interactions)
            if is_direct_question:
                return self._handle_direct_question(query, original_msg, conversation_id, search_start)
            
            # Perform agent discovery (with optional structure filtering)
            result = self.discovery.discover_agents(query, limit=5, min_score=0.3, structure_type=structure_type)
            
            search_time = time.time() - search_start
            if self.telemetry:
                self.telemetry.log_agent_discovery(query, len(result.recommended_agents), search_time)
            
            # Prepare data for structured telemetry
            top_agents = []
            result_quality_score = 0.0
            search_method = "mongodb"  # Default, will be updated based on discovery method
            
            if result.recommended_agents:
                # Extract top agents for telemetry
                for agent_score in result.recommended_agents[:5]:
                    top_agents.append({
                        "agent_id": agent_score.agent_id,
                        "score": agent_score.score,
                        "match_reasons": agent_score.match_reasons[:2] if agent_score.match_reasons else []
                    })
                
                # Calculate result quality score (average of top 3 scores)
                top_scores = [agent.score for agent in result.recommended_agents[:3]]
                result_quality_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
                
                # Determine search method (check if MongoDB was used)
                if hasattr(self.discovery, 'use_mongodb') and self.discovery.use_mongodb:
                    if structure_type:
                        search_method = f"mongodb_{structure_type}"
                    else:
                        search_method = "mongodb"
                else:
                    search_method = "registry"
            
            # Format response
            if not result.recommended_agents:
                response_text = f"🔍 No agents found for: '{query}'\n\n"
                response_text += "💡 Suggestions:\n"
                for suggestion in result.suggestions[:3]:
                    response_text += f"  • {suggestion}\n"
            else:
                structure_info = f" ({structure_type} structure)" if structure_type else ""
                response_text = f"🔍 Found {len(result.recommended_agents)} agents{structure_info} for: '{query}'\n\n"
                
                for i, agent_score in enumerate(result.recommended_agents, 1):
                    response_text += f"{i}. @{agent_score.agent_id} (Score: {agent_score.score:.2f})\n"
                    
                    # Try to get detailed agent data
                    agent_data = self.discovery.get_agent_details(agent_score.agent_id)
                    if agent_data:
                        response_text += f"   📋 {agent_data.get('description', 'No description')}\n"
                        capabilities = agent_data.get('capabilities', [])
                        if capabilities:
                            response_text += f"   🏷️ {', '.join(capabilities[:3])}\n"
                    else:
                        response_text += f"   📋 Agent available in registry\n"
                    
                    # Show match reasons if available
                    if agent_score.match_reasons:
                        response_text += f"   ✅ {agent_score.match_reasons[0]}\n"
                    
                    response_text += "\n"
                
                response_text += f"💬 To contact an agent, use: @agent-id your message\n"
                response_text += f"⏱️ Search completed in {search_time:.2f}s"
            
            # Log structured telemetry to MongoDB
            if self.telemetry:
                response_time = time.time() - search_start
                self.telemetry.log_structured_query(
                    query_text=query,
                    query_type="search",
                    conversation_id=conversation_id,
                    search_time=search_time,
                    agents_found=len(result.recommended_agents),
                    search_method=search_method,
                    top_agents=top_agents,
                    result_quality_score=result_quality_score,
                    response_time=response_time,
                    success=True
                )
            
            return self._create_response(original_msg, conversation_id, response_text)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            if self.telemetry:
                self.telemetry.log_error(f"Search query failed: {str(e)}", {"query": query})
                
                # Log failed search to structured telemetry
                response_time = time.time() - search_start if 'search_start' in locals() else 0.0
                self.telemetry.log_structured_query(
                    query_text=query,
                    query_type="search",
                    conversation_id=conversation_id,
                    search_time=0.0,
                    agents_found=0,
                    search_method="error",
                    top_agents=[],
                    result_quality_score=0.0,
                    response_time=response_time,
                    success=False,
                    error_message=str(e)
                )
            
            return self._create_response(
                original_msg, conversation_id,
                f"🔍 Search failed: {str(e)}"
            )
    
    def _handle_agent_mention(self, user_text: str, original_msg: Message, conversation_id: str) -> Message:
        """Handle @agent-id mentions for A2A communication"""
        try:
            # Parse @agent-id message format
            parts = user_text.split(" ", 1)
            if len(parts) < 2:
                return self._create_response(
                    original_msg, conversation_id,
                    "💬 Usage: @agent-id your message\nExample: @data-scientist Can you analyze this data?"
                )
            
            target_agent_id = parts[0][1:]  # Remove @ symbol
            message_text = parts[1]
            
            # Send message to target agent
            response = self._send_to_agent(target_agent_id, message_text, conversation_id)
            
            # Log response time for telemetry
            if self.telemetry:
                response_time = time.time() - time.time()  # This would be calculated properly in real implementation
                self.telemetry.log_response_time(response_time, "agent_to_agent")
            
            return self._create_response(original_msg, conversation_id, response)
            
        except Exception as e:
            logger.error(f"Agent mention error: {e}")
            if self.telemetry:
                self.telemetry.log_error(f"Agent mention failed: {str(e)}", {"message": user_text})
            
            return self._create_response(
                original_msg, conversation_id,
                f"💬 Failed to contact agent: {str(e)}"
            )
    
    def _extract_keywords_with_llm(self, query: str) -> List[str]:
        """Extract 5 keywords from query using LLM"""
        try:
            # Use the same agent logic (Claude API) that the agent already has
            keyword_prompt = f"""Extract exactly 5 keywords from this query that best represent the core concepts and requirements. Return only the keywords separated by commas, no other text.

Query: {query}

Keywords:"""
            
            # Call the agent's own LLM logic for keyword extraction
            response = self.agent_logic(keyword_prompt, "keyword_extraction")
            
            # Parse the response to extract keywords
            keywords = []
            if response:
                # Clean and split the response
                clean_response = response.strip()
                # Remove any agent ID prefix if present
                if ']' in clean_response:
                    clean_response = clean_response.split(']', 1)[-1].strip()
                
                # Split by commas and clean each keyword
                raw_keywords = clean_response.split(',')
                for keyword in raw_keywords:
                    clean_keyword = keyword.strip().lower()
                    if clean_keyword and len(clean_keyword) > 1:
                        keywords.append(clean_keyword)
                
                # Ensure we have exactly 5 keywords
                keywords = keywords[:5]
                
                # If we don't have enough, pad with query words
                if len(keywords) < 5:
                    query_words = [word.lower().strip() for word in query.split() if len(word) > 2]
                    for word in query_words:
                        if word not in keywords and len(keywords) < 5:
                            keywords.append(word)
            
            # Fallback: use query words if LLM extraction failed
            if not keywords:
                keywords = [word.lower().strip() for word in query.split() if len(word) > 2][:5]
            
            logger.info(f"🔑 [{self.agent_id}] Extracted keywords: {keywords}")
            return keywords
            
        except Exception as e:
            logger.error(f"❌ [{self.agent_id}] Keyword extraction failed: {e}")
            # Fallback to simple word splitting
            return [word.lower().strip() for word in query.split() if len(word) > 2][:5]
    
    def _handle_direct_question(self, query: str, original_msg: Message, conversation_id: str, search_start: float) -> Message:
        """Handle direct questions with new flow: 1 question → 15 interactions"""
        # Check if discovery system is available
        if not self.discovery:
            return self._create_response(
                original_msg, conversation_id,
                "🔍 Agent discovery not available. Registry connection required."
            )
        
        try:
            logger.info(f"🎯 [{self.agent_id}] Processing direct question: {query}")
            
            # Step 1: Search across all 3 capability structures
            all_agents = []
            search_results = {}
            
            # Keywords structure: Extract keywords with LLM
            logger.info(f"🔑 [{self.agent_id}] Searching keywords structure...")
            keywords = self._extract_keywords_with_llm(query)
            keywords_query = " ".join(keywords)
            keywords_result = self.discovery.discover_agents(keywords_query, limit=5, min_score=0.3, structure_type="keywords")
            search_results["keywords"] = {
                "agents": keywords_result.recommended_agents,
                "method": f"LLM keywords: {keywords}"
            }
            all_agents.extend([(agent, "keywords") for agent in keywords_result.recommended_agents])
            
            # Description structure: Direct text matching
            logger.info(f"📝 [{self.agent_id}] Searching description structure...")
            description_result = self.discovery.discover_agents(query, limit=5, min_score=0.3, structure_type="description")
            search_results["description"] = {
                "agents": description_result.recommended_agents,
                "method": "Direct text matching"
            }
            all_agents.extend([(agent, "description") for agent in description_result.recommended_agents])
            
            # Embedding structure: Cosine similarity
            logger.info(f"🔗 [{self.agent_id}] Searching embedding structure...")
            embedding_result = self.discovery.discover_agents(query, limit=5, min_score=0.3, structure_type="embedding")
            search_results["embedding"] = {
                "agents": embedding_result.recommended_agents,
                "method": "Cosine similarity"
            }
            all_agents.extend([(agent, "embedding") for agent in embedding_result.recommended_agents])
            
            search_time = time.time() - search_start
            total_agents_found = len(all_agents)
            
            logger.info(f"📊 [{self.agent_id}] Found {total_agents_found} agents total across all structures")
            
            # Step 2: Ask the original question to all found agents
            qa_interactions = []
            if all_agents:
                logger.info(f"❓ [{self.agent_id}] Asking question to {total_agents_found} agents...")
                
                for agent_score, structure_type in all_agents:
                    try:
                        # Look up agent URL
                        agent_url = self._lookup_agent(agent_score.agent_id)
                        if not agent_url:
                            continue
                        
                        # Ensure URL has /a2a endpoint
                        if not agent_url.endswith('/a2a'):
                            agent_url = f"{agent_url}/a2a"
                        
                        # Ask the original question
                        client = A2AClient(agent_url, timeout=30)
                        start_time = time.time()
                        response = client.send_message(
                            Message(
                                role=MessageRole.USER,
                                content=TextContent(text=query),
                                conversation_id=conversation_id
                            )
                        )
                        response_time = time.time() - start_time
                        
                        # Extract response
                        answer = "No response"
                        if response and hasattr(response, 'parts') and response.parts:
                            answer = response.parts[0].text
                        
                        qa_interactions.append({
                            "agent_id": agent_score.agent_id,
                            "structure_type": structure_type,
                            "score": agent_score.score,
                            "question": query,
                            "answer": answer,
                            "response_time": response_time,
                            "success": True
                        })
                        
                        logger.info(f"✅ [{self.agent_id}] Got response from {agent_score.agent_id} ({structure_type})")
                        
                    except Exception as e:
                        logger.error(f"❌ [{self.agent_id}] Failed to get response from {agent_score.agent_id}: {e}")
                        qa_interactions.append({
                            "agent_id": agent_score.agent_id,
                            "structure_type": structure_type,
                            "score": agent_score.score,
                            "question": query,
                            "answer": f"Error: {str(e)}",
                            "response_time": 0,
                            "success": False
                        })
            
            # Step 3: Format response showing all Q&A pairs
            response_text = self._format_direct_question_response(query, search_results, qa_interactions, search_time)
            
            # Step 4: Log telemetry
            if self.telemetry:
                self.telemetry.log_agent_discovery(query, total_agents_found, search_time)
                # TODO: Add structured telemetry for Q&A interactions
            
            return self._create_response(original_msg, conversation_id, response_text)
            
        except Exception as e:
            logger.error(f"❌ [{self.agent_id}] Direct question handling failed: {e}")
            return self._create_response(
                original_msg, conversation_id,
                f"❌ Error processing question: {str(e)}"
            )
    
    def _format_direct_question_response(self, query: str, search_results: Dict, qa_interactions: List[Dict], search_time: float) -> str:
        """Format the response for direct questions showing all Q&A pairs"""
        response_text = f"🎯 Question: '{query}'\n"
        response_text += f"⏱️ Search completed in {search_time:.2f}s\n\n"
        
        # Show search summary
        total_found = sum(len(result["agents"]) for result in search_results.values())
        response_text += f"📊 Found {total_found} agents across {len(search_results)} structures:\n"
        
        for structure, result in search_results.items():
            agent_count = len(result["agents"])
            method = result["method"]
            response_text += f"  • {structure.capitalize()}: {agent_count} agents ({method})\n"
        
        response_text += f"\n💬 Responses from {len(qa_interactions)} agents:\n"
        response_text += "=" * 50 + "\n\n"
        
        # Group by structure type for better organization
        for structure in ["keywords", "description", "embedding"]:
            structure_interactions = [qa for qa in qa_interactions if qa["structure_type"] == structure]
            if structure_interactions:
                response_text += f"🔍 {structure.upper()} STRUCTURE:\n"
                response_text += "-" * 30 + "\n"
                
                for i, qa in enumerate(structure_interactions, 1):
                    response_text += f"{i}. @{qa['agent_id']} (Score: {qa['score']:.2f})\n"
                    response_text += f"   Q: {qa['question']}\n"
                    response_text += f"   A: {qa['answer'][:200]}{'...' if len(qa['answer']) > 200 else ''}\n"
                    response_text += f"   ⏱️ {qa['response_time']:.2f}s\n\n"
                
                response_text += "\n"
        
        return response_text