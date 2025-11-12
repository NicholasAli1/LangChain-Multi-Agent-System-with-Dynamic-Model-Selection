"""State management for multi-agent workflows."""

from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """State structure for the multi-agent workflow."""
    
    messages: List[BaseMessage]
    task: str
    plan: Optional[str]
    research: Optional[str]
    execution_result: Optional[str]
    review: Optional[str]
    current_step: str
    completed_steps: List[str]
    context: Dict[str, Any]

