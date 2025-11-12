"""Configuration settings for models and system parameters."""

import os
from pathlib import Path
from typing import Dict, Any

# Load environment variables from .env files
try:
    from dotenv import load_dotenv
    # Get project root directory (parent of config directory)
    project_root = Path(__file__).parent.parent
    # Load .env.local first (higher priority), then .env
    env_local = project_root / ".env.local"
    env_file = project_root / ".env"
    if env_local.exists():
        load_dotenv(env_local, override=True)
        print(f"✅ Loaded environment variables from {env_local}")
    elif env_file.exists():
        load_dotenv(env_file, override=False)
        print(f"✅ Loaded environment variables from {env_file}")
except ImportError:
    # python-dotenv not installed, skip loading .env files
    print("ℹ️  python-dotenv not installed. Install with: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Warning: Could not load .env files: {e}")

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
# Strip quotes if present (dotenv should handle this, but just in case)
LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY", "").strip('"\'')
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "false").strip('"\'').lower() == "true"
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT", "langchain_multi_model").strip('"\'')

