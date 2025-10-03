# 🚀 End-to-End Testing Guide for NANDA System

## ✅ **Local Testing Status: PASSED (5/5)**
- 🧩 Modular Embedding System: ✅ CLIP active, fallbacks working
- 📊 MongoDB Agent Facts: ✅ 390 agents, modular embeddings integrated  
- 📈 Telemetry System: ✅ Structured logging to MongoDB working
- 🔍 Agent Discovery: ✅ Semantic search with ranking working
- 🔄 Complete Integration: ✅ End-to-end flow operational

---

## 🎯 **End-to-End Testing Steps**

### **Phase 1: Pre-Deployment Setup**

#### 1.1 **Environment Variables Setup**
```bash
# Copy and configure environment variables
cd /Users/adityasharma/mit-nanda/nanda-workspace/NEST_Backup
cp env.example .env

# Edit .env file with your actual values:
vim .env
```

**Required variables:**
```ini
# MongoDB URIs (already configured)
MONGODB_TELEMETRY_URI=mongodb+srv://adityasharmasrt_db_user:V4036f6X0xO4qJ0W@nanda.wui3ygq.mongodb.net/
MONGODB_AGENTFACTS_URI=mongodb+srv://adityasharmasrt_db_user:V4036f6X0xO4qJ0W@nanda.wui3ygq.mongodb.net/

# Anthropic API Key for LLM functionality
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Registry URL
REGISTRY_URL=http://registry.chat39.com:6900
```

#### 1.2 **AWS Configuration Check**
```bash
# Verify AWS profile is set to nanda-manager
aws configure list --profile nanda-manager
export AWS_PROFILE=nanda-manager

# Verify credentials
aws sts get-caller-identity
```

#### 1.3 **Code Deployment Preparation**
```bash
# Commit and push latest changes
cd /Users/adityasharma/mit-nanda/nanda-workspace/NEST_Backup
git add .
git commit -m "Add modular embedding system and complete integration"
git push origin main
```

---

### **Phase 2: Single Agent Deployment**

#### 2.1 **Deploy Enhanced Agent with Modular Embeddings**
```bash
cd /Users/adityasharma/mit-nanda/nanda-workspace/NEST_Backup/scripts

# Deploy single agent with enhanced features
./aws-single-agent-deployment.sh
```

**Expected output:**
- ✅ EC2 instance created
- ✅ Enhanced agent script deployed
- ✅ Dependencies installed (transformers, pymongo, python-dotenv)
- ✅ Agent registered with registry
- ✅ Agent responding on port 6000

#### 2.2 **Verify Agent Deployment**
```bash
# Get the deployed agent IP (from deployment output)
AGENT_IP="<deployed_agent_ip>"

# Test basic agent response
curl -X POST http://$AGENT_IP:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"Hello, are you working?","type":"text"},"role":"user","conversation_id":"test-basic"}'
```

**Expected response:**
```json
{
  "content": {"text": "Hello! Yes, I'm working perfectly...", "type": "text"},
  "role": "assistant",
  "conversation_id": "test-basic"
}
```

---

### **Phase 3: Modular Embedding System Testing**

#### 3.1 **Test Embedding System Status**
```bash
# SSH into the deployed agent
ssh -i ~/.ssh/nanda-agent-key-a1b2.pem ubuntu@$AGENT_IP

# Check embedding system status
cd nanda-workspace/NEST_Backup
python3 -c "
from nanda_core.embeddings.embedding_manager import get_embedding_manager
manager = get_embedding_manager('embedding_config.json')
print('Active embedder:', manager.get_active_embedder_info())
print('All embedders:', manager.get_all_embedders_status())
"
```

**Expected output:**
- ✅ CLIP embedder active
- ✅ Simulated embedder as fallback
- ❌ Voyage AI disabled (expected)

#### 3.2 **Test Embedding Creation**
```bash
# Test embedding creation on deployed agent
python3 -c "
from nanda_core.embeddings.embedding_manager import create_embedding
embedding = create_embedding('Python web developer expert')
print(f'Embedding created: {len(embedding)} dimensions')
print(f'First 5 values: {embedding[:5]}')
"
```

**Expected output:**
- ✅ 512-dimensional embedding created
- ✅ Real CLIP values (not simulated hash)

---

### **Phase 4: Semantic Search Testing**

#### 4.1 **Test Agent Discovery via API**
```bash
# Test semantic search through agent API
curl -X POST http://$AGENT_IP:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"? python web development expert","type":"text"},"role":"user","conversation_id":"test-search-1"}'
```

**Expected response:**
```json
{
  "content": {
    "text": "🔍 Found X agents for 'python web development expert':\n  1. Python Developer 1 (desc-001) - Score: 0.XXX\n  2. Python Developer 2 (desc-011) - Score: 0.XXX\n  ...",
    "type": "text"
  },
  "role": "assistant",
  "conversation_id": "test-search-1"
}
```

