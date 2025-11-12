"""Configuration settings for models and system parameters."""

import os
from typing import Dict, Any

# Base URL for Ollama (Msty)
BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:10000")

# Model configurations
MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "phi3": {
        "model": "phi3:mini",
        "base_url": BASE_URL,
        "type": "llm",
        "capabilities": ["general", "reasoning", "fast"],
        "max_tokens": 2048,
        "temperature": 0.7,
    },
    "gemma3": {
        "model": "gemma3:latest",
        "base_url": BASE_URL,
        "type": "llm",
        "capabilities": ["general", "coding", "analysis"],
        "max_tokens": 4096,
        "temperature": 0.7,
    },
    "qwen3": {
        "model": "qwen3:latest",
        "base_url": BASE_URL,
        "type": "llm",
        "capabilities": ["general", "multilingual", "complex"],
        "max_tokens": 8192,
        "temperature": 0.7,
    },
}

# Embedding model configurations
EMBEDDING_CONFIGS: Dict[str, Dict[str, Any]] = {
    "gemma_embed": {
        "model": "embeddinggemma:latest",
        "base_url": BASE_URL,
        "type": "embedding",
    },
    "mxbai_embed": {
        "model": "mxbai-embed-large:latest",
        "base_url": BASE_URL,
        "type": "embedding",
    },
}

# Model selection criteria
MODEL_SELECTION_CRITERIA = {
    "simple": ["phi3"],
    "coding": ["gemma3", "qwen3"],
    "complex": ["qwen3", "gemma3"],
    "fast": ["phi3"],
    "multilingual": ["qwen3"],
}

# Default embedding model
DEFAULT_EMBEDDING = "mxbai_embed"

# LangSmith configuration (optional)
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "langchain_multi_model")

