# Multi-Agent Deployment Guide

## Overview

The `aws-ec2-deploy-multi-agent.sh` script allows you to deploy multiple NANDA agents on a single EC2 instance. This is cost-effective and efficient for running multiple specialized agents that don't require high individual resource allocation.

## Key Features

- **Multiple Agents**: Deploy up to 10+ agents on a single EC2 instance
- **Individual Ports**: Each agent runs on its own port (6000-6009+)
- **Process Management**: Uses supervisor to manage all agent processes
- **Automatic Restart**: Agents automatically restart if they crash
- **Centralized Logging**: Individual logs for each agent
- **Cost Effective**: Share resources across multiple agents

## Usage

### Basic Usage

```bash
bash aws-ec2-deploy-multi-agent.sh <ANTHROPIC_API_KEY> <AGENT_CONFIG_JSON> [REGISTRY_URL] [REGION] [INSTANCE_TYPE]
```

### Parameters

- **ANTHROPIC_API_KEY**: Your Anthropic API key (required)
- **AGENT_CONFIG_JSON**: JSON string or file path with agent configurations (required)
- **REGISTRY_URL**: Optional registry URL for agent discovery
- **REGION**: AWS region (default: us-east-1)
- **INSTANCE_TYPE**: EC2 instance type (default: t3.small - recommended for multiple agents)

### Example with Configuration File

```bash
# Using the example configuration file
bash aws-ec2-deploy-multi-agent.sh \
  "sk-ant-your-api-key-here" \
  "example-multi-agent-config.json" \
  "https://your-registry.com" \
  "us-east-1" \
  "t3.medium"
```

### Example with Inline JSON

```bash
bash aws-ec2-deploy-multi-agent.sh \
  "sk-ant-your-api-key-here" \
  '[
    {
      "agent_id": "data-scientist-001",
      "agent_name": "Dr. Data",
      "domain": "data analysis",
      "specialization": "analytical and precise AI assistant",
      "description": "I specialize in data analysis and statistics.",
      "capabilities": "data analysis,statistics,machine learning,Python,R",
      "port": 6000
    },
    {
      "agent_id": "tech-support-001",
      "agent_name": "TechWiz",
      "domain": "technical support",
      "specialization": "patient and knowledgeable tech specialist",
      "description": "I help with troubleshooting and technical issues.",
      "capabilities": "troubleshooting,software installation,network configuration",
      "port": 6001
    }
  ]'
```

## Agent Configuration Format

Each agent in the JSON array must have these fields:

```json
{
  "agent_id": "unique-agent-identifier",
  "agent_name": "Display Name",
  "domain": "primary expertise area",
  "specialization": "personality description",
  "description": "detailed agent description",
  "capabilities": "comma,separated,capabilities",
  "port": 6000
}
```

### Port Assignment Guidelines

- Use ports 6000-6099 for your agents
- Each agent must have a unique port
- The script automatically opens all specified ports in the security group

## Instance Size Recommendations

| Number of Agents | Recommended Instance Type | Monthly Cost (approx.) |
|-------------------|---------------------------|-------------------------|
| 1-3 agents        | t3.micro                  | $8-10                   |
| 4-6 agents        | t3.small                  | $15-20                  |
| 7-10 agents       | t3.medium                 | $30-35                  |
| 10+ agents        | t3.large                  | $60-70                  |

## Management Commands

### SSH Access
```bash
ssh -i nanda-multi-agent-key.pem ubuntu@<PUBLIC_IP>
```

### Monitor All Agents
```bash
ssh -i nanda-multi-agent-key.pem ubuntu@<PUBLIC_IP> 'sudo supervisorctl status'
```

### Restart Specific Agent
```bash
ssh -i nanda-multi-agent-key.pem ubuntu@<PUBLIC_IP> 'sudo supervisorctl restart nanda_agent_data_scientist_001'
```

### View Agent Logs
```bash
ssh -i nanda-multi-agent-key.pem ubuntu@<PUBLIC_IP> 'cd nanda-multi-agents && ls -la *.log'
ssh -i nanda-multi-agent-key.pem ubuntu@<PUBLIC_IP> 'tail -f nanda-multi-agents/agent_data_scientist_001_output.log'
```

### Stop All Agents
```bash
ssh -i nanda-multi-agent-key.pem ubuntu@<PUBLIC_IP> 'sudo supervisorctl stop all'
```

### Start All Agents
```bash
ssh -i nanda-multi-agent-key.pem ubuntu@<PUBLIC_IP> 'sudo supervisorctl start all'
```

## Testing Your Agents

### Test Individual Agent
```bash
curl -X POST http://<PUBLIC_IP>:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{
    "content": {
      "text": "Hello, can you help me with data analysis?",
      "type": "text"
    },
    "role": "user",
    "conversation_id": "test123"
  }'
```

### Test All Agents Script
```bash
#!/bin/bash
PUBLIC_IP="your-instance-ip"
PORTS=(6000 6001 6002 6003 6004)

for PORT in "${PORTS[@]}"; do
  echo "Testing agent on port $PORT..."
  curl -X POST http://$PUBLIC_IP:$PORT/a2a \
    -H "Content-Type: application/json" \
    -d '{
      "content": {"text": "hello", "type": "text"},
      "role": "user",
      "conversation_id": "test'$PORT'"
    }'
  echo ""
done
```

## Troubleshooting

### Agent Not Responding
1. Check if agent process is running: `sudo supervisorctl status`
2. Check agent logs: `tail -f nanda-multi-agents/agent_*_output.log`
3. Restart specific agent: `sudo supervisorctl restart nanda_agent_<agent_name>`

### Port Issues
- Ensure each agent has a unique port
- Verify security group has the ports open
- Check if ports are being used: `netstat -tlnp | grep :<port>`

### Memory Issues
- Monitor memory usage: `htop` or `free -h`
- Consider upgrading instance type if agents are being killed
- Reduce number of concurrent agents

### API Key Issues
- Verify Anthropic API key is valid
- Check agent logs for API-related errors
- Ensure API key has sufficient credits

## Cost Optimization

1. **Use Spot Instances**: Add `--instance-market-options '{"MarketType":"spot"}'` to reduce costs by up to 70%
2. **Schedule Shutdown**: Use cron jobs to stop instances during off-hours
3. **Right-size Instance**: Start with t3.small and scale up only if needed
4. **Monitor Usage**: Use CloudWatch to track CPU and memory usage

## Security Considerations

- The script opens ports for all agents - consider restricting IP ranges if needed
- Use IAM roles instead of access keys when possible
- Regularly rotate API keys
- Monitor agent logs for suspicious activity
- Consider using a VPN or private subnets for production deployments

## Cleanup

To terminate the deployment:
```bash
aws ec2 terminate-instances --region <REGION> --instance-ids <INSTANCE_ID>
```

The script output provides the exact termination command for your deployment.

