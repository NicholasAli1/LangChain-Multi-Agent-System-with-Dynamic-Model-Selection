"""Feedback system for improving model selection based on user feedback."""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class FeedbackManager:
    """Manages feedback for model selection improvement."""
    
    def __init__(self, feedback_file: Optional[str] = None):
        """
        Initialize feedback manager.
        
        Args:
            feedback_file: Path to store feedback (defaults to ./feedback/feedback.json)
        """
        if feedback_file is None:
            feedback_dir = os.path.join(
                os.path.dirname(os.path.dirname(__file__)), "feedback"
            )
            Path(feedback_dir).mkdir(parents=True, exist_ok=True)
            feedback_file = os.path.join(feedback_dir, "feedback.json")
        
        self.feedback_file = feedback_file
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> Dict[str, Any]:
        """Load feedback data from file."""
        if os.path.exists(self.feedback_file):
            try:
                with open(self.feedback_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load feedback: {e}")
        
        return {
            "feedback_entries": [],
            "model_performance": {},
            "selection_stats": defaultdict(int)
        }
    
    def _save_feedback(self):
        """Save feedback data to file."""
        try:
            # Convert defaultdict to regular dict for JSON serialization
            data_to_save = {
                "feedback_entries": self.feedback_data["feedback_entries"],
                "model_performance": self.feedback_data["model_performance"],
                "selection_stats": dict(self.feedback_data["selection_stats"])
            }
            
            with open(self.feedback_file, 'w') as f:
                json.dump(data_to_save, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save feedback: {e}")
    
    def record_feedback(
        self,
        task: str,
        selected_model: str,
        rating: int,
        comments: Optional[str] = None,
        actual_model_used: Optional[str] = None
    ):
        """
        Record user feedback on model selection.
        
        Args:
            task: The task that was performed
            selected_model: The model that was selected
            rating: Rating from 1-5 (1=bad, 5=excellent)
            comments: Optional comments
            actual_model_used: The actual model used (if different from selected)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "task": task[:200],  # Truncate for storage
            "selected_model": selected_model,
            "actual_model_used": actual_model_used or selected_model,
            "rating": rating,
            "comments": comments
        }
        
        self.feedback_data["feedback_entries"].append(entry)
        
        # Update model performance stats
        model_key = actual_model_used or selected_model
        if model_key not in self.feedback_data["model_performance"]:
            self.feedback_data["model_performance"][model_key] = {
                "total_ratings": 0,
                "sum_ratings": 0,
                "average_rating": 0.0,
                "count": 0
            }
        
        perf = self.feedback_data["model_performance"][model_key]
        perf["total_ratings"] += rating
        perf["sum_ratings"] += rating
        perf["count"] += 1
        perf["average_rating"] = perf["sum_ratings"] / perf["count"]
        
        # Update selection stats
        self.feedback_data["selection_stats"][f"{selected_model}_{rating}"] += 1
        
        self._save_feedback()
    
    def get_model_performance(self, model_key: str) -> Dict[str, Any]:
        """
        Get performance statistics for a model.
        
        Args:
            model_key: The model key
            
        Returns:
            Performance statistics dictionary
        """
        return self.feedback_data["model_performance"].get(
            model_key,
            {
                "total_ratings": 0,
                "sum_ratings": 0,
                "average_rating": 0.0,
                "count": 0
            }
        )
    
    def get_best_model_for_task_type(self, task_type: str) -> Optional[str]:
        """
        Get the best performing model for a task type based on feedback.
        
        Args:
            task_type: Type of task (e.g., "coding", "complex", "simple")
            
        Returns:
            Best model key or None if no data
        """
        # This is a simplified version - in production, you'd analyze
        # feedback entries to determine task types and best models
        model_perf = self.feedback_data["model_performance"]
        
        if not model_perf:
            return None
        
        # Find model with highest average rating
        best_model = None
        best_rating = 0.0
        
        for model_key, perf in model_perf.items():
            if perf["count"] >= 3:  # Require at least 3 ratings
                if perf["average_rating"] > best_rating:
                    best_rating = perf["average_rating"]
                    best_model = model_key
        
        return best_model
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of all feedback."""
        return {
            "total_feedback_entries": len(self.feedback_data["feedback_entries"]),
            "model_performance": self.feedback_data["model_performance"],
            "selection_stats": dict(self.feedback_data["selection_stats"])
        }
    
    def clear_feedback(self):
        """Clear all feedback data."""
        self.feedback_data = {
            "feedback_entries": [],
            "model_performance": {},
            "selection_stats": defaultdict(int)
        }
        self._save_feedback()

