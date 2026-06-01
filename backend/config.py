"""
Configuration module for the CodeAlpha FAQ Chatbot backend.

Provides centralized settings management, CUDA device detection,
and application constants. Optimized for NVIDIA RTX 4050 GPU.

Author: CodeAlpha Intern | Registration ID: Akshay Saxena
"""

import torch
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings with environment variable override support.

    All fields can be overridden via environment variables or a .env file.

    Attributes:
        app_name: The display name of the application.
        app_version: Semantic version string.
        registration_id: Institutional provenance identifier.
        database_url: SQLite database filename (relative to backend dir).
        cors_origins: Allowed CORS origin patterns.
        confidence_threshold: Minimum hybrid score for a confident match.
        semantic_weight: Weight for semantic similarity in fusion formula.
        lexical_weight: Weight for TF-IDF cosine similarity in fusion formula.
        spacy_model: SpaCy language model identifier.
        transformer_model: Sentence transformer model identifier.
        top_k_results: Number of fallback suggestions on low confidence.
        typeahead_min_chars: Minimum characters before typeahead triggers.

    Time Complexity: O(1) for instantiation
    Space Complexity: O(1)
    """

    app_name: str = "CodeAlpha FAQ Chatbot"
    app_version: str = "1.0.0"
    registration_id: str = "Akshay Saxena"
    database_url: str = "faq_chatbot.db"
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    # NLP Configuration
    confidence_threshold: float = 0.45
    semantic_weight: float = 0.7
    lexical_weight: float = 0.3
    spacy_model: str = "en_core_web_sm"
    transformer_model: str = "all-MiniLM-L6-v2"
    top_k_results: int = 3
    typeahead_min_chars: int = 3

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"


def get_device() -> torch.device:
    """Detect and return the optimal computation device.

    Explicitly checks for NVIDIA CUDA availability to leverage
    the RTX 4050 GPU for tensor operations. Falls back to CPU
    if CUDA is unavailable.

    Returns:
        torch.device: The CUDA device if available, otherwise CPU.

    Time Complexity: O(1)
    Space Complexity: O(1)
    """
    if torch.cuda.is_available():
        device = torch.device("cuda")
        gpu_name: str = torch.cuda.get_device_name(0)
        vram_gb: float = torch.cuda.get_device_properties(0).total_mem / 1e9
        print(f"[GPU] CUDA detected: {gpu_name}")
        print(f"[GPU] VRAM: {vram_gb:.1f} GB")
        return device
    else:
        print("[CPU] CUDA not available. Using CPU fallback.")
        return torch.device("cpu")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retrieve the cached application settings singleton.

    Uses functools.lru_cache to ensure a single Settings instance
    is created and reused across the application lifecycle.

    Returns:
        Settings: The application settings instance.

    Time Complexity: O(1) amortized (cached after first call)
    Space Complexity: O(1)
    """
    return Settings()
