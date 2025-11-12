"""Planner agent for breaking down tasks into steps."""

from typing import List
from agents.base_agent import BaseAgent


class PlannerAgent(BaseAgent):
    """Agent specialized in planning and task decomposition."""
    
    def __init__(self, model_router=None):
        system_prompt = """You are a Planning Agent specialized in breaking down complex tasks into manageable steps.
Your role is to:
1. Analyze the given task or goal
2. Break it down into clear, actionable steps
3. Identify dependencies between steps
4. Suggest the order of execution
5. Identify potential challenges or requirements

Always provide your response in a structured format with numbered steps.
Be specific and actionable in your planning."""
        
        super().__init__(
            name="Planner",
            model_router=model_router,
            system_prompt=system_prompt,
        )
    
    def get_capabilities(self) -> List[str]:
        """Get planner agent capabilities."""
        return [
            "Task decomposition",
            "Step-by-step planning",
            "Dependency analysis",
            "Execution order optimization",
        ]
    
    def create_plan(self, task: str) -> str:
        """
        Create a detailed plan for a given task.
        
        Args:
            task: The task or goal to plan for
            
        Returns:
            Detailed plan as a string
        """
        prompt = f"""Create a detailed plan for the following task:

Task: {task}

Provide a step-by-step plan that breaks down this task into actionable steps.
Include any dependencies, prerequisites, or considerations."""
        
        return self.process(prompt)

