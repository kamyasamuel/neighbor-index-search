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
  -H "X-API-Key: 8e2b7c1a-2f4e-4b7a-9c3d-1a5e2f7b9c8d" \
  -d '{"id": "doc1", "text": "This is a test document."}'
```

### Add multiple documents
```bash
curl -X POST "http://localhost:8000/add-batch" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 8e2b7c1a-2f4e-4b7a-9c3d-1a5e2f7b9c8d" \
  -d '{"ids": ["doc2", "doc3"], "texts": ["Text for doc2", "Text for doc3"]}'
```

### Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: 8e2b7c1a-2f4e-4b7a-9c3d-1a5e2f7b9c8d" \
  -d '{"query": "test", "top_k": 1, "context_window": 5}'
```

### Health check
```bash
curl http://localhost:8000/health
```

## License
MIT
