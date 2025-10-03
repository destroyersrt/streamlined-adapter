#!/usr/bin/env python3
"""
CLIP Embedder Implementation

Modular CLIP embeddings that can be easily enabled/disabled.
Falls back gracefully if transformers/torch are not available.
"""

from typing import List, Dict, Any, Optional
from .base_embedder import BaseEmbedder


class CLIPEmbedder(BaseEmbedder):
    """CLIP-based embedder using Hugging Face transformers"""
    
    def _initialize(self) -> None:
        """Initialize CLIP model and tokenizer"""
        try:
            # Check if required packages are available
            import torch
            from transformers import CLIPTextModel, CLIPTokenizer
            
            self.model_name = self.config.get('model_name', 'openai/clip-vit-base-patch32')
            
            # Load model and tokenizer
            self.model = CLIPTextModel.from_pretrained(self.model_name)
            self.tokenizer = CLIPTokenizer.from_pretrained(self.model_name)
            
            # Set to evaluation mode
            self.model.eval()
            
            self.is_available = True
            print(f"✅ CLIP embedder initialized: {self.model_name}")
            
        except ImportError as e:
            self.error_message = f"Missing dependencies: {e}"
            self.is_available = False
            print(f"⚠️ CLIP embedder unavailable: {self.error_message}")
            
        except Exception as e:
            self.error_message = f"Initialization failed: {e}"
            self.is_available = False
            print(f"❌ CLIP embedder failed: {self.error_message}")
    
    def create_embedding(self, text: str) -> List[float]:
        """Create CLIP embedding for text"""
        if not self.is_available:
            raise RuntimeError(f"CLIP embedder not available: {self.error_message}")
        
        import torch
        
        # Tokenize the text
        inputs = self.tokenizer(
            text, 
            return_tensors='pt', 
            padding=True, 
            truncation=True, 
            max_length=77
        )
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use the pooled output (CLS token representation)
            embedding = outputs.pooler_output.squeeze().tolist()
        
        return embedding
    
    def create_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create CLIP embeddings for multiple texts efficiently"""
        if not self.is_available:
            raise RuntimeError(f"CLIP embedder not available: {self.error_message}")
        
        import torch
        
        # Tokenize all texts at once
        inputs = self.tokenizer(
            texts, 
            return_tensors='pt', 
            padding=True, 
            truncation=True, 
            max_length=77
        )
        
        # Get embeddings for all texts
        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use the pooled output for all texts
            embeddings = outputs.pooler_output.tolist()
        
        return embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get CLIP embedding dimension"""
        return 512  # CLIP text embeddings are 512-dimensional
    
    def get_model_name(self) -> str:
        """Get the CLIP model name"""
        return getattr(self, 'model_name', 'openai/clip-vit-base-patch32')


# Register CLIP embedder
from .base_embedder import EmbedderFactory
EmbedderFactory.register_embedder('clip', CLIPEmbedder)
