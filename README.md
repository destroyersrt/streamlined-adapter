# Streamlined NANDA Adapter

A streamlined, feature-rich adapter for the NANDA Agent Framework that maintains full functionality parity with the original while eliminating unnecessary query preprocessing and adding intelligent agent discovery and comprehensive monitoring capabilities.

## Key Features

### ✅ Core Functionality (Maintained)
- **MCP Server Discovery**: Full support for MCP server discovery from directories and registries
- **Google A2A Protocol**: Complete agent-to-agent communication protocol support
- **Nanda Index Registry**: Full integration with the Nanda registry for agent discovery

### ❌ Removed Features
- **Message Improvement Functions**: All `call_claude` functions that enhance/modify user queries have been removed
- **Query Preprocessing**: No automatic modification of user messages before sending

### 🚀 New Features

#### 1. Intelligent Agent Discovery
- **Task Analysis**: NLP-powered analysis of user tasks to understand requirements
- **Agent Ranking**: Sophisticated scoring algorithm that ranks agents by suitability
- **Smart Recommendations**: Confidence-scored recommendations with explanations

#### 2. Comprehensive Telemetry System
- **Usage Monitoring**: Track message patterns, agent interactions, and system usage
- **Performance Metrics**: Response times, error rates, throughput measurement
- **System Health**: CPU, memory, disk monitoring with alerting
- **Export Capabilities**: JSON/CSV export for external analysis

## Quick Start

### Installation

```bash
pip install streamlined-nanda-adapter
```

### Basic Usage

```python
from streamlined_adapter import StreamlinedAdapter

# Create adapter instance
adapter = StreamlinedAdapter(agent_id="my_agent")

# Start server (blocking)
adapter.start_server()
```

### Agent Discovery

```python
# Discover agents for a specific task
result = adapter.discover_agents("I need to analyze sales data and create visualizations")

print(f"Found {len(result['recommended_agents'])} agents:")
for agent in result['recommended_agents']:
    print(f"- {agent['agent_id']}: {agent['score']:.2f} ({agent['confidence']:.2f})")
```

### Health Monitoring

```python
# Get health status
health = adapter.get_health_status()
print(f"Overall status: {health['overall_status']}")

# Get metrics summary
metrics = adapter.get_metrics_summary(hours=24)
print(f"Total events: {metrics['total_events']}")
```

## Architecture

```
streamlined_adapter/
├── nanda_core/
│   ├── core/
│   │   ├── adapter.py           # Main adapter class
│   │   ├── agent_bridge.py      # A2A protocol bridge
│   │   ├── mcp_client.py        # MCP server client
│   │   └── registry_client.py   # Registry integration
│   ├── discovery/
│   │   ├── agent_discovery.py   # Main discovery system
│   │   ├── task_analyzer.py     # Task analysis engine
│   │   └── agent_ranker.py      # Agent ranking system
│   └── telemetry/
│       ├── telemetry_system.py  # Main telemetry system
│       ├── metrics_collector.py # System metrics collection
│       └── health_monitor.py    # Health monitoring
```

## Functionality Comparison

| Feature | Original Adapter | Streamlined Adapter |
|---------|------------------|-------------------|
| MCP Server Discovery | ✅ | ✅ |
| Google A2A Protocol | ✅ | ✅ |
| Registry Integration | ✅ | ✅ |
| Message Improvement | ✅ | ❌ (Removed) |
| Query Enhancement | ✅ | ❌ (Removed) |
| Agent Discovery | ❌ | ✅ (New) |
| Task Analysis | ❌ | ✅ (New) |
| Agent Ranking | ❌ | ✅ (New) |
| Telemetry System | ❌ | ✅ (New) |
| Health Monitoring | ❌ | ✅ (New) |
| Performance Metrics | ❌ | ✅ (New) |

## Command Line Usage

### Start Adapter Server
```bash
streamlined-adapter --agent-id my_agent --port 6000
```

### Discover Agents
```bash
nanda-discover "Create a dashboard for sales analytics"
```

## Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_key
AGENT_ID=your_agent_id

# Optional
PORT=6000
PUBLIC_URL=http://your-server:6000
API_URL=https://your-api.com
REGISTRY_URL=https://chat.nanda-registry.com:6900
SMITHERY_API_KEY=your_smithery_key
```

## Message Formats

### Agent Communication
```
@target_agent Your message here
```

### MCP Server Queries
```
#registry_provider:server_name Your query here
```

### System Commands
```
/help
/quit
```

## Performance

The streamlined adapter provides significant performance improvements:

- **Reduced Latency**: No message preprocessing means faster response times
- **Lower Resource Usage**: Eliminated Claude API calls for message improvement
- **Better Monitoring**: Comprehensive telemetry provides visibility into performance
- **Intelligent Routing**: Smart agent discovery reduces trial-and-error

## Telemetry Data

The telemetry system collects:

- **Message Events**: Sent/received messages, conversation tracking
- **MCP Queries**: Server interactions, response times
- **Agent Discovery**: Search operations, ranking performance
- **System Metrics**: CPU, memory, disk usage
- **Health Checks**: Registry connectivity, system status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For support and questions:
- Email: support@nanda.ai
- GitHub Issues: [Create an issue](https://github.com/projnanda/streamlined-adapter/issues)