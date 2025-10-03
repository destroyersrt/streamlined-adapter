#!/usr/bin/env python3
"""
Embedding Manager for NANDA Agent Capabilities

Centralized, configurable management of different embedding methods.
Easy to enable/disable specific embedders or change preferences.
"""

import os
from typing import List, Dict, Any, Optional, Union
from .base_embedder import BaseEmbedder, EmbedderFactory

# Import all embedders to register them
from . import clip_embedder, voyage_embedder


class EmbeddingManager:
    """Manages multiple embedding methods with fallback and configuration"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file)
        self.active_embedder = None
        self.fallback_embedders = []
        self._initialize_embedders()
    
    def _load_config(self, config_file: Optional[str] = None) -> Dict[str, Any]:
        """Load embedding configuration"""
        default_config = {
            'preferred_order': ['clip', 'voyage', 'simulated'],
            'embedders': {
                'clip': {
                    'enabled': True,
                    'model_name': 'openai/clip-vit-base-patch32'
                },
                'voyage': {
                    'enabled': True,
                    'model_name': 'voyage-large-2'
                },
                'simulated': {
                    'enabled': True,
                    'dimension': 384
                }
            },
            'fallback_enabled': True,
            'auto_fallback': True
        }
        
        if config_file and os.path.exists(config_file):
            import json
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                # Merge configs (user config overrides defaults)
                for key, value in user_config.items():
                    if key == 'embedders' and isinstance(value, dict):
                        default_config['embedders'].update(value)
                    else:
                        default_config[key] = value
            except Exception as e:
                print(f"⚠️ Failed to load config file {config_file}: {e}")
        
        return default_config
    
    def _initialize_embedders(self):
        """Initialize embedders based on configuration"""
        preferred_order = self.config.get('preferred_order', ['clip', 'voyage', 'simulated'])
        
        for embedder_name in preferred_order:
            embedder_config = self.config.get('embedders', {}).get(embedder_name, {})
            
            # Skip if explicitly disabled
            if not embedder_config.get('enabled', True):
                print(f"⏭️ Skipping disabled embedder: {embedder_name}")
                continue
            
            embedder = EmbedderFactory.create_embedder(embedder_name, embedder_config)
            
            if embedder and embedder.is_enabled():
                if self.active_embedder is None:
                    self.active_embedder = embedder
                    print(f"🎯 Active embedder: {embedder_name}")
                else:
                    self.fallback_embedders.append(embedder)
                    print(f"🔄 Fallback embedder: {embedder_name}")
        
        if self.active_embedder is None:
            print("❌ No embedders available!")
        else:
            print(f"✅ Embedding manager initialized with {len(self.fallback_embedders)} fallbacks")
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """Create embedding with automatic fallback"""
        embedders_to_try = [self.active_embedder] + self.fallback_embedders
        
        for embedder in embedders_to_try:
            if embedder is None:
                continue
                
            try:
                return embedder.create_embedding(text)
            except Exception as e:
                print(f"⚠️ Embedder {embedder.__class__.__name__} failed: {e}")
                if not self.config.get('auto_fallback', True):
                    raise
                continue
        
        raise RuntimeError("All embedders failed")
    
    def create_batch_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Create batch embeddings with automatic fallback"""
        embedders_to_try = [self.active_embedder] + self.fallback_embedders
        
        for embedder in embedders_to_try:
            if embedder is None:
                continue
                
            try:
                return embedder.create_batch_embeddings(texts)
            except Exception as e:
                print(f"⚠️ Embedder {embedder.__class__.__name__} failed: {e}")
                if not self.config.get('auto_fallback', True):
                    raise
                continue
        
        raise RuntimeError("All embedders failed")
    
    def get_active_embedder_info(self) -> Dict[str, Any]:
        """Get information about the active embedder"""
        if self.active_embedder is None:
            return {'status': 'no_active_embedder'}
        
        return {
            'status': 'active',
            'name': self.active_embedder.__class__.__name__,
            'model': self.active_embedder.get_model_name(),
            'dimension': self.active_embedder.get_embedding_dimension(),
            'fallbacks_available': len(self.fallback_embedders)
        }
    
    def get_all_embedders_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all configured embedders"""
        return EmbedderFactory.list_embedders_status()
    
    def switch_embedder(self, embedder_name: str) -> bool:
        """Switch to a different embedder"""
        embedder_config = self.config.get('embedders', {}).get(embedder_name, {})
        new_embedder = EmbedderFactory.create_embedder(embedder_name, embedder_config)
        
        if new_embedder and new_embedder.is_enabled():
            # Move current active to fallbacks
            if self.active_embedder:
                self.fallback_embedders.insert(0, self.active_embedder)
            
            self.active_embedder = new_embedder
            print(f"🔄 Switched to embedder: {embedder_name}")
            return True
        else:
            print(f"❌ Cannot switch to embedder: {embedder_name}")
            return False
    
    def disable_embedder(self, embedder_name: str):
        """Disable a specific embedder"""
        if embedder_name in self.config.get('embedders', {}):
            self.config['embedders'][embedder_name]['enabled'] = False
            print(f"⏸️ Disabled embedder: {embedder_name}")
            
            # Reinitialize if this was the active embedder
            if (self.active_embedder and 
                self.active_embedder.__class__.__name__.lower().replace('embedder', '') == embedder_name):
                print("🔄 Reinitializing embedders due to active embedder disable")
                self._initialize_embedders()
    
    def enable_embedder(self, embedder_name: str):
        """Enable a specific embedder"""
        if embedder_name in self.config.get('embedders', {}):
            self.config['embedders'][embedder_name]['enabled'] = True
            print(f"▶️ Enabled embedder: {embedder_name}")


# Global embedding manager instance
_global_embedding_manager = None


def get_embedding_manager(config_file: Optional[str] = None) -> EmbeddingManager:
    """Get the global embedding manager instance"""
    global _global_embedding_manager
    
    if _global_embedding_manager is None:
        _global_embedding_manager = EmbeddingManager(config_file)
    
    return _global_embedding_manager


def create_embedding(text: str) -> Optional[List[float]]:
    """Convenience function to create a single embedding"""
    manager = get_embedding_manager()
    return manager.create_embedding(text)


def create_batch_embeddings(texts: List[str]) -> Optional[List[List[float]]]:
    """Convenience function to create batch embeddings"""
    manager = get_embedding_manager()
    return manager.create_batch_embeddings(texts)
