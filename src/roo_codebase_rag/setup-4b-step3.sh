#!/bin/bash

# Step 3: Setup Qdrant
echo "📦 Step 3: Setting up Qdrant vector database..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running! Please start Docker first."
    exit 1
fi

# Stop existing Qdrant container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "qdrant"; then
    echo "Stopping existing Qdrant container..."
    docker stop qdrant || true
    docker rm qdrant || true
fi

# Start new Qdrant container
echo "Starting Qdrant container..."
docker run -d --name qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -e QDRANT__SERVICE__API_KEY="your-super-secret-qdrant-api-key" \
    -v "$(pwd)/qdrant_storage:/qdrant/storage" \
    qdrant/qdrant

# Wait for Qdrant to be ready
echo "Waiting for Qdrant to start..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        echo "✅ Qdrant is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Qdrant failed to start"
        exit 1
    fi
    sleep 2
done

