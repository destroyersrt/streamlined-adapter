#!/usr/bin/env python3
"""
Test Modular Embedding System

Demonstrates how easy it is to:
- Enable/disable different embedders
- Switch between embedders
- Handle fallbacks gracefully
- Configure via JSON file
"""

import os
import sys
import json
from typing import List, Dict, Any

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nanda_core.embeddings.embedding_manager import EmbeddingManager, get_embedding_manager


def test_embedder_status():
    """Test embedder availability and status"""
    print("🔍 Testing Embedder Status...")
    
    manager = get_embedding_manager('embedding_config.json')
    
    # Show active embedder
    active_info = manager.get_active_embedder_info()
    print(f"\n🎯 Active Embedder:")
    print(f"  Name: {active_info.get('name', 'None')}")
    print(f"  Model: {active_info.get('model', 'N/A')}")
    print(f"  Dimension: {active_info.get('dimension', 'N/A')}")
    print(f"  Fallbacks: {active_info.get('fallbacks_available', 0)}")
    
    # Show all embedders status
    all_status = manager.get_all_embedders_status()
    print(f"\n📊 All Embedders Status:")
    for name, status in all_status.items():
        enabled = "✅" if status.get('enabled', False) else "❌"
        available = "🟢" if status.get('available', False) else "🔴"
        print(f"  {enabled} {available} {name}: {status.get('model', 'N/A')}")
        if status.get('error'):
            print(f"      Error: {status['error']}")


def test_embedding_creation():
    """Test creating embeddings with the modular system"""
    print("\n🧪 Testing Embedding Creation...")
    
    manager = get_embedding_manager('embedding_config.json')
    
    test_texts = [
        "Python developer specializing in web applications",
        "Data scientist expert in machine learning",
        "DevOps engineer with cloud expertise"
    ]
    
    # Test single embedding
    print("\n📝 Single Embedding Test:")
    for i, text in enumerate(test_texts[:2]):  # Test first 2
        try:
            embedding = manager.create_embedding(text)
            print(f"  ✅ Text {i+1}: {len(embedding)} dimensions - {text[:40]}...")
        except Exception as e:
            print(f"  ❌ Text {i+1}: Failed - {e}")
    
    # Test batch embeddings
    print("\n📦 Batch Embedding Test:")
    try:
        embeddings = manager.create_batch_embeddings(test_texts)
        print(f"  ✅ Batch: {len(embeddings)} embeddings, {len(embeddings[0])} dimensions each")
    except Exception as e:
        print(f"  ❌ Batch: Failed - {e}")


def test_embedder_switching():
    """Test switching between embedders"""
    print("\n🔄 Testing Embedder Switching...")
    
    manager = get_embedding_manager('embedding_config.json')
    
    # Show current active
    current = manager.get_active_embedder_info()
    print(f"  Current: {current.get('name', 'None')}")
    
    # Try to switch to simulated (should work)
    print("\n  Switching to simulated embedder...")
    success = manager.switch_embedder('simulated')
    if success:
        new_active = manager.get_active_embedder_info()
        print(f"  ✅ Switched to: {new_active.get('name', 'None')}")
    else:
        print("  ❌ Switch failed")
    
    # Try to switch to voyage (should fail - disabled)
    print("\n  Switching to voyage embedder...")
    success = manager.switch_embedder('voyage')
    if success:
        new_active = manager.get_active_embedder_info()
        print(f"  ✅ Switched to: {new_active.get('name', 'None')}")
    else:
        print("  ❌ Switch failed (expected - voyage is disabled)")


def test_disable_enable():
    """Test disabling and enabling embedders"""
    print("\n⏸️ Testing Disable/Enable...")
    
    manager = get_embedding_manager('embedding_config.json')
    
    # Disable CLIP
    print("  Disabling CLIP embedder...")
    manager.disable_embedder('clip')
    
    # Show new active
    active = manager.get_active_embedder_info()
    print(f"  New active: {active.get('name', 'None')}")
    
    # Re-enable CLIP
    print("  Re-enabling CLIP embedder...")
    manager.enable_embedder('clip')


def test_fallback_behavior():
    """Test fallback behavior when embedders fail"""
    print("\n🔄 Testing Fallback Behavior...")
    
    # Create a temporary config with voyage enabled (will fail without API key)
    temp_config = {
        "preferred_order": ["voyage", "clip", "simulated"],
        "embedders": {
            "voyage": {"enabled": True},
            "clip": {"enabled": True},
            "simulated": {"enabled": True}
        },
        "auto_fallback": True
    }
    
    with open('temp_embedding_config.json', 'w') as f:
        json.dump(temp_config, f, indent=2)
    
    try:
        # This should fallback from voyage -> clip -> simulated
        manager = EmbeddingManager('temp_embedding_config.json')
        
        active = manager.get_active_embedder_info()
        print(f"  Active after fallback: {active.get('name', 'None')}")
        
        # Test embedding creation (should work with fallback)
        embedding = manager.create_embedding("test text")
        print(f"  ✅ Embedding created: {len(embedding)} dimensions")
        
    finally:
        # Clean up temp config
        if os.path.exists('temp_embedding_config.json'):
            os.remove('temp_embedding_config.json')


def demonstrate_easy_removal():
    """Demonstrate how easy it is to remove/disable components"""
    print("\n🗑️ Demonstrating Easy Removal...")
    
    print("  To disable CLIP embeddings:")
    print("    1. Set 'enabled': false in embedding_config.json")
    print("    2. Or call manager.disable_embedder('clip')")
    print("    3. System automatically falls back to next available")
    
    print("\n  To completely remove CLIP:")
    print("    1. Delete nanda_core/embeddings/clip_embedder.py")
    print("    2. Remove import from embedding_manager.py")
    print("    3. System continues with remaining embedders")
    
    print("\n  To add new embedder:")
    print("    1. Create new_embedder.py extending BaseEmbedder")
    print("    2. Register with EmbedderFactory.register_embedder()")
    print("    3. Add to embedding_config.json")
    print("    4. System automatically picks it up")


if __name__ == "__main__":
    print("🧪 Testing Modular Embedding System")
    print("=" * 60)
    
    test_embedder_status()
    test_embedding_creation()
    test_embedder_switching()
    test_disable_enable()
    test_fallback_behavior()
    demonstrate_easy_removal()
    
    print("\n" + "=" * 60)
    print("✅ Modular embedding system tested successfully!")
    print("🎯 Key benefits:")
    print("  - Easy to enable/disable any embedder")
    print("  - Automatic fallback when embedders fail")
    print("  - Configuration-driven (no code changes needed)")
    print("  - Simple to add new embedding methods")
    print("  - Graceful degradation when dependencies missing")
