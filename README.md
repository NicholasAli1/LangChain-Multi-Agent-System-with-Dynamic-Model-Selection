# LangChain Multi-Agent System with Dynamic Model Selection

A comprehensive multi-agent system built with LangChain and LangGraph that dynamically selects the optimal model for each task based on task characteristics. Includes Hugging Face Chat UI integration for a beautiful web interface.

## Features

- **Multi-Agent Architecture**: Supervisor pattern with specialized agents (Planner, Researcher, Executor, Critic)
- **Dynamic Model Selection**: Automatically routes tasks to the best model (phi3, gemma3, qwen3) based on complexity, requirements, and urgency
- **LangGraph Workflow**: Structured workflow using LangGraph for agent coordination
- **Modular Design**: Clean, maintainable codebase with separated concerns
- **Error Handling**: Robust error handling and logging throughout
- **Chat UI Integration**: FastAPI server with OpenAI-compatible API for Hugging Face Chat UI integration
- **One-Command Startup**: Single script to launch everything

## 🚀 Quick Start (One Command!)

**Start everything with a single command:**

```bash
./start_all.sh
```

This will automatically:
- ✅ Check Docker and start MongoDB
- ✅ Start the API server (port 8000)
- ✅ Start Chat UI (port 5173) and open it in your browser

**Stop everything:**
```bash
./stop_all.sh
```

## Installation

1. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up Ollama**:
   - Ensure Ollama is running on `http://localhost:10000` (or update `config/settings.py`)
   - Make sure the following models are available:
     - `phi3:mini`
     - `gemma3:latest`
     - `qwen3:latest`
     - `embeddinggemma:latest` (optional)
     - `mxbai-embed-large:latest` (optional)

4. **Set up Chat UI** (if using web interface):
   ```bash
   git clone https://github.com/huggingface/chat-ui
   cd chat-ui
   npm install
   ```
   
   The `start_all.sh` script will automatically configure Chat UI, but if you need to set it up manually, create `.env.local` in the Chat UI directory:
   ```env
   # MongoDB connection (required)
   MONGODB_URL=mongodb://localhost:27017
   
   # Multi-Agent API configuration
   OPENAI_BASE_URL=http://localhost:8000/v1
   OPENAI_API_KEY=not-needed
   
   # For OpenAI-compatible endpoints, Chat UI will auto-discover models from the API
   # No MODELS override needed - the API server provides model list via /v1/models
   ```
   
   **Note**: When using OpenAI-compatible endpoints, you don't need to specify `tokenizer` or `chatPromptTemplate` - Chat UI will automatically discover available models from your API server.

## Project Structure

```
langchain_multi_model/
├── config/              # Configuration settings
│   ├── __init__.py
│   └── settings.py      # Model configs, base URLs, selection criteria
├── models/              # Model management
│   ├── __init__.py
│   ├── model_factory.py # Factory for creating LLM/embedding models
│   └── model_router.py  # Dynamic model selection logic
├── agents/              # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py    # Base class for all agents
│   ├── planner_agent.py # Task planning and decomposition
│   ├── researcher_agent.py # Information gathering
│   ├── executor_agent.py  # Task execution
│   ├── critic_agent.py    # Quality review
│   └── supervisor.py      # Workflow coordinator
├── tools/               # Agent tools (for future expansion)
│   └── __init__.py
├── utils/               # Utilities
│   ├── __init__.py
│   ├── state.py         # State management types
│   ├── logging.py       # Logging utilities
│   └── errors.py        # Custom exceptions
├── api_server.py        # FastAPI server for Chat UI integration
├── main.py              # Main entry point
├── start_all.sh         # Master startup script
├── stop_all.sh          # Stop all services
├── start_mongo.sh       # Start MongoDB only
├── start_api.sh         # Start API server only
├── requirements.txt     # Dependencies
└── README.md            # This file
```

## Configuration

Edit `config/settings.py` to customize:
- Base URL for Ollama
- Model configurations
- Model selection criteria
- Embedding models

## Usage

### Basic Usage (Python)

```python
from agents.supervisor import Supervisor
from models.model_router import ModelRouter

# Initialize supervisor
model_router = ModelRouter()
supervisor = Supervisor(model_router=model_router)

# Process a task
task = "Create a Python function that calculates Fibonacci numbers"
result = supervisor.process(task)

# Access results
print(result["plan"])
print(result["execution_result"])
print(result["review"])
```

### Running the Example

```bash
python main.py
```

### Chat UI Integration

**Easiest Way - One Command:**
```bash
./start_all.sh
```

This starts MongoDB, API server, and Chat UI automatically!