#### 4.2 **Test Different Search Queries**
```bash
# Test various capability searches
QUERIES=(
  "? machine learning data scientist"
  "? cloud infrastructure kubernetes expert" 
  "? frontend react javascript developer"
  "? cybersecurity penetration testing"
  "? mobile app development flutter"
)

for query in "${QUERIES[@]}"; do
  echo "Testing: $query"
  curl -X POST http://$AGENT_IP:6000/a2a \
    -H "Content-Type: application/json" \
    -d "{\"content\":{\"text\":\"$query\",\"type\":\"text\"},\"role\":\"user\",\"conversation_id\":\"test-search-$(date +%s)\"}" \
    | jq -r '.content.text'
  echo "---"
done
```

**Expected results:**
- ✅ Each query returns relevant agents
- ✅ Agents ranked by relevance score
- ✅ Different specializations found correctly
- ✅ Response time < 1 second per query

---

### **Phase 5: Telemetry System Verification**

#### 5.1 **Check Telemetry Data Collection**
```bash
# SSH into agent and check telemetry
ssh -i ~/.ssh/nanda-agent-key-a1b2.pem ubuntu@$AGENT_IP
cd nanda-workspace/NEST_Backup

# Check telemetry collection
python3 -c "
from nanda_core.telemetry.mongodb_telemetry import MongoDBTelemetryStorage
telemetry = MongoDBTelemetryStorage()

# Get recent queries
recent = telemetry.get_recent_queries(limit=5)
print(f'Recent queries: {len(recent)}')
for query in recent:
    print(f'  - {query[\"query_text\"]} ({query[\"search_method\"]}) - {query[\"agents_found\"]} agents')

# Get analytics
analytics = telemetry.get_query_analytics(hours=1)
print(f'Analytics: {analytics}')
"
```

**Expected output:**
- ✅ Search queries logged to MongoDB
- ✅ Structured telemetry data captured
- ✅ Analytics showing search performance
- ✅ Agent discovery metrics recorded

#### 5.2 **Verify Telemetry Structure**
```bash
# Check telemetry data structure
python3 -c "
from nanda_core.telemetry.mongodb_telemetry import MongoDBTelemetryStorage
telemetry = MongoDBTelemetryStorage()

# Get sample telemetry record
sample = telemetry.collection.find_one({}, {'_id': 0})
if sample:
    import json
    print('Sample telemetry record:')
    print(json.dumps(sample, indent=2, default=str))
else:
    print('No telemetry records found')
"
```

**Expected fields:**
- ✅ query_id, timestamp, agent_id
- ✅ query_text, query_type, conversation_id
- ✅ search_time, agents_found, search_method
- ✅ top_agents, result_quality_score
- ✅ memory_usage_mb, cpu_usage_percent
- ✅ response_time, success

---

### **Phase 6: A2A Communication Testing**

#### 6.1 **Deploy Second Agent for A2A Testing**
```bash
# Deploy a second agent
cd /Users/adityasharma/mit-nanda/nanda-workspace/NEST_Backup/scripts
./aws-single-agent-deployment.sh
```

#### 6.2 **Test A2A Communication**
```bash
# Get both agent IPs
AGENT1_IP="<first_agent_ip>"
AGENT2_IP="<second_agent_ip>"

# Test A2A communication from Agent 1 to Agent 2
curl -X POST http://$AGENT1_IP:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"@<agent2_id> Hello, can you help me with Python development?","type":"text"},"role":"user","conversation_id":"test-a2a"}'
```

**Expected flow:**
1. ✅ Agent 1 receives message
2. ✅ Agent 1 parses @agent2_id mention
3. ✅ Agent 1 looks up Agent 2 in registry
4. ✅ Agent 1 forwards message to Agent 2
5. ✅ Agent 2 processes with LLM
6. ✅ Agent 2 responds back to Agent 1
7. ✅ Agent 1 returns Agent 2's response

---

### **Phase 7: Performance and Load Testing**

#### 7.1 **Search Performance Testing**
```bash
# Create performance test script
cat > test_search_performance.sh << 'EOF'
#!/bin/bash
AGENT_IP="$1"
QUERIES=(
  "? python expert"
  "? data scientist" 
  "? devops engineer"
  "? frontend developer"
  "? security expert"
)

echo "Testing search performance..."
for i in {1..10}; do
  for query in "${QUERIES[@]}"; do
    start_time=$(date +%s.%N)
    curl -s -X POST http://$AGENT_IP:6000/a2a \
      -H "Content-Type: application/json" \
      -d "{\"content\":{\"text\":\"$query\",\"type\":\"text\"},\"role\":\"user\",\"conversation_id\":\"perf-test-$i\"}" > /dev/null
    end_time=$(date +%s.%N)
    duration=$(echo "$end_time - $start_time" | bc)
    echo "Query '$query' took ${duration}s"
  done
done
EOF

chmod +x test_search_performance.sh
./test_search_performance.sh $AGENT_IP
```

