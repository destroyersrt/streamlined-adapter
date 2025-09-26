# NANDA Adapter Examples

Simple examples demonstrating the clean NANDA adapter functionality.

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
