# NANDA Adapter Examples

Simple examples demonstrating the clean NANDA adapter functionality.

## 🔧 Modular Agent System (NEW!)

### `nanda_agent.py` - Customizable Agent Template
A modular template that makes it easy to create agents with different personalities and expertise by simply changing the configuration.

**Key Features:**
- **Easy customization** - Change personality, expertise, and responses
- **Modular design** - Separate configuration from logic  
- **Multiple agent types** - Support for different specializations
- **Random responses** - Varied greeting messages
- **Extensible** - Easy to add new capabilities

**Usage:**
```python
# Basic usage
python3 nanda_agent.py

# Create custom agent
from modular_agent import create_custom_agent
create_custom_agent(
    agent_name="Data Scientist", 
    personality="analytical and precise",
    expertise_list=["data analysis", "statistics", "machine learning"],
    port=6001
)
```

### `agent_configs.py` - Pre-configured Agent Types  
Ready-to-use agent configurations for different personalities:

- **Helpful Assistant** - General purpose helper
- **Data Scientist** - Analytics and data specialist
- **Pirate Captain** - Swashbuckling adventure theme  
- **Tech Support** - Technical troubleshooting expert
- **Chef** - Culinary assistant

**Usage:**
```python
from agent_configs import create_data_scientist_agent, PIRATE_CONFIG
from modular_agent import create_agent_logic
from nanda_core.core.adapter import NANDA

# Quick creation
agent = create_data_scientist_agent(port=6001)
agent.start()

# Or use config directly  
agent_logic = create_agent_logic(PIRATE_CONFIG)
nanda = NANDA("pirate", agent_logic, 6002)
nanda.start()
```

## 📝 Basic Examples

## Files

### `simple_test.py`
**Basic single agent example** - Shows how to create and start a single agent in just a few lines:

```bash
cd streamlined_adapter
python examples/simple_test.py
```

Features demonstrated:
- Create agent with custom logic
- Start server on specific port  
- Handle basic commands (`/help`, `/ping`, `/status`)
- Process regular messages

### `a2a_test.py`
**Agent-to-Agent communication test** - Demonstrates two agents talking to each other:

```bash
cd streamlined_adapter  
python examples/a2a_test.py
```

Features demonstrated:
- Start multiple agents on different ports
- Send messages between agents using `@agent_id message` format
- Agent discovery and routing
- Clean logging of A2A communication
- Different agent personalities

## Quick Start

Create your own agent in just 6 lines:

```python
from streamlined_adapter import NANDA, helpful_agent

nanda = NANDA(
    agent_id="my_agent",
    agent_logic=helpful_agent,
    port=6000
)
nanda.start()
```

## Testing A2A Communication

1. Start first agent: `python examples/simple_test.py` (port 6005)
2. In another terminal, send a message to it via curl or another agent
3. Use `@agent_id message` format to route messages between agents

## Agent Logic Function

Your agent logic function should have this signature:

```python
def my_agent_logic(message: str, conversation_id: str) -> str:
    return f"Agent response: {message}"
```

The function receives the incoming message and conversation ID, and returns a response string.
