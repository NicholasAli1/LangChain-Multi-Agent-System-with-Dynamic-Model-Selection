"""Custom error classes for the multi-agent system."""


class MultiAgentError(Exception):
    """Base exception for multi-agent system errors."""
    pass


class ModelSelectionError(MultiAgentError):
    """Error in model selection."""
    pass


class AgentExecutionError(MultiAgentError):
    """Error during agent execution."""
    pass


class WorkflowError(MultiAgentError):
    """Error in workflow execution."""
    pass

