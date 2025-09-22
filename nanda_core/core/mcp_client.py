#!/usr/bin/env python3
"""
Streamlined MCP Client for the NANDA Adapter
Handles MCP server discovery and communication without message improvement
"""

import json
import base64
import asyncio
from typing import Optional, Dict, Any, List
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.client.streamable_http import streamablehttp_client
import mcp
from anthropic import Anthropic
import os


class MCPClient:
    """Streamlined MCP client without message preprocessing"""

    def __init__(self):
        self.session = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

    async def connect_to_server(self, server_url: str, transport_type: str = "http") -> Optional[List[Any]]:
        """Connect to MCP server and return available tools"""
        try:
            if transport_type.lower() == "sse":
                transport = await self.exit_stack.enter_async_context(sse_client(server_url))
                read_stream, write_stream = transport
            else:
                transport = await self.exit_stack.enter_async_context(streamablehttp_client(server_url))
                read_stream, write_stream, _ = transport

            self.session = await self.exit_stack.enter_async_context(
                mcp.ClientSession(read_stream, write_stream)
            )
            await self.session.initialize()

            tools_result = await self.session.list_tools()
            return tools_result.tools
        except Exception as e:
            print(f"Error connecting to MCP server: {e}")
            return None

    async def execute_query(self, query: str, server_url: str, transport_type: str = "http") -> str:
        """Execute query on MCP server without message improvement"""
        try:
            tools = await self.connect_to_server(server_url, transport_type)
            if not tools:
                return "Failed to connect to MCP server"

            available_tools = [{
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            } for tool in tools]

            messages = [{"role": "user", "content": query}]

            message = self.anthropic.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=messages,
                tools=available_tools
            )

            while True:
                has_tool_calls = False

                for block in message.content:
                    if block.type == "tool_use":
                        has_tool_calls = True
                        result = await self.session.call_tool(block.name, block.input)
                        processed_result = self._parse_result(result)

                        messages.append({
                            "role": "assistant",
                            "content": [{
                                "type": "tool_use",
                                "id": block.id,
                                "name": block.name,
                                "input": block.input
                            }]
                        })

                        messages.append({
                            "role": "user",
                            "content": [{
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": str(processed_result)
                            }]
                        })

                if not has_tool_calls:
                    break

                message = self.anthropic.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    messages=messages,
                    tools=available_tools
                )

            final_response = ""
            for block in message.content:
                if block.type == "text":
                    final_response += block.text + "\n"

            return self._parse_result(final_response.strip()) if final_response else "No response generated"

        except Exception as e:
            return f"Error: {str(e)}"

    def _parse_result(self, response: Any) -> str:
        """Parse JSON-RPC responses from MCP server"""
        if isinstance(response, str):
            try:
                response_json = json.loads(response)
                if isinstance(response_json, dict) and "result" in response_json:
                    artifacts = response_json["result"].get("artifacts", [])
                    if artifacts and len(artifacts) > 0:
                        parts = artifacts[0].get("parts", [])
                        if parts and len(parts) > 0:
                            return parts[0].get("text", str(response))
            except json.JSONDecodeError:
                pass
        return str(response)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.exit_stack.aclose()
        self.session = None


class MCPRegistry:
    """Handles MCP server discovery from the registry"""

    def __init__(self, registry_url: str):
        self.registry_url = registry_url
        self.smithery_api_key = os.getenv("SMITHERY_API_KEY", "")

    def get_server_config(self, registry_provider: str, qualified_name: str) -> Optional[Dict[str, Any]]:
        """Query registry for MCP server configuration"""
        try:
            import requests

            response = requests.get(f"{self.registry_url}/get_mcp_registry", params={
                'registry_provider': registry_provider,
                'qualified_name': qualified_name
            })

            if response.status_code == 200:
                result = response.json()
                endpoint = result.get("endpoint")
                config = result.get("config")
                config_json = json.loads(config) if isinstance(config, str) else config
                registry_name = result.get("registry_provider")

                return {
                    "endpoint": endpoint,
                    "config": config_json,
                    "registry_provider": registry_name
                }
            return None

        except Exception as e:
            print(f"Error querying MCP registry: {e}")
            return None

    def build_server_url(self, endpoint: str, config: Dict[str, Any], registry_provider: str) -> Optional[str]:
        """Build the final MCP server URL with authentication"""
        try:
            if registry_provider == "smithery":
                if not self.smithery_api_key:
                    print("SMITHERY_API_KEY not found in environment")
                    return None

                config_b64 = base64.b64encode(json.dumps(config).encode()).decode()
                return f"{endpoint}?api_key={self.smithery_api_key}&config={config_b64}"
            else:
                return endpoint
        except Exception as e:
            print(f"Error building server URL: {e}")
            return None