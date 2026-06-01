"""
Sentence Transformer Embedding Engine with CUDA acceleration.

Loads the all-MiniLM-L6-v2 model onto GPU memory for hardware-
accelerated dense embedding generation. Optimized for NVIDIA RTX 4050
with O(1) amortized inference latency.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

import numpy as np
import torch
from sentence_transformers import SentenceTransformer
from typing import Optional

from backend.config import get_settings, get_device


# Module-level singleton state for the transformer model
_model: Optional[SentenceTransformer] = None
_device: Optional[torch.device] = None


def load_transformer_model() -> tuple[SentenceTransformer, torch.device]:
    """Load the Sentence Transformer model onto the optimal device.

    Explicitly routes the model to CUDA if an NVIDIA GPU is available,
    loading all parameters into GPU VRAM for zero-copy inference.
    Uses module-level caching to prevent redundant model loads.

    Returns:
        tuple[SentenceTransformer, torch.device]: The loaded model and device.

    Time Complexity: O(M) where M is the model parameter count (one-time load)
    Space Complexity: O(M) for model weights in GPU/CPU memory (~80MB for MiniLM)
    """
    global _model, _device

    if _model is not None and _device is not None:
        return _model, _device

    settings = get_settings()
    _device = get_device()

    _model = SentenceTransformer(
        settings.transformer_model,
        device=str(_device),
    )

    param_count: int = sum(p.numel() for p in _model.parameters())
    embed_dim: int = _model.get_sentence_embedding_dimension()
    print(f"[EMBED] Model '{settings.transformer_model}' loaded on {_device}")
    print(f"[EMBED] Parameters: {param_count:,} | Embedding dim: {embed_dim}")

    return _model, _device


def generate_embedding(text: str) -> np.ndarray:
    """Generate a dense L2-normalized embedding vector for a single text.

    Routes computation through CUDA for GPU-accelerated inference.
    The returned embedding is normalized, so cosine similarity
    reduces to a simple dot product.

    Args:
        text: Input text string to embed.

    Returns:
        np.ndarray: Dense embedding vector of shape (384,), L2-normalized.

    Time Complexity: O(L) where L is the input token length
    Space Complexity: O(D) where D is the embedding dimension (384)
    """
    model, device = load_transformer_model()
    embedding: np.ndarray = model.encode(
        text,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return embedding


def generate_embeddings_batch(
    texts: list[str],
    batch_size: int = 64,
) -> np.ndarray:
    """Generate dense embeddings for a batch of texts.

    Utilizes GPU parallelism via batched inference for efficiency.
    Each embedding is L2-normalized for downstream dot-product similarity.

    Args:
        texts: List of input texts to embed.
        batch_size: Number of texts to process per GPU batch.

    Returns:
        np.ndarray: Embedding matrix of shape (N, 384), L2-normalized rows.

    Time Complexity: O(N * L / B) where N=texts, L=avg token length, B=batch_size
    Space Complexity: O(N * D) where D is the embedding dimension (384)
    """
    if not texts:
        return np.array([])

    model, device = load_transformer_model()
    embeddings: np.ndarray = model.encode(
        texts,
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return embeddings


def compute_semantic_similarity(
    query_embedding: np.ndarray,
    faq_embeddings: np.ndarray,
) -> np.ndarray:
    """Compute cosine similarity between a query and all FAQ embeddings.

    Since all embeddings are L2-normalized during generation, cosine
    similarity is equivalent to a simple dot product, achieving
    optimal O(N*D) complexity without additional normalization.

    Args:
        query_embedding: Query vector of shape (D,), L2-normalized.
        faq_embeddings: FAQ matrix of shape (N, D), L2-normalized rows.

    Returns:
        np.ndarray: Similarity scores of shape (N,) in range [-1, 1].

    Time Complexity: O(N * D) where N=number of FAQs, D=embedding dim (384)
    Space Complexity: O(N) for the output scores array
    """
    if faq_embeddings.size == 0:
        return np.array([])

    scores: np.ndarray = np.dot(faq_embeddings, query_embedding)
    return scores
