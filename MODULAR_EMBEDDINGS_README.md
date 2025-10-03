# 🧩 Modular Embedding System for NANDA

## 🎯 **Design Philosophy: Easy to Remove/Disable**

This modular embedding system follows your requirement for **easy modularity** - everything can be enabled, disabled, or completely removed without breaking the system.

## 📁 **File Structure**

```
nanda_core/embeddings/
├── __init__.py                 # Module initialization
├── base_embedder.py           # Abstract base class & factory
├── clip_embedder.py           # CLIP embeddings (Hugging Face)
├── voyage_embedder.py         # Voyage AI embeddings
└── embedding_manager.py       # Central management & fallbacks

embedding_config.json          # Configuration file
```

## ⚙️ **Configuration-Driven**

### Enable/Disable via JSON Config:
```json
{
  "preferred_order": ["clip", "voyage", "simulated"],
  "embedders": {
    "clip": {
      "enabled": true,
      "model_name": "openai/clip-vit-base-patch32"
    },
    "voyage": {
      "enabled": false,
      "comment": "Disabled until API key configured"
    },
    "simulated": {
      "enabled": true,
      "dimension": 384
    }
  },
  "auto_fallback": true
}
```

### Enable/Disable via Code:
```python
manager = get_embedding_manager()
manager.disable_embedder('clip')    # Disable CLIP
manager.enable_embedder('voyage')   # Enable Voyage AI
manager.switch_embedder('simulated') # Switch to simulated
```

## 🔧 **Easy Removal Guide**

### 1. **Disable an Embedder** (Soft removal)
```bash
# Option A: Edit config file
vim embedding_config.json
# Set "enabled": false

# Option B: Programmatically
python -c "
from nanda_core.embeddings.embedding_manager import get_embedding_manager
get_embedding_manager().disable_embedder('clip')
"
```

### 2. **Remove an Embedder** (Hard removal)
```bash
# Remove CLIP embedder completely:
rm nanda_core/embeddings/clip_embedder.py

# Remove import from embedding_manager.py:
sed -i '' '/from . import clip_embedder/d' nanda_core/embeddings/embedding_manager.py

# System automatically falls back to next available embedder
```

### 3. **Add New Embedder**
```python
# 1. Create new_embedder.py
class NewEmbedder(BaseEmbedder):
    def _initialize(self): pass
    def create_embedding(self, text): pass
    def get_embedding_dimension(self): pass
    def get_model_name(self): pass

# 2. Register it
EmbedderFactory.register_embedder('new', NewEmbedder)

# 3. Add to config
# "new": {"enabled": true}
```

## 🛡️ **Graceful Fallbacks**

The system automatically handles failures:

1. **Missing Dependencies**: If `transformers` not installed, CLIP is disabled
2. **API Key Missing**: If Voyage AI key missing, falls back to CLIP
3. **Runtime Errors**: If embedder fails, tries next in preference order
4. **Always Available**: Simulated embedder as final fallback

## 📊 **Current Status**

### ✅ **Working Embedders:**
- **CLIP**: ✅ Active (512 dimensions)
- **Simulated**: ✅ Fallback (384 dimensions)

### ❌ **Disabled/Unavailable:**
- **Voyage AI**: ❌ Package not installed

### 🔄 **Integration Status:**
- ✅ MongoDB agent facts updated with modular embeddings
- ✅ 100 embedding agents updated with CLIP embeddings
- ✅ Automatic fallback tested and working
- ✅ Configuration-driven enable/disable tested

## 🚀 **Usage Examples**

### Basic Usage:
```python
from nanda_core.embeddings.embedding_manager import create_embedding

# Simple embedding creation (uses best available embedder)
embedding = create_embedding("Python developer expert")
```

### Advanced Usage:
```python
from nanda_core.embeddings.embedding_manager import get_embedding_manager

manager = get_embedding_manager('embedding_config.json')

# Check status
status = manager.get_active_embedder_info()
print(f"Using: {status['name']} ({status['model']})")

# Batch processing
embeddings = manager.create_batch_embeddings([
    "Python developer",
    "Data scientist", 
    "DevOps engineer"
])

# Switch embedders
manager.switch_embedder('simulated')
```

### MongoDB Integration:
```python
from nanda_core.core.mongodb_agent_facts import MongoDBAgentFacts

mongo_facts = MongoDBAgentFacts()
# Automatically uses modular embedding system
updated = mongo_facts.update_agents_with_modular_embeddings()
```

## 🎯 **Key Benefits**

1. **🔧 Easy Removal**: Any component can be disabled/removed without breaking the system
2. **🔄 Automatic Fallbacks**: System continues working even if preferred embedders fail
3. **⚙️ Configuration-Driven**: No code changes needed to enable/disable features
4. **🧩 Modular Design**: Each embedder is independent and self-contained
5. **🛡️ Graceful Degradation**: Missing dependencies don't crash the system
6. **📈 Easy Extension**: Adding new embedders requires minimal code changes

## 🔍 **Testing**

Run the test suite:
```bash
python test_modular_embeddings.py
```

This demonstrates:
- ✅ Embedder status checking
- ✅ Embedding creation (single & batch)
- ✅ Embedder switching
- ✅ Enable/disable functionality
- ✅ Fallback behavior
- ✅ Easy removal procedures

---

**🎉 The system is now fully modular and follows your requirement for easy removal/disable functionality!**
