# Qwen3 Embedding Dimension Mismatch - Complete Solution Guide

## 🔍 Problem Analysis

**Error Message:**
```
Failed to generate embedding for text 0: 500: Expected 2560 dimensions, got 1024
```

**Root Cause:**
You have a configuration mismatch between your files and the actual Ollama model:

1. **Configuration Files Expect:** 2560 dimensions (Qwen3-Embedding-4B)
   - [`qdrantsetup-qwen3-4b.py`](qdrantsetup-qwen3-4b.py:49) - Line 49: `self.vector_size = 2560`
   - [`qwen3-4b-api.py`](qwen3-4b-api.py:25) - Line 25: `"dimensions": 2560`

2. **Ollama is Returning:** 1024 dimensions (Qwen3-Embedding-0.6B)
   - This means you're running the **0.6B model** instead of the **4B model**

## 📊 Qwen3-Embedding Model Comparison

| Model | Dimensions | Size | Best For |
|-------|-----------|------|----------|
| **Qwen3-Embedding-0.6B** | 1024 | ~600MB | Fast inference, lower memory |
| **Qwen3-Embedding-4B** | 2560 | ~2.5GB | Higher accuracy, better quality |
| **Qwen3-Embedding-8B** | 4096 | ~5GB | Maximum quality |

## ✅ Solution: Setup Qwen3-Embedding-4B (2560 dimensions)

### Step 1: Download the Correct Model

```bash
# Download Qwen3-Embedding-4B with Q4_K_M quantization (recommended)
ollama pull hf.co/Qwen/Qwen3-Embedding-4B-GGUF:Q4_K_M

# Alternative: Q8_0 for higher quality (larger file)
# ollama pull hf.co/Qwen/Qwen3-Embedding-4B-GGUF:Q8_0
```

### Step 2: Optimize the Model

```bash
# Extract and optimize the GGUF model from Ollama
python optimize_gguf.py hf.co/Qwen/Qwen3-Embedding-4B-GGUF:Q4_K_M qwen3-embedding
```

This will:
- Extract the GGUF file from Ollama's blob storage
- Create an optimized Modelfile with Qwen developer recommendations
- Register the model as `qwen3-embedding` in Ollama
- Generate instruction-aware templates for different tasks

### Step 3: Verify the Model

```bash
# Check that the model is registered
ollama list | grep qwen3-embedding

# Test the model dimensions
curl http://localhost:11434/api/embeddings -d '{
  "model": "qwen3-embedding",
  "prompt": "test"
}' | jq '.embedding | length'
```

**Expected output:** `2560` (for 4B model)

### Step 4: Setup Qdrant Vector Database

```bash
# Run the setup script (or use the automated script)
./setup-4b-step3.sh

# Or manually:
docker run -d --name qdrant \
    -p 6333:6333 \
    -e QDRANT__SERVICE__API_KEY="your-super-secret-qdrant-api-key" \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

### Step 5: Initialize Qdrant Collection

```bash
# This will create the collection with 2560 dimensions
python qdrantsetup-qwen3-4b.py
```

### Step 6: Start the API Server

```bash
# Start the OpenAI-compatible API wrapper
python qwen3-4b-api.py
```

The API will be available at `http://localhost:8000`

### Step 7: Verify Everything Works

```bash
# Test the complete pipeline
curl -X POST http://localhost:8000/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "input": "test embedding",
    "model": "qwen3-embedding",
    "encoding_format": "float"
  }' | jq '.data[0].embedding | length'
```

**Expected output:** `2560`

## 🔧 Configuration Files Reference

### For Qwen3-Embedding-4B (2560 dimensions):

**Files to use:**
- ✅ [`qwen3-4b-api.py`](qwen3-4b-api.py) - API wrapper configured for 2560 dimensions
- ✅ [`qdrantsetup-qwen3-4b.py`](qdrantsetup-qwen3-4b.py) - Qdrant setup for 2560 dimensions

**Model Configuration in `qwen3-4b-api.py`:**
```python
MODEL_CONFIG = {
    "model_name": "qwen3-embedding",
    "dimensions": 2560,  # 4B model dimensions
    "max_context_length": 32768,
    "available_dimensions": [512, 768, 1024, 2560],  # MRL support
}
```

### For Qwen3-Embedding-0.6B (1024 dimensions):

