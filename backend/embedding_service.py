"""
Embedding Service for Inventix AI - Phase 4

Generates text embeddings for semantic similarity computation.
Uses OpenAI-compatible API (Nebius).

Rules:
- Same model for all embeddings (consistency)
- Cache embeddings in database (recompute only on change)
- Deterministic, reproducible results
"""
import hashlib
import json
from typing import List, Optional
from openai import OpenAI
from pydantic import BaseModel
from config import get_settings

settings = get_settings()


class EmbeddingResult(BaseModel):
    """Result of embedding generation"""
    success: bool
    embedding: Optional[List[float]] = None
    text_hash: str
    model_name: str
    dimensions: int
    error: Optional[str] = None


def compute_text_hash(text: str) -> str:
    """
    Compute hash of text for cache invalidation.
    Same text → same hash (deterministic).
    """
    normalized = text.strip().lower()
    return hashlib.sha256(normalized.encode()).hexdigest()[:32]


def generate_embedding(text: str) -> EmbeddingResult:
    """
    Generate embedding for text using OpenAI-compatible API.
    
    Uses the same model for all embeddings to ensure consistency.
    Results are deterministic: same text → same embedding.
    """
    text_hash = compute_text_hash(text)
    
    if not settings.llm_api_key or settings.llm_api_key == "your-nebius-api-key-here":
        return EmbeddingResult(
            success=False,
            embedding=None,
            text_hash=text_hash,
            model_name=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            error="LLM API key not configured. Cannot generate embeddings."
        )
    
    try:
        # Use same API as LLM service
        client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url
        )
        
        # Truncate text to avoid token limits
        truncated_text = text[:8000]
        
        response = client.embeddings.create(
            model=settings.embedding_model,
            input=truncated_text
        )
        
        embedding = response.data[0].embedding
        
        return EmbeddingResult(
            success=True,
            embedding=embedding,
            text_hash=text_hash,
            model_name=settings.embedding_model,
            dimensions=len(embedding)
        )
        
    except Exception as e:
        return EmbeddingResult(
            success=False,
            embedding=None,
            text_hash=text_hash,
            model_name=settings.embedding_model,
            dimensions=settings.embedding_dimensions,
            error=f"Embedding generation failed: {str(e)}"
        )


def embedding_to_json(embedding: List[float]) -> str:
    """Serialize embedding to JSON for database storage."""
    return json.dumps(embedding)


def embedding_from_json(json_str: str) -> List[float]:
    """Deserialize embedding from JSON."""
    return json.loads(json_str)
