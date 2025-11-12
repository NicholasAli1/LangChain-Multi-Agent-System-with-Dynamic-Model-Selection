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
    # Re-read from environment to ensure we have latest values
    api_key = os.getenv("LANGCHAIN_API_KEY", "").strip('"\'')
    tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2", "false").strip('"\'').lower() == "true"
    project = os.getenv("LANGCHAIN_PROJECT", "langchain_multi_model").strip('"\'')
    
    # Also check the config values (in case .env was loaded after config import)
    if not api_key and LANGCHAIN_API_KEY:
        api_key = LANGCHAIN_API_KEY
    if not tracing_v2 and LANGCHAIN_TRACING_V2:
        tracing_v2 = LANGCHAIN_TRACING_V2
    if project == "langchain_multi_model" and LANGCHAIN_PROJECT != "langchain_multi_model":
        project = LANGCHAIN_PROJECT
    
    if tracing_v2 and api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = api_key
        os.environ["LANGCHAIN_PROJECT"] = project
        
        # Optional: Set endpoint (defaults to https://api.smith.langchain.com)
        langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT")
        if langchain_endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = langchain_endpoint
        
        print(f"✅ LangSmith tracing enabled for project: {project}")
        return True
    else:
        if not api_key:
            print("ℹ️  LangSmith API key not set. Set LANGCHAIN_API_KEY to enable tracing.")
        if not tracing_v2:
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

