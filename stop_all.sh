#!/bin/bash
# Script to stop all services

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}Stopping services...${NC}\n"

# Stop API server
echo -e "${YELLOW}Stopping API server...${NC}"
pkill -f "python api_server.py" || pkill -f "uvicorn api_server:app" || true
sleep 1
if ! pgrep -f "api_server" > /dev/null; then
    echo -e "${GREEN}✅ API server stopped${NC}"
else
    echo -e "${RED}⚠️  API server may still be running${NC}"
fi

# Stop Chat UI
echo -e "${YELLOW}Stopping Chat UI...${NC}"
pkill -f "vite dev" || pkill -f "npm run dev" || true
sleep 1
if ! pgrep -f "vite dev" > /dev/null; then
    echo -e "${GREEN}✅ Chat UI stopped${NC}"
else
    echo -e "${RED}⚠️  Chat UI may still be running${NC}"
fi

# Optionally stop MongoDB (commented out - usually you want to keep it running)
# echo -e "${YELLOW}Stopping MongoDB...${NC}"
# docker stop mongo-chatui 2>/dev/null && echo -e "${GREEN}✅ MongoDB stopped${NC}" || echo -e "${YELLOW}MongoDB container not running${NC}"

echo ""
echo -e "${GREEN}Done!${NC}"
echo -e "${YELLOW}Note: MongoDB container is still running.${NC}"
echo -e "${YELLOW}To stop it: docker stop mongo-chatui${NC}"

