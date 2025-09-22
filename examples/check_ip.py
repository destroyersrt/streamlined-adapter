#!/usr/bin/env python3
"""
Quick IP address detection for A2A testing
"""

import socket

def get_local_ip():
    """Get the local IP address"""
    try:
        # Connect to a remote address to determine local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error detecting IP: {e}")
        return "localhost"

if __name__ == "__main__":
    ip = get_local_ip()
    print(f"🌐 Detected IP address: {ip}")
    print(f"📡 Agent endpoints will be:")
    print(f"   Sarcastic Agent: http://{ip}:6002/a2a")
    print(f"   Helpful Agent:   http://{ip}:6003/a2a")
    print(f"")
    print(f"🧪 Test curl commands:")
    print(f"curl -X POST http://{ip}:6002/a2a \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"role\": \"user\", \"content\": {{\"type\": \"text\", \"text\": \"hello\"}}, \"conversation_id\": \"test\"}}'")
    print(f"")
    print(f"curl -X POST http://{ip}:6002/a2a \\")
    print(f"  -H 'Content-Type: application/json' \\")
    print(f"  -d '{{\"role\": \"user\", \"content\": {{\"type\": \"text\", \"text\": \"@helpful_agent Hello from sarcastic!\"}}, \"conversation_id\": \"test_a2a\"}}'")