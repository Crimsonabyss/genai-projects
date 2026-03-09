#!/bin/bash

# Qwen3 Embedding Setup Script
# Automates the complete setup process for RooCode integration

set -e  # Exit on any error

# Step 4: Start the API in background
echo "📦 Step 4: Starting OpenAI-compatible API..."
# The & makes the command run in the background.
python qwen3-4b-api.py &
API_PID=$!
echo $API_PID

# Wait for API to be ready
echo "Waiting for API to start..."
for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is ready"
        break
    fi
    if [ $i -eq 20 ]; then
        echo "❌ API failed to start"
        kill $API_PID || true
        exit 1
    fi
    sleep 2
done
