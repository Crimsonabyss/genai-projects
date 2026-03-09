#!/bin/bash

# Qwen3 Embedding Setup Script
# Automates the complete setup process for RooCode integration

set -e  # Exit on any error


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
