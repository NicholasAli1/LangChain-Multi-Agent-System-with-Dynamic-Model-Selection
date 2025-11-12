"""Main entry point for the multi-agent system with dynamic model selection."""

from agents.supervisor import Supervisor
from models.model_router import ModelRouter
from utils.state import AgentState
from utils.langsmith_setup import setup_langsmith

# Set up LangSmith tracing if configured
setup_langsmith()


def main():
    """Main function to run the multi-agent system."""
    print("=" * 60)
    print("Multi-Agent System with Dynamic Model Selection")
    print("=" * 60)
    print()
    
    # Initialize supervisor with model router
    model_router = ModelRouter()
    supervisor = Supervisor(model_router=model_router)
    
    # Example task
    task = "Create a Python function that calculates the Fibonacci sequence up to n terms, with proper error handling and documentation."
    
    print(f"Task: {task}")
    print()
    print("Processing through multi-agent workflow...")
    print("-" * 60)
    
    # Process the task
    result: AgentState = supervisor.process(task)
    
    # Display results
    print("\n" + "=" * 60)
    print("WORKFLOW RESULTS")
    print("=" * 60)
    
    print("\n📋 PLAN:")
    print(result.get("plan", "N/A"))
    print()
    
    print("🔍 RESEARCH:")
    print(result.get("research", "N/A"))
    print()
    
    print("⚙️  EXECUTION RESULT:")
    print(result.get("execution_result", "N/A"))
    print()
    
    print("✅ REVIEW:")
    print(result.get("review", "N/A"))
    print()
    
    print("=" * 60)
    print("Model Selection History:")
    print("=" * 60)
    history = model_router.get_selection_history()
    for i, selection in enumerate(history, 1):
        print(f"\nSelection {i}:")
        print(f"  Task: {selection['task']}")
        print(f"  Selected Model: {selection['selected_model']}")
        print(f"  Characteristics: {selection['characteristics']}")
    
    print("\n" + "=" * 60)
    print("Workflow completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
