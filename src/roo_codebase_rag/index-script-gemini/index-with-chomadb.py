import argparse
import os
import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
import ollama

# ==========================================
# 1. Custom Embedding Function (2560 dims)
# ==========================================
class QwenEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="Qwen3-Embedding-4B-GGUF:Q4_K_M"):
        self.model_name = model_name
        self.target_dim = 2560 

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = []
        # Batch processing is often safer, but for simplicity we loop here.
        # Ideally, you might want to batch these calls if processing thousands of files.
        for text in input:
            response = ollama.embeddings(model=self.model_name, prompt=text)
            vector = response["embedding"]
            embeddings.append(vector)
        return embeddings

# ==========================================
# 2. File Processing Helper
# ==========================================
def get_file_contents(paths):
    """
    Generator that yields (file_path, content) for all valid text files
    found in the provided list of paths (files or directories).
    """
    for path in paths:
        if os.path.isfile(path):
            # Process single file
            files_to_process = [path]
        elif os.path.isdir(path):
            # Process directory recursively
            files_to_process = []
            for root, _, files in os.walk(path):
                for file in files:
                    files_to_process.append(os.path.join(root, file))
        else:
            print(f"Skipping invalid path: {path}")
            continue

        for file_path in files_to_process:
            try:
                # Attempt to read as UTF-8. Skips binary files automatically.
                with open(file_path, 'r', encoding='utf-8', errors='strict') as f:
                    content = f.read()
                    # Skip empty files or files that are just whitespace
                    if content.strip():
                        yield file_path, content
            except UnicodeDecodeError:
                print(f"Skipping binary or non-utf8 file: {file_path}")
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

# ==========================================
# 3. Main Execution
# ==========================================
def main():
    # --- Setup Argparse ---
    parser = argparse.ArgumentParser(description="Index files or directories into ChromaDB using Qwen Embeddings.")
    parser.add_argument(
        "inputs", 
        nargs="+", 
        help="One or more files or directories to index."
    )
    parser.add_argument(
        "--db-path", 
        default="./my_chroma_db_2560", 
        help="Path to store the ChromaDB."
    )
    parser.add_argument(
        "--collection", 
        default="codebase_index", 
        help="Name of the collection."
    )
    
    args = parser.parse_args()

    # --- Initialize Chroma ---
    print(f"Opening database at: {args.db_path}")
    client = chromadb.PersistentClient(path=args.db_path)
    
    collection = client.get_or_create_collection(
        name=args.collection,
        embedding_function=QwenEmbeddingFunction()
    )

    # --- Process Files ---
    documents = []
    metadatas = []
    ids = []
    
    print("🔍 Scanning files...")
    
    for file_path, content in get_file_contents(args.inputs):
        documents.append(content)
        metadatas.append({"source": file_path})
        # Use file path as unique ID. 
        # NOTE: If you re-index the same file, Chroma will update the existing entry.
        ids.append(file_path)
        print(f"   -> Found: {file_path}")

    if not documents:
        print("No valid text files found to index.")
        return

    # --- Add to Database ---
    print(f"Generating embeddings for {len(documents)} files... (This may take a moment)")
    
    # Add in batches to avoid hitting API/Memory limits if list is huge
    BATCH_SIZE = 100
    for i in range(0, len(documents), BATCH_SIZE):
        batch_end = i + BATCH_SIZE
        print(f"   Processing batch {i} to {min(batch_end, len(documents))}...")
        collection.add(
            documents=documents[i:batch_end],
            metadatas=metadatas[i:batch_end],
            ids=ids[i:batch_end]
        )

    print(f"\nSuccess! Indexed {collection.count()} documents total in collection '{args.collection}'.")

if __name__ == "__main__":
    main()

