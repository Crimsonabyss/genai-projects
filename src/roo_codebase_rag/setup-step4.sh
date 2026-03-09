#!/bin/bash

# Qwen3 Embedding Setup Script
# Automates the complete setup process for RooCode integration

set -e  # Exit on any error

# Step 4: Start the API in background
echo "📦 Step 4: Starting OpenAI-compatible API..."
# The & makes the command run in the background.
python qwen3-api.py &
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

# Step 5: Setup Qdrant vector store
echo "📦 Step 5: Setting up Qdrant vector store..."
python qdrantsetup.py
echo "✅ Qdrant vector store configured"

# Step 6: Run verification tests
echo "📦 Step 6: Running verification tests..."
python test_setup.py

# Summary
echo ""
echo "🎉 Setup complete! Your Qwen3 embedding system is ready for Roo Code."
echo ""
echo "🔧 Roo Code Configuration:"
echo "   Embeddings Provider: OpenAI-compatible"
echo "   Base URL: http://localhost:8000"
echo "   API Key: your-super-secret-qdrant-api-key"
echo "   Model: qwen3"
echo "   Embedding Dimension: 1024"
echo "   Qdrant URL: http://localhost:6333"
echo "   Qdrant API Key: your-super-secret-qdrant-api-key"
echo "   Collection Name: qwen3_embedding"
echo ""
echo "🚀 Services running:"
echo "   - Qwen3 API: http://localhost:8000"
echo "   - Qdrant: http://localhost:6333"
echo "   - Ollama: http://localhost:11434"
echo ""
echo "💡 To stop the API: kill $API_PID"
echo "💡 To stop Qdrant: docker stop qdrant"
echo "💡 To restart: ./setup.sh"
