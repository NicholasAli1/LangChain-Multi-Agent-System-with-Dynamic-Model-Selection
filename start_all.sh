#!/bin/bash
# Master script to start everything: MongoDB, API Server, and Chat UI

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
PROJECT_DIR="/Users/nick/Code/Python/langchain_multi_model"
CHAT_UI_DIR="/Users/nick/Code/Python/huggingfacechat"
API_PORT=8000
CHAT_UI_PORT=5173

# Cleanup function
cleanup() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    # Kill API server if running
    if [ ! -z "$API_PID" ]; then
        echo -e "${YELLOW}Stopping API server (PID: $API_PID)...${NC}"
        kill $API_PID 2>/dev/null || true
    fi
    
    # Kill Chat UI if running
    if [ ! -z "$CHAT_UI_PID" ]; then
        echo -e "${YELLOW}Stopping Chat UI (PID: $CHAT_UI_PID)...${NC}"
        kill $CHAT_UI_PID 2>/dev/null || true
    fi
    
    # Note: We don't stop MongoDB container - let user manage that
    echo -e "${GREEN}Cleanup complete!${NC}"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Starting Multi-Agent System${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Step 1: Check Docker
echo -e "${YELLOW}[1/4] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running!${NC}"
    echo -e "${YELLOW}Please start Docker Desktop and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}\n"

# Step 2: Start MongoDB
echo -e "${YELLOW}[2/4] Starting MongoDB...${NC}"
if docker ps | grep -q mongo-chatui; then
    echo -e "${GREEN}✅ MongoDB container is already running${NC}"
elif docker ps -a | grep -q mongo-chatui; then
    echo -e "${YELLOW}Starting existing MongoDB container...${NC}"
    docker start mongo-chatui > /dev/null
    sleep 2
    echo -e "${GREEN}✅ MongoDB started${NC}"
else
    echo -e "${YELLOW}Creating new MongoDB container...${NC}"
    docker run -d -p 27017:27017 --name mongo-chatui mongo:latest > /dev/null
    sleep 3
    echo -e "${GREEN}✅ MongoDB container created and started${NC}"
fi

# Verify MongoDB is ready
if ! docker ps | grep -q mongo-chatui; then
    echo -e "${RED}❌ Failed to start MongoDB${NC}"
    exit 1
fi
echo ""

# Step 3: Start API Server
echo -e "${YELLOW}[3/4] Starting API Server...${NC}"
cd "$PROJECT_DIR"

# Check if API server is already running
if curl -s http://localhost:$API_PORT/ > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  API server appears to be already running on port $API_PORT${NC}"
    echo -e "${YELLOW}   Continuing with existing server...${NC}"
else
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Start API server in background
    echo -e "${YELLOW}Starting API server on port $API_PORT...${NC}"
    python api_server.py > /tmp/api_server.log 2>&1 &
    API_PID=$!
    
    # Wait for API server to be ready
    echo -e "${YELLOW}Waiting for API server to start...${NC}"
    for i in {1..30}; do
        if curl -s http://localhost:$API_PORT/ > /dev/null 2>&1; then
            echo -e "${GREEN}✅ API server is running (PID: $API_PID)${NC}"
            echo -e "${BLUE}   API available at: http://localhost:$API_PORT${NC}"
            echo -e "${BLUE}   API docs at: http://localhost:$API_PORT/docs${NC}"
            break
        fi
        sleep 1
        if [ $i -eq 30 ]; then
            echo -e "${RED}❌ API server failed to start after 30 seconds${NC}"
            echo -e "${YELLOW}Check logs: tail -f /tmp/api_server.log${NC}"
            exit 1
        fi
    done
fi
echo ""

# Step 4: Start Chat UI
echo -e "${YELLOW}[4/4] Starting Chat UI...${NC}"
cd "$CHAT_UI_DIR"

# Check if Chat UI is already running
if curl -s http://localhost:$CHAT_UI_PORT > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Chat UI appears to be already running on port $CHAT_UI_PORT${NC}"
    echo -e "${YELLOW}   Opening browser...${NC}"
    open http://localhost:$CHAT_UI_PORT
else
    # Verify .env.local exists
    if [ ! -f ".env.local" ]; then
        echo -e "${RED}❌ .env.local file not found in Chat UI directory!${NC}"
        echo -e "${YELLOW}Creating .env.local from template...${NC}"
        cat > .env.local << 'EOF'
# MongoDB connection (required)
MONGODB_URL=mongodb://localhost:27017

# Multi-Agent API configuration
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=not-needed

# For OpenAI-compatible endpoints, Chat UI will auto-discover models from the API
# No MODELS override needed - the API server provides model list via /v1/models
EOF
        echo -e "${GREEN}✅ Created .env.local${NC}"
    fi
    
    echo -e "${YELLOW}Starting Chat UI on port $CHAT_UI_PORT...${NC}"
    npm run dev > /tmp/chat_ui.log 2>&1 &
    CHAT_UI_PID=$!
    
    # Wait for Chat UI to be ready
    echo -e "${YELLOW}Waiting for Chat UI to start...${NC}"
    for i in {1..60}; do
        if curl -s http://localhost:$CHAT_UI_PORT > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Chat UI is running (PID: $CHAT_UI_PID)${NC}"
            echo -e "${BLUE}   Chat UI available at: http://localhost:$CHAT_UI_PORT${NC}"
            sleep 2
            open http://localhost:$CHAT_UI_PORT
            break
        fi
        sleep 1
        if [ $i -eq 60 ]; then
            echo -e "${RED}❌ Chat UI failed to start after 60 seconds${NC}"
            echo -e "${YELLOW}Check logs: tail -f /tmp/chat_ui.log${NC}"
            exit 1
        fi
    done
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🚀 Everything is running!${NC}"
echo -e "${GREEN}========================================${NC}\n"
echo -e "${BLUE}Services:${NC}"
echo -e "  • MongoDB:     mongodb://localhost:27017"
echo -e "  • API Server:  http://localhost:$API_PORT"
echo -e "  • Chat UI:     http://localhost:$CHAT_UI_PORT"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}\n"

# Keep script running and show logs
echo -e "${BLUE}Monitoring services (Ctrl+C to stop)...${NC}\n"
wait