**Files to use:**
- ✅ [`qwen3-api.py`](qwen3-api.py) - API wrapper configured for 1024 dimensions
- ✅ [`qdrantsetup.py`](qdrantsetup.py) - Qdrant setup for 1024 dimensions

## 🎯 Qwen3-Embedding Advanced Features

### 1. Instruction-Aware Embedding (1-5% Performance Improvement)

```python
# Use task-specific instructions
response = requests.post("http://localhost:8000/v1/embeddings", json={
    "input": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    "model": "qwen3-embedding",
    "task": "code_search",  # Optimized for code
    "encoding_format": "float"
})
```

**Available tasks:**
- `text_search` - General semantic search (default)
- `code_search` - Code and programming tasks
- `document_retrieval` - Document and text retrieval
- `question_answering` - Q&A systems
- `clustering` - Text clustering and categorization
- `classification` - Classification tasks
- `similarity` - Semantic similarity comparison

### 2. MRL (Matryoshka Representation Learning)

Reduce dimensions while maintaining quality:

```python
# Use 1024 dimensions instead of 2560 for faster search
response = requests.post("http://localhost:8000/v1/embeddings", json={
    "input": "Your text here",
    "model": "qwen3-embedding",
    "dimensions": 1024,  # Supported: 512, 768, 1024, 2560
    "encoding_format": "float"
})
```

## 🚀 RooCode Integration

After completing the setup, configure RooCode with these settings:

```yaml
# Embeddings Provider Configuration
Provider: OpenAI-compatible
Base URL: http://localhost:8000
API Key: your-super-secret-qdrant-api-key
Model: qwen3-embedding
Embedding Dimension: 2560

# Vector Database Configuration
Qdrant URL: http://localhost:6333
Qdrant API Key: your-super-secret-qdrant-api-key
Collection Name: qwen3_embedding
```

## 🐛 Troubleshooting

### Issue: "Expected 2560 dimensions, got 1024"

**Cause:** You're running the 0.6B model instead of the 4B model.

**Solution:** Follow Steps 1-2 above to download and optimize the 4B model.

### Issue: Model not found in Ollama

```bash
# List all models
ollama list

# If qwen3-embedding is missing, re-run the optimizer
python optimize_gguf.py hf.co/Qwen/Qwen3-Embedding-4B-GGUF:Q4_K_M qwen3-embedding
```

### Issue: Qdrant collection has wrong dimensions

```bash
# Delete the existing collection and recreate it
python -c "
from qdrant_client import QdrantClient
client = QdrantClient(url='http://localhost:6333', api_key='your-super-secret-qdrant-api-key')
client.delete_collection('qwen3_embedding')
"

# Recreate with correct dimensions
python qdrantsetup-qwen3-4b.py
```

### Issue: API returns wrong dimensions

**Check the model configuration:**
```bash
curl http://localhost:8000/ | jq '.dimensions'
```

**Expected:** `2560` (for 4B model)

If incorrect, ensure you're running the correct API file:
- For 4B: `python qwen3-4b-api.py`
- For 0.6B: `python qwen3-api.py`

## 📝 Quick Reference Commands

```bash
# Check Ollama models
ollama list

# Test embedding dimensions
curl http://localhost:11434/api/embeddings -d '{"model":"qwen3-embedding","prompt":"test"}' | jq '.embedding | length'

# Check API health
curl http://localhost:8000/health

# Check Qdrant health
curl http://localhost:6333/health

# View Qdrant collection info
curl http://localhost:6333/collections/qwen3_embedding
```

## 🎉 Success Checklist

- [ ] Downloaded Qwen3-Embedding-4B model via Ollama
- [ ] Optimized model with `optimize_gguf.py`
- [ ] Model returns 2560-dimensional embeddings
- [ ] Qdrant container is running
- [ ] Qdrant collection created with 2560 dimensions
- [ ] API server running on port 8000
- [ ] API returns 2560-dimensional embeddings
- [ ] RooCode configured with correct settings

## 📚 Additional Resources

- **Qwen3-Embedding Documentation:** [HuggingFace Model Card](https://huggingface.co/Qwen/Qwen3-Embedding-4B-GGUF)
- **Ollama Documentation:** [ollama.ai/docs](https://ollama.ai/docs)
- **Qdrant Documentation:** [qdrant.tech/documentation](https://qdrant.tech/documentation)

---

**Need Help?** Check the logs:
- Ollama: `ollama logs`
- API: Check terminal where `qwen3-4b-api.py` is running
- Qdrant: `docker logs qdrant`