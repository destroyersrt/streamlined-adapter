#!/usr/bin/env python3
"""
NANDA Compatibility Layer for Streamlined Adapter

Provides backwards compatibility with the original NANDA interface while using
the streamlined adapter architecture underneath.
"""

import os
import sys
import threading
from typing import Callable, Optional, Dict, Any
from .adapter import StreamlinedAdapter


class NANDA:
    """
    Backwards compatibility class that mimics the original NANDA interface
    but uses the streamlined adapter underneath without message improvement.
    """
    
    def __init__(self, improvement_logic: Callable[[str], str]):
        """
        Initialize NANDA with custom improvement logic
        
        Note: In the streamlined version, this becomes a custom response handler
        instead of a message modifier.
        
        Args:
            improvement_logic: Function that takes (message_text: str) -> str
                             This will be converted to a response handler, not message modifier
        """
        self.improvement_logic = improvement_logic
        self.adapter = None
        
        print(f"🤖 NANDA (Streamlined) initialized with handler logic: {improvement_logic.__name__}")
        print("⚠️  Note: This logic will be used for agent responses, NOT message modification")
        
        # Create the streamlined adapter
        self._create_adapter()
        
        # Set up custom handlers
        self._setup_handlers()
    
    def _create_adapter(self):
        """Create the underlying streamlined adapter"""
        # Get agent configuration from environment
        agent_id = os.getenv("AGENT_ID", "nanda_agent")
        self.adapter = StreamlinedAdapter(agent_id)
        print(f"✅ Streamlined adapter created for agent: {agent_id}")
    
    def _setup_handlers(self):
        """Set up custom handlers using the improvement logic"""
        
        def response_handler(message_text: str, conversation_id: str) -> str:
            """Convert improvement logic to response handler"""
            try:
                # Use the improvement logic as a response generator
                response = self.improvement_logic(message_text)
                return f"Agent Response: {response}"
            except Exception as e:
                print(f"Error in custom handler: {e}")
                return f"Received: {message_text}"
        
        # Set the handler
        self.adapter.set_message_handler(response_handler)
        print(f"🔧 Custom response handler '{self.improvement_logic.__name__}' configured")
    
    def start_server(self, host: str = "0.0.0.0"):
        """
        Start the agent bridge server
        
        Args:
            host: Host to bind to (default: "0.0.0.0")
        """
        print("🚀 NANDA (Streamlined) starting server...")
        
        # Read configuration from environment
        public_url = os.getenv("PUBLIC_URL")
        api_url = os.getenv("API_URL")
        
        # Register with registry if PUBLIC_URL is set
        register_with_registry = bool(public_url)
        
        if public_url:
            print(f"📝 Will register agent with registry using URL: {public_url}")
        else:
            print("⚠️  PUBLIC_URL not set - agent will not be registered with registry")
        
        # Start the streamlined adapter server
        self.adapter.start_server(host=host, register_with_registry=register_with_registry)
    
    def start_server_api(self, anthropic_key: str, domain: str, agent_id: Optional[str] = None, 
                        port: int = 6000, api_port: int = 6001, **kwargs):
        """
        Start NANDA with API server support (backwards compatibility)
        
        Args:
            anthropic_key: Anthropic API key
            domain: Domain name for the server
            agent_id: Agent ID (optional)
            port: Agent bridge port
            api_port: API server port
            **kwargs: Additional arguments (for compatibility)
        """
        print("🚀 NANDA (Streamlined) starting with API server support...")
        
        # Set environment variables for compatibility
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        if agent_id:
            os.environ["AGENT_ID"] = agent_id
        os.environ["PORT"] = str(port)
        
        # Generate URLs based on domain
        public_url = f"https://{domain}:{port}"
        api_url = f"https://{domain}:{api_port}"
        
        os.environ["PUBLIC_URL"] = public_url
        os.environ["API_URL"] = api_url
        
        print(f"🌐 Domain: {domain}")
        print(f"🔗 Public URL: {public_url}")
        print(f"🔗 API URL: {api_url}")
        
        # Start the Flask API server in a separate thread
        self._start_api_server(api_port)
        
        # Start the main agent server
        self.start_server()
    
    def _start_api_server(self, api_port: int):
        """Start a simple Flask API server for compatibility"""
        try:
            from flask import Flask, request, jsonify
            from flask_cors import CORS
            
            app = Flask(__name__)
            CORS(app)
            
            @app.route('/api/health', methods=['GET'])
            def health_check():
                return jsonify({"status": "healthy", "agent_id": self.adapter.agent_id})
            
            @app.route('/api/send', methods=['POST'])
            def send_message():
                data = request.get_json()
                message = data.get('message', '')
                # This would typically send to the agent
                return jsonify({"status": "message received", "message": message})
            
            @app.route('/api/agents/list', methods=['GET'])
            def list_agents():
                agents = self.adapter.list_available_agents()
                return jsonify(agents)
            
            @app.route('/api/receive_message', methods=['POST'])
            def receive_message():
                data = request.get_json()
                # Handle incoming messages from UI clients
                return jsonify({"status": "ok"})
            
            @app.route('/api/render', methods=['GET'])
            def render():
                # Return latest message (for compatibility)
                return jsonify({"message": "No recent messages"})
            
            def run_flask():
                print(f"📡 Starting API server on port {api_port}")
                app.run(host='0.0.0.0', port=api_port, ssl_context='adhoc', debug=False)
            
            # Start Flask in background thread
            api_thread = threading.Thread(target=run_flask, daemon=True)
            api_thread.start()
            
        except ImportError:
            print("⚠️  Flask not available - API server will not start")
            print("   Install with: pip install flask flask-cors pyopenssl")
    
    @property
    def bridge(self):
        """Access to the underlying bridge (for compatibility)"""
        return self.adapter.bridge
    
    def stop(self):
        """Stop the NANDA server"""
        if self.adapter:
            self.adapter.stop()


# Utility functions for compatibility
def create_nanda_adapter(improvement_logic: Callable[[str], str]) -> NANDA:
    """Create a NANDA adapter with custom improvement logic"""
    return NANDA(improvement_logic)


def start_nanda_server(improvement_logic: Callable[[str], str], **kwargs):
    """Quick start function for NANDA server"""
    nanda = NANDA(improvement_logic)
    
    if 'anthropic_key' in kwargs and 'domain' in kwargs:
        nanda.start_server_api(**kwargs)
    else:
        nanda.start_server()
    
    return nanda


# Example improvement functions for testing
def example_pirate_improver(message: str) -> str:
    """Example pirate-style message improver"""
    return f"Arrr! {message}, matey!"


def example_professional_improver(message: str) -> str:
    """Example professional message improver"""
    return f"I would like to formally communicate: {message}"


def example_echo_improver(message: str) -> str:
    """Example echo improver"""
    return f"Echo: {message}"


if __name__ == "__main__":
    # Test the NANDA compatibility layer
    print("🧪 Testing NANDA Compatibility Layer")
    
    # Test with a simple improvement function
    def test_improver(message: str) -> str:
        return f"Improved: {message}"
    
    # Create NANDA instance
    nanda = NANDA(test_improver)
    
    print(f"✅ NANDA instance created with agent ID: {nanda.adapter.agent_id}")
    print("🚀 Starting server...")
    
    try:
        nanda.start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        nanda.stop()

