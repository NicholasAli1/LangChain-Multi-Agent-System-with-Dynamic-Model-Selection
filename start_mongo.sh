#!/bin/bash
# Script to start MongoDB for Chat UI

echo "Checking Docker status..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if container exists
if docker ps -a | grep -q mongo-chatui; then
    if docker ps | grep -q mongo-chatui; then
        echo "✅ MongoDB container is already running!"
        docker ps | grep mongo
    else
        echo "🔄 Starting existing MongoDB container..."
        docker start mongo-chatui
        sleep 2
        if docker ps | grep -q mongo-chatui; then
            echo "✅ MongoDB started successfully!"
        else
            echo "❌ Failed to start MongoDB container"
            exit 1
        fi
    fi
else
    echo "🆕 Creating new MongoDB container..."
    docker run -d -p 27017:27017 --name mongo-chatui mongo:latest
    sleep 3
    if docker ps | grep -q mongo-chatui; then
        echo "✅ MongoDB container created and started!"
    else
        echo "❌ Failed to create MongoDB container"
        exit 1
    fi
fi

echo ""
echo "MongoDB is ready at mongodb://localhost:27017"
echo "You can now start Chat UI!"

