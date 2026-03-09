#!/bin/bash

# Qwen3 Embedding Setup Script
# Automates the complete setup process for RooCode integration

set -e  # Exit on any error

# Step 5: Setup Qdrant vector store
echo "📦 Step 5: Setting up Qdrant vector store..."
python qdrantsetup-qwen3-4b.py
echo "✅ Qdrant vector store configured"
