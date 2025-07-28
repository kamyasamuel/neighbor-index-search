from fastapi import FastAPI, HTTPException, Request, Depends, UploadFile, File, Form
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os
import shutil
import zipfile
from fastapi import UploadFile, File, Form, Depends
import shutil
import zipfile
from .indexer import NeighborIndex
from .auth import create_user_api_key, get_collection_for_api_key

api_key_header = APIKeyHeader(name="X-API-Key")
app = FastAPI()

UPLOADS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
os.makedirs(UPLOADS_DIR, exist_ok=True)

# --- Upload and Index Endpoints ---
load_dotenv()

api_key_header = APIKeyHeader(name="X-API-Key")

index_cache = {}

def get_index_for_collection(collection_name):
    if collection_name not in index_cache:
        index_cache[collection_name] = NeighborIndex(collection_name=collection_name)
    return index_cache[collection_name]

# Dependency for API key verification and collection selection
def verify_api_key_and_get_collection(api_key: str = Depends(api_key_header)):
    collection = get_collection_for_api_key(api_key)
    if not collection:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return collection

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


@app.post("/add")
def add_doc(req: AddDocRequest, collection=Depends(verify_api_key_and_get_collection)):
    index = get_index_for_collection(collection)
    index.add_collection(req.id, req.text)
    return {"status": "success", "added": req.id}


@app.post("/add-batch")
def add_docs(req: AddDocsRequest, collection=Depends(verify_api_key_and_get_collection)):
    index = get_index_for_collection(collection)
    index.add_collection(req.ids, req.texts)
    return {"status": "success", "added": req.ids}


@app.post("/search")
def search(req: SearchRequest, collection=Depends(verify_api_key_and_get_collection)):
    index = get_index_for_collection(collection)
    results = index.search(req.query, top_k=req.top_k, context_window=req.context_window)
    return {"results": results}
class APIKeyGenRequest(BaseModel):
    user: str
    collection: str

@app.post("/generate-api-key")
def generate_api_key(req: APIKeyGenRequest):
    api_key = create_user_api_key(req.user, req.collection)
    return {"api_key": api_key, "collection": req.collection}

@app.post("/upload")
def upload_file_api(
    file: UploadFile = File(...),
    user: str = Form(...),
    collection: str = Form(...),
    api_key: str = Depends(api_key_header)
):
    # API key must be valid for this user/collection
    stored_collection = get_collection_for_api_key(api_key)
    if stored_collection != collection:
        raise HTTPException(status_code=403, detail="Invalid API Key or collection")
    user_dir = os.path.join(UPLOADS_DIR, user, collection)
    os.makedirs(user_dir, exist_ok=True)
    if not file.filename or not isinstance(file.filename, str):
        raise HTTPException(status_code=400, detail="No filename provided")
    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # If zip, extract contents
    if file.filename and file.filename.lower().endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(user_dir)
    return {"status": "uploaded", "filename": file.filename}

@app.post("/index-uploads")
def index_uploaded_files_api(
    user: str = Form(...),
    collection: str = Form(...),
    api_key: str = Depends(api_key_header)
):
    # API key must be valid for this user/collection
    stored_collection = get_collection_for_api_key(api_key)
    if stored_collection != collection:
        raise HTTPException(status_code=403, detail="Invalid API Key or collection")
    user_dir = os.path.join(UPLOADS_DIR, user, collection)
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="No uploads found for this user/collection")
    # Find all files (ignore directories)
    files = [f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f))]
    if not files:
        return {"status": "no files to index"}
    index = get_index_for_collection(collection)
    from neighbor_index_search.cli import text_extractor, split_text_into_chunks
    for file_name in files:
        file_path = os.path.join(user_dir, file_name)
        text = text_extractor(user_dir, file_name)
        chunks = split_text_into_chunks(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_name}_chunk_{i}"
            index.add_collection(chunk_id, chunk)
    return {"status": "indexed", "files": files}

@app.post("/upload")
def upload_file(
    file: UploadFile = File(...),
    user: str = Form(...),
    collection: str = Form(...),
    api_key: str = Depends(api_key_header)
):
    # API key must be valid for this user/collection
    stored_collection = get_collection_for_api_key(api_key)
    if stored_collection != collection:
        raise HTTPException(status_code=403, detail="Invalid API Key or collection")
    user_dir = os.path.join(UPLOADS_DIR, user, collection)
    os.makedirs(user_dir, exist_ok=True)
    if not file.filename or not isinstance(file.filename, str):
        raise HTTPException(status_code=400, detail="No filename provided")
    file_path = os.path.join(user_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # If zip, extract contents
    if file.filename.lower().endswith('.zip'):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(user_dir)
    return {"status": "uploaded", "filename": file.filename}

@app.post("/index-uploads")
def index_uploaded_files(
    user: str = Form(...),
    collection: str = Form(...),
    api_key: str = Depends(api_key_header)
):
    # API key must be valid for this user/collection
    stored_collection = get_collection_for_api_key(api_key)
    if stored_collection != collection:
        raise HTTPException(status_code=403, detail="Invalid API Key or collection")
    user_dir = os.path.join(UPLOADS_DIR, user, collection)
    if not os.path.exists(user_dir):
        raise HTTPException(status_code=404, detail="No uploads found for this user/collection")
    # Find all files (ignore directories)
    files = [f for f in os.listdir(user_dir) if os.path.isfile(os.path.join(user_dir, f))]
    if not files:
        return {"status": "no files to index"}
    index = get_index_for_collection(collection)
    from neighbor_index_search.cli import text_extractor, split_text_into_chunks
    for file_name in files:
        file_path = os.path.join(user_dir, file_name)
        text = text_extractor(user_dir, file_name)
        chunks = split_text_into_chunks(text)
        for i, chunk in enumerate(chunks):
            chunk_id = f"{file_name}_chunk_{i}"
            index.add_collection(chunk_id, chunk)
    return {"status": "indexed", "files": files}

@app.get("/health")
def health():
    return {"status": "ok"}
