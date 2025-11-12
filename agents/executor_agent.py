"""Executor agent for executing tasks and generating outputs."""

from typing import List
from agents.base_agent import BaseAgent


class ExecutorAgent(BaseAgent):
    """Agent specialized in executing tasks and generating outputs."""
    
    def __init__(self, model_router=None):
        system_prompt = """You are an Executor Agent specialized in executing tasks and generating outputs.
Your role is to:
1. Understand the task requirements clearly
2. Execute the task step by step
3. Generate the requested output (code, content, analysis, etc.)
4. Ensure quality and completeness
5. Handle errors gracefully and provide feedback

For coding tasks, write clean, well-documented code.
For content tasks, ensure clarity and relevance.
Always verify your outputs meet the requirements."""
        
        super().__init__(
            name="Executor",
            model_router=model_router,
            system_prompt=system_prompt,
        )
    
    def get_capabilities(self) -> List[str]:
        """Get executor agent capabilities."""
        return [
            "Code generation",
            "Content creation",
            "Task execution",
            "Output generation",
            "Quality assurance",
        ]
    
    def execute(self, task: str, context: str = None) -> str:
        """
        Execute a task and generate output.
        
        Args:
            task: The task to execute
            context: Optional context or requirements
            
        Returns:
            Execution result or generated output
        """
        if context:
            prompt = f"""Execute the following task:

Task: {task}

Context/Requirements:
{context}

Provide the complete output or result."""
        else:
            prompt = f"""Execute the following task:

Task: {task}

Provide the complete output or result."""
        
        return self.process(prompt, context={"requires_coding": "code" in task.lower()})

