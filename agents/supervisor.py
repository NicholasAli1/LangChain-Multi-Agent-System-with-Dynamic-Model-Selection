"""Supervisor agent for coordinating the multi-agent workflow."""

from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from utils.state import AgentState
from utils.errors import WorkflowError
from agents.planner_agent import PlannerAgent
from agents.researcher_agent import ResearcherAgent
from agents.executor_agent import ExecutorAgent
from agents.critic_agent import CriticAgent
from models.model_router import ModelRouter


class Supervisor:
    """Supervisor that coordinates multiple specialized agents."""
    
    def __init__(self, model_router: Optional[ModelRouter] = None):
        """
        Initialize the supervisor with specialized agents.
        
        Args:
            model_router: Optional model router (creates new one if None)
        """
        self.model_router = model_router or ModelRouter()
        
        # Initialize specialized agents
        self.planner = PlannerAgent(model_router=self.model_router)
        self.researcher = ResearcherAgent(model_router=self.model_router)
        self.executor = ExecutorAgent(model_router=self.model_router)
        self.critic = CriticAgent(model_router=self.model_router)
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("planner", self._plan_node)
        workflow.add_node("researcher", self._research_node)
        workflow.add_node("executor", self._execute_node)
        workflow.add_node("critic", self._critic_node)
        
        # Define edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "researcher")
        workflow.add_edge("researcher", "executor")
        workflow.add_edge("executor", "critic")
        workflow.add_edge("critic", END)
        
        return workflow.compile()
    
    def _plan_node(self, state: AgentState) -> AgentState:
        """Planning node."""
        task = state.get("task", "")
        plan = self.planner.create_plan(task)
        
        state["plan"] = plan
        state["current_step"] = "planning"
        state["completed_steps"] = state.get("completed_steps", []) + ["planning"]
        state["messages"] = state.get("messages", []) + [
            HumanMessage(content=f"Task: {task}"),
            AIMessage(content=f"Plan: {plan}"),
        ]
        
        return state
    
    def _research_node(self, state: AgentState) -> AgentState:
        """Research node."""
        task = state.get("task", "")
        plan = state.get("plan", "")
        
        research_prompt = f"""Based on the task and plan, identify what information or research is needed:

Task: {task}
Plan: {plan}

What information should be gathered before execution?"""
        
        research = self.researcher.research(research_prompt)
        
        state["research"] = research
        state["current_step"] = "research"
        state["completed_steps"] = state.get("completed_steps", []) + ["research"]
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Research: {research}"),
        ]
        
        return state
    
    def _execute_node(self, state: AgentState) -> AgentState:
        """Execution node."""
        task = state.get("task", "")
        plan = state.get("plan", "")
        research = state.get("research", "")
        
        execution_context = f"""Plan:
{plan}

Research:
{research}"""
        
        result = self.executor.execute(task, execution_context)
        
        state["execution_result"] = result
        state["current_step"] = "execution"
        state["completed_steps"] = state.get("completed_steps", []) + ["execution"]
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Execution Result: {result}"),
        ]
        
        return state
    
    def _critic_node(self, state: AgentState) -> AgentState:
        """Critic/review node."""
        task = state.get("task", "")
        execution_result = state.get("execution_result", "")
        
        review = self.critic.review(execution_result, requirements=task)
        
        state["review"] = review
        state["current_step"] = "review"
        state["completed_steps"] = state.get("completed_steps", []) + ["review"]
        state["messages"] = state.get("messages", []) + [
            AIMessage(content=f"Review: {review}"),
        ]
        
        return state
    
    def process(self, task: str, context: Optional[Dict[str, Any]] = None) -> AgentState:
        """
        Process a task through the multi-agent workflow.
        
        Args:
            task: The task to process
            context: Optional context dictionary
            
        Returns:
            Final state after workflow execution
            
        Raises:
            WorkflowError: If workflow execution fails
        """
        if not task or not task.strip():
            raise WorkflowError("Task cannot be empty")
        
        initial_state: AgentState = {
            "messages": [],
            "task": task,
            "plan": None,
            "research": None,
            "execution_result": None,
            "review": None,
            "current_step": "initialized",
            "completed_steps": [],
            "context": context or {},
        }
        
        try:
            # Execute workflow
            final_state = self.workflow.invoke(initial_state)
            return final_state
        except Exception as e:
            raise WorkflowError(f"Workflow execution failed: {str(e)}") from e

