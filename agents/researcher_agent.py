"""Researcher agent for gathering and synthesizing information."""

from typing import List
from agents.base_agent import BaseAgent


class ResearcherAgent(BaseAgent):
    """Agent specialized in research and information gathering."""
    
    def __init__(self, model_router=None):
        system_prompt = """You are a Research Agent specialized in gathering, analyzing, and synthesizing information.
Your role is to:
1. Identify what information is needed for a given task
2. Gather relevant information from available sources
3. Analyze and synthesize the information
4. Present findings in a clear, organized manner
5. Cite sources when applicable

Always provide well-structured, factual responses based on the information available.
If information is not available, clearly state what is missing."""
        
        super().__init__(
            name="Researcher",
            model_router=model_router,
            system_prompt=system_prompt,
        )
    
    def get_capabilities(self) -> List[str]:
        """Get researcher agent capabilities."""
        return [
            "Information gathering",
            "Data synthesis",
            "Fact-checking",
            "Source analysis",
            "Report generation",
        ]
    
    def research(self, topic: str, questions: List[str] = None) -> str:
        """
        Research a topic and answer specific questions.
        
        Args:
            topic: The topic to research
            questions: Optional list of specific questions to answer
            
        Returns:
            Research findings as a string
        """
        if questions:
            questions_text = "\n".join([f"- {q}" for q in questions])
            prompt = f"""Research the following topic and answer the specific questions:

Topic: {topic}

Questions:
{questions_text}

Provide comprehensive answers based on your knowledge."""
        else:
            prompt = f"""Research and provide information about the following topic:

Topic: {topic}

Provide a comprehensive overview, key points, and relevant details."""
        
        return self.process(prompt)