**Expected performance:**
- ✅ Search queries < 1 second average
- ✅ Embedding creation < 0.1 second
- ✅ MongoDB queries < 0.5 second
- ✅ No memory leaks or crashes

#### 7.2 **Concurrent Request Testing**
```bash
# Test concurrent requests
for i in {1..5}; do
  curl -X POST http://$AGENT_IP:6000/a2a \
    -H "Content-Type: application/json" \
    -d '{"content":{"text":"? python developer","type":"text"},"role":"user","conversation_id":"concurrent-'$i'"}' &
done
wait
```

**Expected results:**
- ✅ All requests complete successfully
- ✅ No race conditions or errors
- ✅ Telemetry captures all requests

---

### **Phase 8: Integration Validation**

#### 8.1 **End-to-End Workflow Test**
```bash
# Complete workflow test
WORKFLOW_TEST='
{
  "content": {
    "text": "I need help with a Python web application. Can you find me experts and then connect me with the best one?",
    "type": "text"
  },
  "role": "user", 
  "conversation_id": "workflow-test"
}'

curl -X POST http://$AGENT_IP:6000/a2a \
  -H "Content-Type: application/json" \
  -d "$WORKFLOW_TEST"
```

**Expected workflow:**
1. ✅ Agent analyzes request
2. ✅ Agent performs semantic search
3. ✅ Agent finds relevant Python experts
4. ✅ Agent ranks by capability match
5. ✅ Agent logs telemetry data
6. ✅ Agent provides structured response

#### 8.2 **Modular System Validation**
```bash
# Test system modularity by disabling CLIP
ssh -i ~/.ssh/nanda-agent-key-a1b2.pem ubuntu@$AGENT_IP
cd nanda-workspace/NEST_Backup

# Disable CLIP embedder
python3 -c "
from nanda_core.embeddings.embedding_manager import get_embedding_manager
manager = get_embedding_manager('embedding_config.json')
manager.disable_embedder('clip')
print('CLIP disabled, testing fallback...')

# Test that system still works with simulated embedder
embedding = manager.create_embedding('test fallback')
print(f'Fallback working: {len(embedding)} dimensions')
"

# Test search still works
curl -X POST http://$AGENT_IP:6000/a2a \
  -H "Content-Type: application/json" \
  -d '{"content":{"text":"? python developer","type":"text"},"role":"user","conversation_id":"fallback-test"}'
```

**Expected results:**
- ✅ System automatically falls back to simulated embedder
- ✅ Search functionality continues working
- ✅ No crashes or errors
- ✅ Graceful degradation demonstrated

---

## 🎯 **Success Criteria**

### **✅ Must Pass:**
1. **Deployment**: Both agents deploy successfully
2. **Embeddings**: CLIP embeddings working, fallback functional
3. **Search**: Semantic search returns relevant results
4. **Telemetry**: All queries logged to MongoDB
5. **A2A**: Agent-to-agent communication working
6. **Performance**: Search < 1s, no memory leaks
7. **Modularity**: Can disable/enable components without breaking

### **⚠️ Nice to Have:**
1. **Voyage AI**: Real Voyage embeddings (requires API key)
2. **Advanced Analytics**: Complex telemetry queries
3. **Load Balancing**: Multiple agent instances

---

## 🚨 **Troubleshooting Guide**

### **Common Issues:**

#### **Agent Not Responding**
```bash
# Check agent logs
ssh -i ~/.ssh/nanda-agent-key-a1b2.pem ubuntu@$AGENT_IP
tail -f nanda-workspace/NEST_Backup/agent.log
```

#### **Embedding Errors**
```bash
# Check transformers installation
pip list | grep transformers
pip install transformers --upgrade
```

#### **MongoDB Connection Issues**
```bash
# Test MongoDB connection
python3 -c "
from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts
try:
    mongo = MongoDBAgentFacts()
    print('MongoDB connected successfully')
except Exception as e:
    print(f'MongoDB error: {e}')
"
```

#### **Search Returns No Results**
```bash
# Check agent collection
python3 -c "
from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts
mongo = MongoDBAgentFacts()
count = mongo.get_agent_count()
print(f'Total agents in DB: {count}')
"
```

---

## 🎉 **Expected Final State**

After successful end-to-end testing:

- ✅ **2 Enhanced agents** deployed and communicating
- ✅ **Modular embedding system** with CLIP active, fallbacks working
- ✅ **390 agents** in MongoDB with real embeddings
- ✅ **Semantic search** finding relevant agents in <1s
- ✅ **Telemetry system** capturing all interactions
- ✅ **A2A communication** working between agents
- ✅ **Graceful fallbacks** when components disabled
- ✅ **Production-ready** system with monitoring

**🚀 Ready for production deployment!**
