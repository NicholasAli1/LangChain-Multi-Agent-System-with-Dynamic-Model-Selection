"""Base agent class for all specialized agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Union
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from models.model_router import ModelRouter
from utils.memory import VectorMemory


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""
    
    def __init__(
        self,
        name: str,
        model_router: Optional[ModelRouter] = None,
        system_prompt: Optional[str] = None,
        use_memory: bool = True,
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Agent name/identifier
            model_router: Model router instance (creates new one if None)
            system_prompt: System prompt for the agent
            use_memory: Whether to use vector memory for long-term storage
        """
        self.name = name
        self.model_router = model_router or ModelRouter()
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.conversation_history: List[BaseMessage] = []
        self.memory = VectorMemory(collection_name=f"{name}_memory") if use_memory else None
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for the agent."""
        return f"You are {self.name}, a helpful AI assistant."
    
    def _build_prompt(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> List[BaseMessage]:
        """
        Build the prompt with system message, relevant memory, and conversation history.
        
        Args:
            user_input: User's input message
            context: Optional context dictionary
            
        Returns:
            List of messages for the LLM
        """
        messages = []
        
        # Add system message (use SystemMessage for proper handling)
        if self.system_prompt:
            messages.append(SystemMessage(content=self.system_prompt))
        
        # Add relevant context from memory if available
        if self.memory:
            relevant_context = self.memory.get_relevant_context(user_input, k=2)
            if relevant_context:
                context_msg = f"Relevant previous conversations:\n{relevant_context}\n\n"
                messages.append(SystemMessage(content=context_msg))
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current user input
        messages.append(HumanMessage(content=user_input))
        
        return messages
    
    def _select_model(self, task: str, context: Optional[Dict[str, Any]] = None) -> Union[BaseChatModel, Any]:
        """
        Select the appropriate model for the task.
        
        Args:
            task: Task description
            context: Optional context
            
        Returns:
            Selected model instance
        """
        return self.model_router.select_model(task, context)
    
    def process(self, input_text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process input and return response.
        
        Args:
            input_text: Input text to process
            context: Optional context dictionary
            
        Returns:
            Agent's response
        """
        # Select model
        model = self._select_model(input_text, context)
        
        # Build messages
        messages = self._build_prompt(input_text, context)
        
        # Get response
        response = model.invoke(messages)
        
        # Extract content
        if hasattr(response, "content"):
            response_text = response.content
        else:
            response_text = str(response)
        
        # Update conversation history
        self.conversation_history.append(HumanMessage(content=input_text))
        self.conversation_history.append(AIMessage(content=response_text))
        
        # Store in long-term memory
        if self.memory:
            self.memory.add_conversation(
                task=input_text,
                response=response_text,
                metadata={
                    "agent": self.name,
                    "model": context.get("model_key") if context else None
                }
            )
        
        # Keep history manageable (last 10 exchanges)
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
        
        return response_text
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get list of agent capabilities.
        
        Returns:
            List of capability descriptions
        """
        pass
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()

