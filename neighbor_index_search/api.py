from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from .indexer import NeighborIndex
import os
from typing import List
import dotenv

dotenv.load_dotenv()

API_KEY = os.getenv("NEIGHBOR_INDEX_API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

app = FastAPI()
index = NeighborIndex()

# Dependency for API key verification
def verify_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

class AddDocRequest(BaseModel):
    id: str
    text: str

class AddDocsRequest(BaseModel):
    ids: List[str]
    texts: List[str]

class SearchRequest(BaseModel):
    query: str
    top_k: int = 1
    context_window: int = 5

@app.post("/add", dependencies=[Depends(verify_api_key)])
def add_doc(req: AddDocRequest):
    index.add_collection(req.id, req.text)
    return {"status": "success", "added": req.id}

@app.post("/add-batch", dependencies=[Depends(verify_api_key)])
def add_docs(req: AddDocsRequest):
    index.add_collection(req.ids, req.texts)
    return {"status": "success", "added": req.ids}

@app.post("/search", dependencies=[Depends(verify_api_key)])
def search(req: SearchRequest):
    results = index.search(req.query, top_k=req.top_k, context_window=req.context_window)
    return {"results": results}

@app.get("/health")
def health():
    return {"status": "ok"}
