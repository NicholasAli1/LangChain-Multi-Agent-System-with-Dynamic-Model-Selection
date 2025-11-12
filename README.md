# 🤖 LangChain Multi-Agent System

> A powerful multi-agent system with dynamic model selection, long-term memory, and intelligent feedback loops. Built with LangChain, LangGraph, and integrated with Hugging Face Chat UI.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1.0+-green.svg)](https://langchain.com/)

---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🧠 **Multi-Agent Architecture** | Supervisor pattern with specialized agents (Planner, Researcher, Executor, Critic) |
| 🎯 **Dynamic Model Selection** | Automatically routes tasks to optimal models (phi3, gemma3, qwen3) based on complexity |
| 🔄 **LangGraph Workflow** | Structured workflow coordination using LangGraph |
| 💾 **Long-Term Memory** | Vector store-based memory for persistent conversation context |
| 📊 **Feedback Loops** | Learns from user feedback to improve model selection |
| 📈 **LangSmith Integration** | Full observability and tracing capabilities |
| 🎨 **Chat UI Integration** | Beautiful web interface via Hugging Face Chat UI |
| 🚀 **One-Command Startup** | Launch everything with a single script |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Docker Desktop (for MongoDB)
- Node.js & npm (for Chat UI)
- Ollama running on `http://localhost:10000`

### Installation

```bash
# 1. Clone and setup
git clone <your-repo>
cd langchain_multi_model

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure Ollama models are available
# phi3:mini, gemma3:latest, qwen3:latest
```

### Launch Everything (One Command)

```bash
./start_all.sh
```

**What it does:**
- ✅ Checks Docker and starts MongoDB
- ✅ Starts API server (port 8000)
- ✅ Starts Chat UI (port 5173) and opens browser

**Stop everything:**
```bash
./stop_all.sh
```

---

## 📖 Table of Contents

- [Quick Start](#-quick-start)
- [Architecture Overview](#-architecture-overview)
- [Usage Examples](#-usage-examples)
- [Advanced Features](#-advanced-features)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Extending the System](#-extending-the-system)
- [Troubleshooting](#-troubleshooting)

---

## 🏗️ Architecture Overview

### System Flow

```
User Task
    ↓
Model Router (Analyzes task characteristics)
    ↓
┌─────────────────────────────────────────┐
│  Multi-Agent Workflow (LangGraph)       │
├─────────────────────────────────────────┤
│  1. Planner Agent    → Breaks down task │
│  2. Researcher Agent → Gathers info     │
│  3. Executor Agent   → Executes task    │
│  4. Critic Agent     → Reviews output   │
└─────────────────────────────────────────┘
    ↓
Response with Full Workflow Details
```

### Model Selection Logic

The **Model Router** intelligently selects models based on:

| Criteria | Model Selection |
|----------|----------------|
| **Urgency** (fast/urgent keywords) | `phi3` - Fastest response |
| **Multilingual** (translate/language) | `qwen3` - Best multilingual support |
| **Coding** (code/function/class) | `gemma3` or `qwen3` (complex) |
| **Complexity** (length > 500 chars) | `qwen3` - Handles complex tasks |
| **Simple** (default) | `phi3` or `gemma3` |

**Feedback Integration:** After collecting ≥3 ratings with ≥4.0 average, the router prioritizes well-performing models.

---

## 💻 Usage Examples

### Basic Python Usage

```python
from agents.supervisor import Supervisor
from models.model_router import ModelRouter

# Initialize
model_router = ModelRouter()
supervisor = Supervisor(model_router=model_router)

# Process a task
task = "Create a Python function that calculates Fibonacci numbers"
result = supervisor.process(task)

# Access results
print("Plan:", result["plan"])
print("Execution:", result["execution_result"])
print("Review:", result["review"])
```

### Running the Example

```bash
python main.py
```

### Chat UI Integration

**Automatic (Recommended):**
```bash
./start_all.sh  # Launches everything
```

**Manual Setup:**
```bash
# 1. Start MongoDB
./start_mongo.sh

# 2. Start API server
python api_server.py

# 3. Start Chat UI (in separate terminal)
cd /path/to/chat-ui
npm run dev -- --open
```

Access Chat UI at `http://localhost:5173`

---

## 🔧 Advanced Features

### 1. Vector Store Integration (Long-Term Memory)

**Automatic & Enabled by Default**

All conversations are automatically stored in a FAISS vector database, enabling:

- **Semantic Search**: Retrieve relevant past conversations
- **Context Retrieval**: Agents automatically get relevant context for new tasks
- **Persistent Storage**: Memory persists across sessions in `./memory/` directory

**Example:**
```python
# Memory is automatically used - no configuration needed!
supervisor = Supervisor(ModelRouter())
result = supervisor.process("Your task")

# Agents automatically retrieve relevant past conversations
```

**Manual Memory Access:**
```python
from utils.memory import VectorMemory

memory = VectorMemory()
# Search for relevant conversations
results = memory.search("Python functions", k=5)
```

### 2. Feedback Loops for Model Selection

**Improve model selection through user feedback**

**Via API:**
```bash
# Submit feedback (1-5 rating)
curl -X POST http://localhost:8000/v1/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Create a Python function",
    "selected_model": "gemma3",
    "rating": 5,
    "comments": "Excellent response!"
  }'

# View feedback summary
curl http://localhost:8000/v1/feedback/summary
```

**Programmatic:**
```python
model_router.record_feedback(
    task="Create a function",
    selected_model="gemma3",
    rating=5,
    comments="Great!"
)

# Get performance stats
summary = model_router.get_feedback_summary()
print(summary["model_performance"])
```

**How it works:**
- Feedback is stored in `./feedback/feedback.json`
- Router uses feedback when models have ≥3 ratings with ≥4.0 average
- Automatically improves future model selections

### 3. LangSmith Integration (Observability)

**Full tracing and observability**

**Setup:**
```bash
# 1. Get API key from https://smith.langchain.com
# 2. Set environment variables
export LANGCHAIN_API_KEY="your-api-key"
export LANGCHAIN_TRACING_V2="true"
export LANGCHAIN_PROJECT="langchain_multi_model"
```

**Features:**
- ✅ Automatic tracing of all agent interactions
- ✅ Model selection tracking
- ✅ Performance metrics
- ✅ Debugging insights
- ✅ View traces in LangSmith dashboard

**Note:** LangSmith automatically enables when API key is configured. No code changes needed!

---

## ⚙️ Configuration

### Model Configuration

Edit `config/settings.py` to customize:

```python
# Base URL for Ollama
BASE_URL = "http://localhost:10000"

# Add new models
MODEL_CONFIGS = {
    "your_model": {
        "model": "your-model:latest",
        "base_url": BASE_URL,
        "type": "llm",
        "capabilities": ["general"],
        "max_tokens": 2048,
        "temperature": 0.7,
    }
}

# Update selection criteria
MODEL_SELECTION_CRITERIA = {
    "your_task_type": ["your_model"]
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:10000` |
| `LANGCHAIN_API_KEY` | LangSmith API key | (optional) |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | `false` |
| `LANGCHAIN_PROJECT` | LangSmith project name | `langchain_multi_model` |
| `API_PORT` | API server port | `8000` |

---

## 📁 Project Structure

```
langchain_multi_model/
├── 📂 config/                 # Configuration
│   ├── __init__.py
│   └── settings.py            # Model configs, URLs, criteria
│
├── 📂 models/                 # Model Management
│   ├── __init__.py
│   ├── model_factory.py       # Creates/caches LLM & embedding models
│   └── model_router.py        # Intelligent model selection
│
├── 📂 agents/                 # Agent Implementations
│   ├── __init__.py
│   ├── base_agent.py          # Base class with memory integration
│   ├── planner_agent.py       # Task planning & decomposition
│   ├── researcher_agent.py    # Information gathering
│   ├── executor_agent.py      # Task execution
│   ├── critic_agent.py        # Quality review
│   └── supervisor.py          # LangGraph workflow coordinator
│
├── 📂 utils/                  # Utilities
│   ├── __init__.py
│   ├── state.py               # State management (TypedDict)
│   ├── memory.py              # Vector store memory
│   ├── feedback.py            # Feedback management
│   ├── langsmith_setup.py     # LangSmith integration
│   ├── logging.py             # Logging utilities
│   └── errors.py              # Custom exceptions
│
├── 📂 tools/                  # Agent Tools (for expansion)
│   └── __init__.py
│
├── 🚀 start_all.sh            # Master startup script
├── 🛑 stop_all.sh             # Stop all services
├── 🗄️  start_mongo.sh         # Start MongoDB only
├── 🔌 start_api.sh            # Start API server only
│
├── 🌐 api_server.py            # FastAPI server (OpenAI-compatible)
├── 📝 main.py                 # Main entry point
├── 📋 requirements.txt        # Dependencies
└── 📖 README.md               # This file
```

---

## 🔌 API Endpoints

The API server exposes OpenAI-compatible endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/v1/models` | GET | List available models |
| `/v1/chat/completions` | POST | Process task through multi-agent system |
| `/v1/feedback` | POST | Submit feedback on model performance |
| `/v1/feedback/summary` | GET | Get feedback statistics |

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

---

## 🛠️ Extending the System

### Adding a New Agent

1. **Create agent file** (`agents/my_agent.py`):
```python
from agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, model_router=None):
        system_prompt = "You are a specialized agent for..."
        super().__init__("MyAgent", model_router, system_prompt)
    
    def get_capabilities(self):
        return ["capability1", "capability2"]
```

2. **Add to supervisor** (`agents/supervisor.py`):
```python
self.my_agent = MyAgent(model_router=self.model_router)
workflow.add_node("my_agent", self._my_agent_node)
```

### Adding a New Model

1. **Add to config** (`config/settings.py`):
```python
MODEL_CONFIGS["new_model"] = {
    "model": "new-model:latest",
    "base_url": BASE_URL,
    "type": "llm",
    "capabilities": ["general"],
    "max_tokens": 4096,
    "temperature": 0.7,
}
```

2. **Update selection criteria** (optional):
```python
MODEL_SELECTION_CRITERIA["new_task_type"] = ["new_model"]
```

### Adding Tools

1. **Create tool** (`tools/my_tool.py`):
```python
from langchain.tools import tool

@tool
def my_tool(input: str) -> str:
    """Tool description."""
    # Tool implementation
    return result
```

2. **Pass to agents**:
```python
from tools.my_tool import my_tool
agent = MyAgent(tools=[my_tool])
```

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>Docker is not running</b></summary>

**Solution:**
1. Start Docker Desktop application
2. Wait for it to fully start
3. Run `./start_all.sh` again

</details>

<details>
<summary><b>Port already in use</b></summary>

**Solution:**
```bash
# Kill process on port 8000 (API server)
lsof -ti:8000 | xargs kill

# Kill process on port 5173 (Chat UI)
lsof -ti:5173 | xargs kill

# Or use stop script
./stop_all.sh
```

</details>

<details>
<summary><b>Models not found</b></summary>

**Solution:**
- Verify Ollama is running: `curl http://localhost:10000/api/tags`
- Check models are pulled: `ollama list`
- Verify base URL in `config/settings.py`

</details>

<details>
<summary><b>MongoDB connection errors</b></summary>

**Solution:**
```bash
# Check if running
docker ps | grep mongo

# View logs
docker logs mongo-chatui

# Restart
docker start mongo-chatui
```

</details>

<details>
<summary><b>Chat UI shows wrong model</b></summary>

**Solution:**
- Verify `.env.local` exists in Chat UI directory
- Check it has correct `OPENAI_BASE_URL=http://localhost:8000/v1`
- Restart Chat UI after changes

</details>

<details>
<summary><b>Import errors</b></summary>

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify Python version (3.10+)
python --version
```

</details>

### Service Status Checks

```bash
# MongoDB
docker ps | grep mongo

# API Server
curl http://localhost:8000/

# Chat UI
curl http://localhost:5173/

# View logs
tail -f /tmp/api_server.log    # API server
tail -f /tmp/chat_ui.log       # Chat UI
```

---

## 📊 Startup Scripts Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `start_all.sh` | Launch everything | `./start_all.sh` |
| `stop_all.sh` | Stop all services | `./stop_all.sh` |
| `start_mongo.sh` | Start MongoDB only | `./start_mongo.sh` |
| `start_api.sh` | Start API server only | `./start_api.sh` |

---

## 🎯 How It Works (Detailed)

### 1. Task Analysis
The Model Router analyzes the task for:
- **Length** and complexity indicators
- **Keywords** (coding, multilingual, urgent, etc.)
- **Context** from previous interactions

### 2. Model Selection
Based on analysis, selects optimal model:
- **phi3**: Fast, simple tasks, urgent requests
- **gemma3**: Coding tasks, general analysis
- **qwen3**: Complex tasks, multilingual needs

### 3. Multi-Agent Workflow
Each task goes through:
1. **Planner** → Breaks down into actionable steps
2. **Researcher** → Gathers relevant information
3. **Executor** → Performs the task
4. **Critic** → Reviews and evaluates output

### 4. Memory & Context
- Conversations stored in vector database
- Relevant past conversations retrieved automatically
- Context included in agent prompts

### 5. Feedback Integration
- User feedback recorded and analyzed
- Model performance tracked
- Selection improved based on ratings

---

## 🔐 Error Handling

Custom exceptions for better debugging:

- `MultiAgentError` - Base exception class
- `ModelSelectionError` - Model selection failures
- `AgentExecutionError` - Agent execution failures
- `WorkflowError` - Workflow execution failures

---

## 📝 Logging

Configure logging:

```python
from utils.logging import setup_logging
import logging

logger = setup_logging(level=logging.INFO, log_file="app.log")
```

---

## 🚧 Future Enhancements

- [ ] Additional specialized agents (Code Reviewer, Documentation Agent)
- [ ] Speculative execution (parallel model runs)
- [ ] Remote model support (OpenAI, Anthropic, etc.)
- [ ] Human-in-the-loop capabilities
- [ ] Workflow checkpointing for long tasks

---

## 📄 License

This project is provided as-is for educational and development purposes.

---

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - LLM application framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent workflows
- [Hugging Face Chat UI](https://github.com/huggingface/chat-ui) - Beautiful chat interface
- [Ollama](https://ollama.ai/) - Local LLM inference

---

**Made with ❤️ using LangChain and LangGraph**
