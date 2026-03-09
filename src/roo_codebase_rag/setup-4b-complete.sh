#!/bin/bash

# Qwen3-Embedding-4B Complete Setup Script
# Automates the entire setup process for RooCode integration with 2560-dimensional embeddings

set -e  # Exit on any error

echo "🚀 Qwen3-Embedding-4B Complete Setup for RooCode"
echo "=================================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed!"
    echo "Please install Ollama from: https://ollama.ai"
    exit 1
fi
print_status "Ollama is installed"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    echo "Please install Docker from: https://docker.com"
    exit 1
fi
print_status "Docker is installed"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running!"
    echo "Please start Docker and try again"
    exit 1
fi
print_status "Docker is running"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    exit 1
fi
print_status "Python 3 is installed"

echo ""

# Step 1: Download Qwen3-Embedding-4B model
echo "📥 Step 1: Downloading Qwen3-Embedding-4B model..."
echo "This may take a few minutes depending on your internet connection..."

# Check if model already exists
if ollama list | grep -q "hf.co/Qwen/Qwen3-Embedding-4B-GGUF:Q4_K_M"; then
    print_warning "Model already downloaded, skipping..."
else
    ollama pull hf.co/Qwen/Qwen3-Embedding-4B-GGUF:Q4_K_M
    if [ $? -eq 0 ]; then
        print_status "Model downloaded successfully"
    else
        print_error "Failed to download model"
        exit 1
    fi
fi

echo ""

# Step 2: Optimize the model
echo "🔧 Step 2: Optimizing model for embedding-only usage..."

if [ -f "qwen3-embedding.gguf" ]; then
    print_warning "Optimized model already exists, skipping..."
else
    python3 optimize_gguf.py "hf.co/Qwen/Qwen3-Embedding-4B-GGUF:Q4_K_M" "qwen3-embedding"
    if [ $? -eq 0 ]; then
        print_status "Model optimized successfully"
    else
        print_error "Failed to optimize model"
        exit 1
    fi
fi

echo ""

# Step 3: Verify model dimensions
echo "🔍 Step 3: Verifying model dimensions..."

# Start Ollama if not running (it should be running already)
sleep 2

# Test the model
DIMENSIONS=$(curl -s http://localhost:11434/api/embeddings -d '{"model":"qwen3-embedding","prompt":"test"}' | python3 -c "import sys, json; print(len(json.load(sys.stdin)['embedding']))" 2>/dev/null)

if [ "$DIMENSIONS" = "2560" ]; then
    print_status "Model returns correct dimensions: 2560"
else
    print_error "Model returns incorrect dimensions: $DIMENSIONS (expected 2560)"
    print_warning "You may need to re-run the optimization step"
    exit 1
fi

echo ""

# Step 4: Install Python dependencies
echo "📦 Step 4: Installing Python dependencies..."

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt -q
    print_status "Dependencies installed"
else
    print_warning "requirements.txt not found, skipping..."
fi

echo ""

# Step 5: Setup Qdrant
echo "🗄️  Step 5: Setting up Qdrant vector database..."

# Stop existing Qdrant container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "qdrant"; then
    print_info "Stopping existing Qdrant container..."
    docker stop qdrant >/dev/null 2>&1 || true
    docker rm qdrant >/dev/null 2>&1 || true
fi

# Start new Qdrant container
print_info "Starting Qdrant container..."
docker run -d --name qdrant \
    -p 6333:6333 \
    -p 6334:6334 \
    -e QDRANT__SERVICE__API_KEY="your-super-secret-qdrant-api-key" \
    -v "$(pwd)/qdrant_storage:/qdrant/storage" \
    qdrant/qdrant >/dev/null 2>&1

# Wait for Qdrant to be ready
print_info "Waiting for Qdrant to start..."
for i in {1..30}; do
    if curl -s http://localhost:6333/health > /dev/null 2>&1; then
        print_status "Qdrant is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Qdrant failed to start"
        exit 1
    fi
    sleep 2
done

echo ""

# Step 6: Initialize Qdrant collection
echo "📊 Step 6: Initializing Qdrant collection with 2560 dimensions..."

python3 qdrantsetup-qwen3-4b.py
if [ $? -eq 0 ]; then
    print_status "Qdrant collection initialized"
else
    print_error "Failed to initialize Qdrant collection"
    exit 1
fi

echo ""

# Step 7: Start the API server (in background)
echo "🌐 Step 7: Starting API server..."

# Check if API is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "API server already running on port 8000"
else
    print_info "Starting API server in background..."
    nohup python3 qwen3-4b-api.py > api.log 2>&1 &
    API_PID=$!
    
    # Wait for API to be ready
    sleep 3
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "API server started (PID: $API_PID)"
        echo "   Logs: tail -f api.log"
    else
        print_error "API server failed to start"
        print_info "Check api.log for details"
        exit 1
    fi
fi

echo ""

# Step 8: Verify complete setup
echo "🧪 Step 8: Verifying complete setup..."

# Test API dimensions
API_DIMENSIONS=$(curl -s -X POST http://localhost:8000/v1/embeddings \
    -H "Content-Type: application/json" \
    -d '{"input":"test","model":"qwen3-embedding","encoding_format":"float"}' \
    | python3 -c "import sys, json; print(len(json.load(sys.stdin)['data'][0]['embedding']))" 2>/dev/null)

if [ "$API_DIMENSIONS" = "2560" ]; then
    print_status "API returns correct dimensions: 2560"
else
    print_error "API returns incorrect dimensions: $API_DIMENSIONS"
    exit 1
fi

# Check Qdrant collection
QDRANT_DIMENSIONS=$(curl -s http://localhost:6333/collections/qwen3_embedding \
    | python3 -c "import sys, json; print(json.load(sys.stdin)['result']['config']['params']['vectors']['size'])" 2>/dev/null)

if [ "$QDRANT_DIMENSIONS" = "2560" ]; then
    print_status "Qdrant collection configured for 2560 dimensions"
else
    print_error "Qdrant collection has incorrect dimensions: $QDRANT_DIMENSIONS"
    exit 1
fi

echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "📊 Configuration Summary:"
echo "   • Model: Qwen3-Embedding-4B (Q4_K_M)"
echo "   • Dimensions: 2560"
echo "   • Ollama: http://localhost:11434"
echo "   • API Server: http://localhost:8000"
echo "   • Qdrant: http://localhost:6333"
echo ""
echo "🔧 RooCode Configuration:"
echo "   Embeddings Provider: OpenAI-compatible"
echo "   Base URL: http://localhost:8000"
echo "   API Key: your-super-secret-qdrant-api-key"
echo "   Model: qwen3-embedding"
echo "   Embedding Dimension: 2560"
echo ""
echo "   Vector Database: Qdrant"
echo "   Qdrant URL: http://localhost:6333"
echo "   Qdrant API Key: your-super-secret-qdrant-api-key"
echo "   Collection Name: qwen3_embedding"
echo ""
echo "📝 Next Steps:"
echo "   1. Configure RooCode with the settings above"
echo "   2. Start indexing your codebase"
echo "   3. Check API logs: tail -f api.log"
echo ""
echo "🎯 Advanced Features:"
echo "   • Instruction-aware embedding (1-5% performance boost)"
echo "   • MRL support (512, 768, 1024, 2560 dimensions)"
echo "   • Task-specific templates (code_search, document_retrieval, etc.)"
echo ""
echo "📚 Documentation: See SOLUTION.md for detailed information"
echo ""
