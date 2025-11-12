"""Model router for dynamic model selection based on task characteristics."""

from typing import Dict, List, Optional, Any
from langchain_core.language_models import BaseChatModel
from models.model_factory import ModelFactory
from config.settings import MODEL_CONFIGS, MODEL_SELECTION_CRITERIA


class ModelRouter:
    """Routes tasks to the most appropriate model based on task characteristics."""
    
    def __init__(self):
        self.model_factory = ModelFactory()
        self.selection_history: List[Dict[str, Any]] = []
    
    def analyze_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a task to determine its characteristics.
        
        Args:
            task: The task description or prompt
            context: Optional context dictionary with additional information
            
        Returns:
            Dictionary with task characteristics
        """
        task_lower = task.lower()
        characteristics = {
            "length": len(task),
            "complexity": "simple",
            "requires_coding": False,
            "requires_multilingual": False,
            "urgency": "normal",
        }
        
        # Detect coding tasks
        coding_keywords = ["code", "function", "class", "python", "javascript", "api", "debug", "implement"]
        if any(keyword in task_lower for keyword in coding_keywords):
            characteristics["requires_coding"] = True
            characteristics["complexity"] = "coding"
        
        # Detect multilingual requirements
        multilingual_keywords = ["translate", "language", "multilingual", "spanish", "french", "german"]
        if any(keyword in task_lower for keyword in multilingual_keywords):
            characteristics["requires_multilingual"] = True
        
        # Assess complexity based on length and keywords
        if characteristics["length"] > 500:
            characteristics["complexity"] = "complex"
        elif characteristics["length"] > 200:
            characteristics["complexity"] = "moderate"
        
        # Check for urgency indicators
        if "urgent" in task_lower or "fast" in task_lower or "quick" in task_lower:
            characteristics["urgency"] = "high"
        
        # Override with context if provided
        if context:
            characteristics.update(context)
        
        return characteristics
    
    def select_model(self, task: str, context: Optional[Dict[str, Any]] = None) -> BaseChatModel:
        """
        Select the best model for a given task.
        
        Args:
            task: The task description or prompt
            context: Optional context dictionary
            
        Returns:
            Selected ChatOllama model instance
        """
        characteristics = self.analyze_task(task, context)
        
        # Determine model key based on characteristics
        model_key = None
        
        # Priority 1: Urgency (fast model for urgent tasks)
        if characteristics["urgency"] == "high":
            model_key = "phi3"
        
        # Priority 2: Multilingual requirements
        elif characteristics["requires_multilingual"]:
            model_key = "qwen3"
        
        # Priority 3: Coding tasks
        elif characteristics["requires_coding"]:
            # Use gemma3 for coding, but qwen3 for complex coding
            if characteristics["complexity"] == "complex":
                model_key = "qwen3"
            else:
                model_key = "gemma3"
        
        # Priority 4: Complexity-based selection
        else:
            complexity = characteristics["complexity"]
            if complexity in MODEL_SELECTION_CRITERIA:
                # Select first available model for this complexity level
                model_key = MODEL_SELECTION_CRITERIA[complexity][0]
            else:
                # Default to gemma3 for moderate complexity
                model_key = "gemma3"
        
        # Get the model instance
        model = self.model_factory.get_llm(model_key)
        
        # Log selection
        selection_record = {
            "task": task[:100],  # Truncate for logging
            "characteristics": characteristics,
            "selected_model": model_key,
        }
        self.selection_history.append(selection_record)
        
        return model
    
    def get_selection_history(self) -> List[Dict[str, Any]]:
        """Get the history of model selections."""
        return self.selection_history.copy()
    
    def clear_history(self):
        """Clear the selection history."""
        self.selection_history.clear()

