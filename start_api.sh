#!/bin/bash
# Start the FastAPI server for Neighbor Index Search with autoreload
export $(grep -v '^#' .env | xargs)
uvicorn neighbor_index_search.api:app --host 0.0.0.0 --port 8000 --reload
