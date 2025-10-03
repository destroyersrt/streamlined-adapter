#!/usr/bin/env python3
"""
Base Embedder Interface for NANDA Agent Capabilities

Provides a modular interface for different embedding methods.
Easy to add new embedders or disable existing ones.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import time


class BaseEmbedder(ABC):
    """Abstract base class for all embedding implementations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.is_available = False
        self.error_message = None
        self._initialize()
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize the embedder. Set is_available=True if successful."""
        pass
    
    @abstractmethod
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text"""
        pass
    
    @abstractmethod
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by this embedder"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the name/identifier of the embedding model"""
        pass
    
    def create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts. Override for efficiency."""
        embeddings = []
        for text in texts:
            embedding = self.create_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def is_enabled(self) -> bool:
        """Check if this embedder is available and enabled"""
        return self.is_available and not self.config.get('disabled', False)
    
    def get_status(self) -> Dict[str, Any]:
        """Get status information about this embedder"""
        return {
            'name': self.__class__.__name__,
            'model': self.get_model_name(),
            'available': self.is_available,
            'enabled': self.is_enabled(),
            'dimension': self.get_embedding_dimension() if self.is_available else None,
            'error': self.error_message
        }


class SimulatedEmbedder(BaseEmbedder):
    """Simulated embedder for testing (fallback option)"""
    
    def _initialize(self) -> None:
        """Always available as fallback"""
        self.is_available = True
        self.dimension = self.config.get('dimension', 384)
    
    def create_embedding(self, text: str) -> List[float]:
        """Create simulated embedding using hash"""
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        # Convert to vector
        embedding = []
        for i in range(0, len(hash_hex), 2):
            val = int(hash_hex[i:i+2], 16) / 255.0
            embedding.append(val)
        
        # Pad to desired dimension
        while len(embedding) < self.dimension:
            embedding.extend(embedding[:min(self.dimension-len(embedding), len(embedding))])
        
        return embedding[:self.dimension]
    
    def get_embedding_dimension(self) -> int:
        return self.dimension
    
    def get_model_name(self) -> str:
        return "simulated-md5-embedder"


class EmbedderFactory:
    """Factory for creating and managing embedders"""
    
    _embedders = {}
    _default_embedder = None
    
    @classmethod
    def register_embedder(cls, name: str, embedder_class: type, config: Optional[Dict[str, Any]] = None):
        """Register an embedder class"""
        cls._embedders[name] = {
            'class': embedder_class,
            'config': config or {}
        }
    
    @classmethod
    def create_embedder(cls, name: str, config: Optional[Dict[str, Any]] = None) -> Optional[BaseEmbedder]:
        """Create an embedder instance"""
        if name not in cls._embedders:
            return None
        
        embedder_info = cls._embedders[name]
        merged_config = {**embedder_info['config'], **(config or {})}
        
        try:
            embedder = embedder_info['class'](merged_config)
            return embedder if embedder.is_enabled() else None
        except Exception as e:
            print(f"⚠️ Failed to create embedder '{name}': {e}")
            return None
    
    @classmethod
    def get_available_embedders(cls) -> List[str]:
        """Get list of available embedder names"""
        available = []
        for name in cls._embedders:
            embedder = cls.create_embedder(name)
            if embedder and embedder.is_enabled():
                available.append(name)
        return available
    
    @classmethod
    def get_best_embedder(cls, preferred_order: Optional[List[str]] = None) -> Optional[BaseEmbedder]:
        """Get the best available embedder"""
        if preferred_order is None:
            preferred_order = ['clip', 'voyage', 'simulated']
        
        for name in preferred_order:
            embedder = cls.create_embedder(name)
            if embedder and embedder.is_enabled():
                return embedder
        
        return None
    
    @classmethod
    def list_embedders_status(cls) -> Dict[str, Dict[str, Any]]:
        """Get status of all registered embedders"""
        status = {}
        for name in cls._embedders:
            embedder = cls.create_embedder(name)
            if embedder:
                status[name] = embedder.get_status()
            else:
                status[name] = {
                    'name': name,
                    'available': False,
                    'enabled': False,
                    'error': 'Failed to initialize'
                }
        return status


# Register the simulated embedder as fallback
EmbedderFactory.register_embedder('simulated', SimulatedEmbedder)
