# 🚀 NANDA Agent Deployment Scripts

Production-ready scripts for deploying NANDA agents to AWS EC2.

## 📋 Available Scripts

### 🤖 Single Agent Deployment
**`aws-single-agent-deployment.sh`** - Deploy one specialized agent to one EC2 instance

```bash
bash aws-single-agent-deployment.sh <AGENT_ID> <API_KEY> <NAME> <DOMAIN> <SPECIALIZATION> <DESCRIPTION> <CAPABILITIES> [REGISTRY_URL] [PORT] [REGION] [INSTANCE_TYPE]
```

**Example:**
```bash
bash aws-single-agent-deployment.sh \
  "data-scientist" \
  "sk-ant-api03-..." \
  "Data Scientist" \
  "data analysis" \
  "expert data analyst and machine learning specialist" \
  "I help with statistical analysis, machine learning, and data visualization" \
  "python,statistics,machine learning,data visualization" \
  "http://registry.chat39.com:6900" \
  "6000" \
  "us-east-1" \
  "t3.micro"
```

### 🏭 Multi-Agent Deployment  
**`aws-multi-agent-deployment.sh`** - Deploy 10 agents to one EC2 instance

```bash
bash aws-multi-agent-deployment.sh <API_KEY> <CONFIG_JSON> [REGISTRY_URL] [REGION] [INSTANCE_TYPE]
```

**Example:**
```bash
bash aws-multi-agent-deployment.sh \
  "sk-ant-api03-..." \
  "agent_configs/group-01-business-and-finance-experts.json" \
  "http://registry.chat39.com:6900" \
  "us-east-1" \
  "t3.xlarge"
```

### 🖥️ Existing Server Deployment
**`deploy-agent.sh`** - Deploy agent to existing Ubuntu/Amazon Linux server

```bash
bash deploy-agent.sh <AGENT_TYPE> <AGENT_ID> <API_KEY> [PORT] [REGISTRY_URL]
```

## 📦 Pre-configured Agent Groups

Ready-to-deploy agent configurations:

| File | Agents | Description |
|------|--------|-------------|
| `agent_configs/group-01-business-and-finance-experts.json` | 10 | Financial analysts, advisors, strategists |
| `agent_configs/group-02-technology-and-engineering.json` | 10 | Software engineers, DevOps, AI researchers |
| `agent_configs/group-03-creative-and-design.json` | 10 | Designers, content creators, brand experts |
| `agent_configs/group-04-healthcare-and-life-sciences.json` | 10 | Medical researchers, health informatics |
| `agent_configs/group-05-education-and-research.json` | 10 | Academic researchers, educators |
| `agent_configs/group-06-media-and-entertainment.json` | 10 | Journalists, producers, social media |
| `agent_configs/group-07-environmental-and-sustainability.json` | 10 | Climate scientists, sustainability experts |
| `agent_configs/group-08-social-services-and-community.json` | 10 | Social workers, policy analysts |
| `agent_configs/group-09-sports-and-recreation.json` | 10 | Fitness trainers, sports analysts |
| `agent_configs/group-10-travel-and-hospitality.json` | 10 | Travel planners, hospitality managers |
| `agent_configs/100-agents-config.json` | 100 | All agent personalities combined |

## 🛠️ Prerequisites

- **AWS CLI** configured with credentials (`aws configure`)
- **Anthropic API Key** for Claude LLM
- **SSH Key Pair** for EC2 access (automatically created)

## 🎯 Recommended Instance Types

| Deployment | Instance Type | Cost | Use Case |
|------------|---------------|------|----------|
| Single Agent | `t3.micro` | $8/month | Development, testing |
| Multi-Agent (10) | `t3.xlarge` | $150/month | Production, high traffic |
| High Performance | `t3.2xlarge` | $300/month | Enterprise, 20+ agents |

## 🔧 What the Scripts Do

1. **🔐 AWS Setup**: Create security groups, key pairs, open ports
2. **🖥️ EC2 Launch**: Launch Ubuntu 22.04 instance with user-data script
3. **📦 Dependencies**: Install Python, git, anthropic library
4. **📂 Project Setup**: Clone repo, create virtual environment
5. **🤖 Agent Start**: Configure and start agent(s) with supervisor
6. **📋 Registry**: Register agent(s) with NANDA registry
7. **✅ Health Check**: Verify agent(s) are responding

## 🧪 Testing Deployed Agents

### Test Single Agent
```bash
curl -X POST http://AGENT_IP:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"Hello! What are your capabilities?","type":"text"},"role":"user","conversation_id":"test123"}'
```

### Test A2A Communication
```bash
curl -X POST http://AGENT_A_IP:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"@agent-b-id Can you help with this task?","type":"text"},"role":"user","conversation_id":"test123"}'
```

## 🛑 Cleanup

To terminate instances:
```bash
# Single agent
aws ec2 terminate-instances --region us-east-1 --instance-ids i-xxxxx

# Multiple instances
aws ec2 describe-instances --filters "Name=tag:Project,Values=NANDA*" --query 'Reservations[*].Instances[*].InstanceId' --output text | xargs aws ec2 terminate-instances --region us-east-1 --instance-ids
```

## 🚨 Troubleshooting

### Common Issues

**Agent not responding:**
- Check security group has port open
- Verify agent process is running: `ps aux | grep python`
- Check logs: `tail -f agent.log`

**SSH connection failed:**
- Ensure using correct `.pem` key file
- Check key permissions: `chmod 400 *.pem`
- Verify instance is running: `aws ec2 describe-instances`

**Registration failed:**
- Verify registry URL is accessible
- Check public IP retrieval in user-data logs
- Ensure ANTHROPIC_API_KEY is valid

### Debug Commands

```bash
# SSH into instance
ssh -i nanda-agent-key.pem ubuntu@INSTANCE_IP

# Check user-data logs
sudo tail -f /var/log/cloud-init-output.log

# Check agent logs
cd nanda-agent-* && tail -f agent.log

# Check running processes
ps aux | grep python
```

## 📈 Scaling

### Deploy 100 Agents (10 instances)
```bash
for i in {1..10}; do
  bash aws-multi-agent-deployment.sh \
    "sk-ant-api03-..." \
    "group-0${i}-*.json" \
    "http://registry.chat39.com:6900" \
    "us-east-1" \
    "t3.xlarge" &
done
```

### Cross-Region Deployment
```bash
# Deploy to multiple regions
for region in us-east-1 us-west-2 eu-west-1; do
  bash aws-multi-agent-deployment.sh \
    "sk-ant-api03-..." \
    "group-01-business-and-finance-experts.json" \
    "http://registry.chat39.com:6900" \
    "$region" \
    "t3.xlarge" &
done
```

---

**🎯 Ready to deploy? Start with a single agent to test, then scale to multi-agent deployments!**