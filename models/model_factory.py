"""Factory for creating and managing LLM and embedding models."""

from typing import Optional, Union
try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    CHATOLLAMA_AVAILABLE = True
except ImportError:
    CHATOLLAMA_AVAILABLE = False
    try:
        from langchain_ollama import OllamaLLM, OllamaEmbeddings
    except ImportError:
        raise ImportError(
            "langchain-ollama is required. Install it with: pip install langchain-ollama"
        )

from config.settings import MODEL_CONFIGS, EMBEDDING_CONFIGS, DEFAULT_EMBEDDING
from utils.errors import ModelSelectionError


class ModelFactory:
    """Factory class for creating LLM and embedding models."""
    
    _llm_cache: dict = {}
    _embedding_cache: dict = {}
    
    @classmethod
    def get_llm(cls, model_key: str) -> Union[ChatOllama, "OllamaLLM"]:
        """
        Get or create an LLM instance.
        
        Args:
            model_key: Key from MODEL_CONFIGS (e.g., 'phi3', 'gemma3', 'qwen3')
            
        Returns:
            ChatOllama or OllamaLLM instance
        """
        if model_key not in cls._llm_cache:
            if model_key not in MODEL_CONFIGS:
                raise ModelSelectionError(f"Unknown model key: {model_key}")
            
            config = MODEL_CONFIGS[model_key]
            if config["type"] != "llm":
                raise ModelSelectionError(f"Model {model_key} is not an LLM")
            
            try:
                if CHATOLLAMA_AVAILABLE:
                    cls._llm_cache[model_key] = ChatOllama(
                        model=config["model"],
                        base_url=config["base_url"],
                        temperature=config.get("temperature", 0.7),
                        num_ctx=config.get("max_tokens", 2048),
                    )
                else:
                    # Fallback to OllamaLLM for older versions
                    cls._llm_cache[model_key] = OllamaLLM(
                        model=config["model"],
                        base_url=config["base_url"],
                        temperature=config.get("temperature", 0.7),
                        num_ctx=config.get("max_tokens", 2048),
                    )
            except Exception as e:
                raise ModelSelectionError(
                    f"Failed to create model {model_key}: {str(e)}"
                ) from e
        
        return cls._llm_cache[model_key]
    
    @classmethod
    def get_embedding(cls, embedding_key: Optional[str] = None) -> OllamaEmbeddings:
        """
        Get or create an embedding model instance.
        
        Args:
            embedding_key: Key from EMBEDDING_CONFIGS (defaults to DEFAULT_EMBEDDING)
            
        Returns:
            OllamaEmbeddings instance
        """
        if embedding_key is None:
            embedding_key = DEFAULT_EMBEDDING
        
        if embedding_key not in cls._embedding_cache:
            if embedding_key not in EMBEDDING_CONFIGS:
                raise ModelSelectionError(f"Unknown embedding key: {embedding_key}")
            
            config = EMBEDDING_CONFIGS[embedding_key]
            if config["type"] != "embedding":
                raise ModelSelectionError(f"Model {embedding_key} is not an embedding model")
            
            try:
                cls._embedding_cache[embedding_key] = OllamaEmbeddings(
                    model=config["model"],
                    base_url=config["base_url"],
                )
            except Exception as e:
                raise ModelSelectionError(
                    f"Failed to create embedding model {embedding_key}: {str(e)}"
                ) from e
        
        return cls._embedding_cache[embedding_key]
    
    @classmethod
    def clear_cache(cls):
        """Clear the model cache."""
        cls._llm_cache.clear()
        cls._embedding_cache.clear()

