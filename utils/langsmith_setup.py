"""LangSmith integration for observability and tracing."""

import os
from typing import Optional
from config.settings import (
    LANGCHAIN_API_KEY,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_PROJECT
)


def setup_langsmith():
    """
    Set up LangSmith tracing if configured.
    
    This should be called at the start of the application.
    """
    if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
        
        # Optional: Set endpoint (defaults to https://api.smith.langchain.com)
        langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
        if langchain_endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = langchain_endpoint
        
        print(f"✅ LangSmith tracing enabled for project: {LANGCHAIN_PROJECT}")
        return True
    else:
        if not LANGCHAIN_API_KEY:
            print("ℹ️  LangSmith API key not set. Set LANGCHAIN_API_KEY to enable tracing.")
        if not LANGCHAIN_TRACING_V2:
            print("ℹ️  LangSmith tracing disabled. Set LANGCHAIN_TRACING_V2=true to enable.")
        return False


def get_langsmith_url(run_id: str) -> Optional[str]:
    """
    Get LangSmith URL for a run.
    
    Args:
        run_id: The run ID from LangChain
        
    Returns:
        URL to view the run in LangSmith, or None if not configured
    """
    if not LANGCHAIN_TRACING_V2 or not LANGCHAIN_API_KEY:
        return None
    
    # Extract project/org from API key if possible, or use default
    base_url = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
    # LangSmith UI is typically at smith.langchain.com
    ui_base = base_url.replace("api.smith", "smith").replace("/api", "")
    
    return f"{ui_base}/o/default/p/{LANGCHAIN_PROJECT}/r/{run_id}"

