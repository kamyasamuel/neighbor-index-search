# Neighbor Index Search

A Python project for building a ChromaDB-like index that retrieves a search hit and its surrounding collections for context generation and similarity proximity. Embeddings are generated using a local Ollama model.

## Features
- Indexes collections and enables fast similarity search
- Retrieves 5 collections before and after a search hit for context
- Uses Ollama for local embedding generation

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start Ollama and ensure the embedding model is available (e.g., `all-minilm:latest`).
   ```bash
   On Linux:
   curl -fsSL https://ollama.com/install.sh | sh
   ollama pull all-minilm
   ```
3. Run the indexing and search script:
   ```bash
   python -m neighbor_index_search.cli --help
   ```

## API Usage

Start the API server:
```bash
bash start_api.sh
```

### Add a single document
```bash
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"id": "doc1", "text": "This is a test document."}'
```

### Add multiple documents
```bash
curl -X POST "http://localhost:8000/add-batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"ids": ["doc2", "doc3"], "texts": ["Text for doc2", "Text for doc3"]}'
```

### Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"query": "test", "top_k": 1, "context_window": 5}'
```

### Generate API Key for a User and Collection
```bash
curl -X POST "http://localhost:8000/generate-api-key" \
  -H "Content-Type: application/json" \
  -d '{"user": "alice", "collection": "alice_collection"}'
```

The response will include an `api_key` and the associated `collection`. Use this API key in the `X-API-Key` header for all other requests.

### Health check
```bash
curl http://localhost:8000/health
```

### Upload a document or zip file
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "user=alice" \
  -F "collection=alice_collection" \
  -F "file=@/path/to/your/document.pdf"
```

You can also upload a zip file containing multiple documents:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "user=alice" \
  -F "collection=alice_collection" \
  -F "file=@/path/to/your/documents.zip"
```

### Index all uploaded files for a user/collection
```bash
curl -X POST "http://localhost:8000/index-uploads" \
  -H "X-API-Key: YOUR_API_KEY" \
  -F "user=alice" \
  -F "collection=alice_collection"
```

## License
MIT