**Manual Setup:**
1. Start MongoDB: `./start_mongo.sh` or `docker run -d -p 27017:27017 --name mongo-chatui mongo:latest`
2. Start the API server: `python api_server.py`
3. Start Chat UI: `cd /path/to/chat-ui && npm run dev -- --open`
4. Access Chat UI at `http://localhost:5173`

**Stop Everything:**
```bash
./stop_all.sh
```

The API server exposes an OpenAI-compatible endpoint at `http://localhost:8000/v1/chat/completions`, allowing you to use Hugging Face Chat UI or any other OpenAI-compatible client.

## How It Works

1. **Task Intake**: User provides a task
2. **Planning**: Planner agent breaks down the task into steps
3. **Research**: Researcher agent gathers necessary information
4. **Execution**: Executor agent performs the task
5. **Review**: Critic agent evaluates the output

At each step, the **Model Router** analyzes the task and selects the most appropriate model:
- **phi3**: Fast responses, simple tasks, urgent requests
- **gemma3**: Coding tasks, general analysis
- **qwen3**: Complex tasks, multilingual requirements

## Model Selection Logic

The router considers:
- **Task complexity**: Length, keywords, structure
- **Task type**: Coding, research, multilingual, etc.
- **Urgency**: Fast model for urgent tasks
- **Capabilities**: Model-specific strengths

## Startup Scripts

### `start_all.sh` - Master Script
Launches everything in one command:
- Checks Docker status
- Starts MongoDB container
- Starts API server in background
- Starts Chat UI and opens browser
- Monitors all services

### `stop_all.sh` - Stop Everything
Stops API server and Chat UI (keeps MongoDB running)

### `start_mongo.sh` - MongoDB Only
Starts MongoDB container if not running

### `start_api.sh` - API Server Only
Starts the FastAPI server

## Manual Control

If you prefer to start things individually:

### Start MongoDB only:
```bash
./start_mongo.sh
```

### Start API server only:
```bash
python api_server.py
# Or
./start_api.sh
```

### Start Chat UI only:
```bash
cd /path/to/chat-ui
npm run dev -- --open
```

## Extending the System

### Adding a New Agent

1. Create a new file in `agents/` (e.g., `agents/custom_agent.py`)
2. Inherit from `BaseAgent`
3. Implement `get_capabilities()` method
4. Add to supervisor workflow in `agents/supervisor.py`

### Adding a New Model

1. Add model config to `config/settings.py` in `MODEL_CONFIGS`
2. Update `MODEL_SELECTION_CRITERIA` if needed
3. The router will automatically consider the new model

### Adding Tools

1. Create tool functions in `tools/`
2. Pass tools to agents via their constructors
3. Agents can use tools via LangChain's tool integration

## Error Handling

The system includes custom exceptions:
- `MultiAgentError`: Base exception
- `ModelSelectionError`: Model selection failures
- `AgentExecutionError`: Agent execution failures
- `WorkflowError`: Workflow execution failures

## Logging

Configure logging in `utils/logging.py`:
```python
from utils.logging import setup_logging

logger = setup_logging(level=logging.INFO, log_file="app.log")
```

## Troubleshooting

### "Docker is not running"
- Start Docker Desktop application
- Wait for it to fully start
- Run `./start_all.sh` again

### "Port already in use"
- API server (8000): `lsof -ti:8000 | xargs kill`
- Chat UI (5173): `lsof -ti:5173 | xargs kill`
- Or use `./stop_all.sh` first

### Services not starting
- Check logs:
  - API server: `tail -f /tmp/api_server.log`
  - Chat UI: `tail -f /tmp/chat_ui.log`

### Chat UI shows wrong model
- Make sure `.env.local` exists in Chat UI directory
- Restart Chat UI after creating/updating `.env.local`

### Models not found
- Ensure Ollama is running and models are pulled
- Check base URL in `config/settings.py`

### Import errors
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.10+ required)

### Workflow fails
- Check logs for specific error messages
- Verify model availability
- Ensure task is well-formed

### MongoDB connection errors
- Verify MongoDB is running: `docker ps | grep mongo`
- Check MongoDB logs: `docker logs mongo-chatui`
- Restart MongoDB: `docker start mongo-chatui`

## Status Check

Check if services are running:

```bash
# MongoDB
docker ps | grep mongo

# API Server
curl http://localhost:8000/

# Chat UI
curl http://localhost:5173/
```

## Future Enhancements

- [ ] Add more specialized agents (e.g., Code Reviewer, Documentation Agent)
- [ ] Implement speculative execution (parallel model runs)
- [ ] Add vector store integration for long-term memory
- [ ] Implement feedback loops for model selection improvement
- [ ] Add LangSmith integration for observability
- [ ] Support for remote models (OpenAI, Anthropic, etc.)
- [ ] Human-in-the-loop capabilities
- [ ] Checkpointing for long workflows

## License

This project is provided as-is for educational and development purposes.
