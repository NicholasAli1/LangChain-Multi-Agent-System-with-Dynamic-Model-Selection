"""FastAPI server to expose the multi-agent system via OpenAI-compatible API."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import time
from agents.supervisor import Supervisor
from models.model_router import ModelRouter
from utils.errors import WorkflowError
from utils.langsmith_setup import setup_langsmith

# Set up LangSmith tracing if configured
setup_langsmith()

app = FastAPI(title="LangChain Multi-Agent API", version="1.0.0")

# Enable CORS for Chat UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Chat UI URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize supervisor
model_router = ModelRouter()
supervisor = Supervisor(model_router=model_router)


# Request/Response models
class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "LangChain Multi-Agent API",
        "version": "1.0.0"
    }


@app.get("/v1/models")
async def list_models():
    """List available models."""
    return {
        "object": "list",
        "data": [
            {
                "id": "multi-agent-supervisor",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "langchain-multi-agent",
            },
            {
                "id": "phi3",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "ollama",
            },
            {
                "id": "gemma3",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "ollama",
            },
            {
                "id": "qwen3",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "ollama",
            },
        ]
    }


@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: ChatCompletionRequest):
    """
    Chat completions endpoint compatible with OpenAI API.
    Processes requests through the multi-agent system.
    """
    try:
        # Extract user message from conversation
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user messages found")
        
        # Get the latest user message as the task
        task = user_messages[-1].content
        
        # Process through multi-agent system
        result = supervisor.process(task)
        
        # Format response - use execution result or review as the response
        response_content = result.get("execution_result") or result.get("review") or "Task completed."
        
        # Include full workflow details in a structured format
        workflow_summary = f"""Task completed through multi-agent workflow:

📋 Plan:
{result.get('plan', 'N/A')}

🔍 Research:
{result.get('research', 'N/A')}

⚙️ Execution:
{result.get('execution_result', 'N/A')}

✅ Review:
{result.get('review', 'N/A')}
"""
        
        # Use workflow summary for more detailed responses, or just execution result
        final_content = workflow_summary if request.model == "multi-agent-supervisor" else response_content
        
        # Create response
        response_message = Message(role="assistant", content=final_content)
        
        # Estimate token usage (rough approximation)
        prompt_tokens = len(task.split()) * 1.3  # Rough estimate
        completion_tokens = len(final_content.split()) * 1.3
        
        return ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time())}",
            created=int(time.time()),
            model=request.model,
            choices=[
                Choice(
                    index=0,
                    message=response_message,
                    finish_reason="stop"
                )
            ],
            usage=Usage(
                prompt_tokens=int(prompt_tokens),
                completion_tokens=int(completion_tokens),
                total_tokens=int(prompt_tokens + completion_tokens)
            )
        )
    
    except WorkflowError as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


class FeedbackRequest(BaseModel):
    task: str
    selected_model: str
    rating: int  # 1-5
    comments: Optional[str] = None


@app.post("/v1/feedback")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback on model selection performance.
    
    This helps improve model selection over time.
    """
    try:
        if not 1 <= request.rating <= 5:
            raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
        
        model_router.record_feedback(
            task=request.task,
            selected_model=request.selected_model,
            rating=request.rating,
            comments=request.comments
        )
        
        return {
            "status": "success",
            "message": "Feedback recorded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recording feedback: {str(e)}")


@app.get("/v1/feedback/summary")
async def get_feedback_summary():
    """Get summary of feedback data."""
    try:
        summary = model_router.get_feedback_summary()
        if summary:
            return summary
        return {
            "message": "No feedback data available yet",
            "total_feedback_entries": 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting feedback summary: {str(e)}")


if __name__ == "__main__":
    import os
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

