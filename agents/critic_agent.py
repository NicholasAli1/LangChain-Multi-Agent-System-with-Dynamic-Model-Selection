"""Critic agent for reviewing and evaluating outputs."""

from typing import List
from agents.base_agent import BaseAgent


class CriticAgent(BaseAgent):
    """Agent specialized in reviewing, evaluating, and providing feedback."""
    
    def __init__(self, model_router=None):
        system_prompt = """You are a Critic Agent specialized in reviewing and evaluating outputs.
Your role is to:
1. Review outputs for quality, accuracy, and completeness
2. Identify errors, issues, or areas for improvement
3. Provide constructive feedback
4. Verify that outputs meet requirements
5. Suggest improvements when needed

Be thorough but fair in your evaluations.
Provide specific, actionable feedback.
Focus on both strengths and areas for improvement."""
        
        super().__init__(
            name="Critic",
            model_router=model_router,
            system_prompt=system_prompt,
        )
    
    def get_capabilities(self) -> List[str]:
        """Get critic agent capabilities."""
        return [
            "Quality assessment",
            "Error detection",
            "Feedback generation",
            "Requirement verification",
            "Improvement suggestions",
        ]
    
    def review(self, output: str, requirements: str = None) -> str:
        """
        Review and evaluate an output.
        
        Args:
            output: The output to review
            requirements: Optional requirements to check against
            
        Returns:
            Review and feedback as a string
        """
        if requirements:
            prompt = f"""Review the following output against the requirements:

Output:
{output}

Requirements:
{requirements}

Provide a comprehensive review including:
1. Quality assessment
2. Requirement compliance check
3. Identified issues
4. Suggestions for improvement"""
        else:
            prompt = f"""Review the following output:

Output:
{output}

Provide a comprehensive review including:
1. Quality assessment
2. Strengths
3. Areas for improvement
4. Specific suggestions"""
        
        return self.process(prompt)

