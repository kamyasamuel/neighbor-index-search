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

## License
MIT
