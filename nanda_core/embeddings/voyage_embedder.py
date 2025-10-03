#!/usr/bin/env python3
"""
Voyage AI Embedder Implementation

Modular Voyage AI embeddings that can be easily enabled/disabled.
Falls back gracefully if voyageai package or API key are not available.
"""

import os
from typing import List, Dict, Any, Optional
from .base_embedder import BaseEmbedder


class VoyageEmbedder(BaseEmbedder):
    """Voyage AI-based embedder"""
    
    def _initialize(self) -> None:
        """Initialize Voyage AI client"""
        try:
            # Check if voyageai package is available
            import voyageai
            
            # Check for API key
            api_key = self.config.get('api_key') or os.getenv('VOYAGE_API_KEY')
            if not api_key:
                self.error_message = "Voyage AI API key not found"
                self.is_available = False
                print(f"⚠️ Voyage embedder unavailable: {self.error_message}")
                return
            
            # Initialize client
            self.client = voyageai.Client(api_key=api_key)
            self.model_name = self.config.get('model_name', 'voyage-large-2')
            
            # Test the connection with a simple embedding
            test_result = self.client.embed(["test"], model=self.model_name)
            self.dimension = len(test_result.embeddings[0])
            
            self.is_available = True
            print(f"✅ Voyage embedder initialized: {self.model_name}")
            
        except ImportError:
            self.error_message = "voyageai package not installed"
            self.is_available = False
            print(f"⚠️ Voyage embedder unavailable: {self.error_message}")
            
        except Exception as e:
            self.error_message = f"Initialization failed: {e}"
            self.is_available = False
            print(f"❌ Voyage embedder failed: {self.error_message}")
    
    def create_embedding(self, text: str) -> List[float]:
        """Create Voyage AI embedding for text"""
        if not self.is_available:
            raise RuntimeError(f"Voyage embedder not available: {self.error_message}")
        
        result = self.client.embed([text], model=self.model_name)
        return result.embeddings[0]
    
    def create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create Voyage AI embeddings for multiple texts efficiently"""
        if not self.is_available:
            raise RuntimeError(f"Voyage embedder not available: {self.error_message}")
        
        # Voyage AI supports batch processing natively
        result = self.client.embed(texts, model=self.model_name)
        return result.embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get Voyage AI embedding dimension"""
        return getattr(self, 'dimension', 1024)  # voyage-large-2 is 1024-dimensional
    
    def get_model_name(self) -> str:
        """Get the Voyage AI model name"""
        return getattr(self, 'model_name', 'voyage-large-2')


# Register Voyage embedder
from .base_embedder import EmbedderFactory
EmbedderFactory.register_embedder('voyage', VoyageEmbedder)
