# NANDA Agent Deployment Scripts

Simple deployment scripts for NANDA agents on cloud servers.

## Quick Deploy

Deploy any agent type with a single command:

```bash
bash scripts/deploy-agent.sh <AGENT_TYPE> <AGENT_ID> <ANTHROPIC_API_KEY> [PORT] [REGISTRY_URL]
```

### Examples

```bash
# Deploy helpful agent
bash scripts/deploy-agent.sh helpful my_helper sk-ant-xxxxx

# Deploy LangChain analyst agent on port 6020  
bash scripts/deploy-agent.sh analyst doc_analyzer sk-ant-xxxxx 6020

# Deploy with registry registration
bash scripts/deploy-agent.sh pirate captain_jack sk-ant-xxxxx 6000 https://registry.example.com
```

## Agent Types

| Type | Description | Dependencies |
|------|-------------|--------------|
| `helpful` | General helpful agent (default) | None |
| `pirate` | Pirate personality agent | None |
| `echo` | Simple echo agent | None |
| `analyst` | LangChain + Anthropic document analyst | LangChain |

## What the Script Does

1. **System Setup** - Updates system, installs Python 3
2. **Clone Adapter** - Downloads streamlined adapter from GitHub
3. **Environment** - Creates Python virtual environment  
4. **Dependencies** - Installs required packages (anthropic, python-a2a, etc.)
5. **Agent Creation** - Generates custom agent script
6. **Launch** - Starts agent in background

## Output

After successful deployment:

```
🎉 NANDA Agent Deployment Complete!
====================================
Agent ID: my_helper
Type: helpful
Port: 6000
Directory: /home/user/nanda-agent-my_helper

🚀 Agent started successfully (PID: 12345)

📋 Useful commands:
  • View logs: tail -f /home/user/nanda-agent-my_helper/agent.log
  • Stop agent: kill 12345
  • Test agent: curl -X POST http://localhost:6000/a2a ...

🔗 Agent URL: http://your-server-ip:6000/a2a
```

## Server Requirements

- **Ubuntu/Debian**: `sudo` access for package installation
- **Amazon Linux/RHEL**: `sudo` access for package installation  
- **Python**: 3.8+ (script installs if missing)
- **Network**: Port access for agent communication

## Testing Your Agent

Once deployed, test your agent:

```bash
# Test basic functionality
curl -X POST http://localhost:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"hello"}}'

# View logs
tail -f ~/nanda-agent-*/agent.log

# Test agent-to-agent communication (if you have multiple agents)
curl -X POST http://localhost:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"@other_agent Hello there!"}}'
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change port number
2. **Permission denied**: Ensure sudo access
3. **API key invalid**: Check ANTHROPIC_API_KEY
4. **LangChain missing**: For analyst agent, ensure dependencies install correctly

### Log Files

- **Agent logs**: `~/nanda-agent-*/agent.log`
- **Installation logs**: Check terminal output during deployment

### Manual Management

```bash
# Find your agent process
ps aux | grep python3 | grep run_agent

# Stop agent
kill <PID>

# Restart agent  
cd ~/nanda-agent-*
source env/bin/activate
python3 run_agent.py &
```

## Custom Agents

To create custom agents, see the template in `/templates/custom_agent_template.py` and modify the deployment script or create your own agent logic.
