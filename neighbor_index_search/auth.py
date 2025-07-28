import secrets
from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("NEIGHBOR_INDEX_DB", "neighbor_index_db")
COLLECTION = "api_keys"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
api_keys_col = db[COLLECTION]

def generate_api_key():
    return secrets.token_hex(32)

def create_user_api_key(user: str, collection_name: str):
    api_key = generate_api_key()
    api_keys_col.insert_one({
        "user": user,
        "api_key": api_key,
        "collection": collection_name
    })
    return api_key

def get_collection_for_api_key(api_key: str):
    doc = api_keys_col.find_one({"api_key": api_key})
    if doc:
        return doc["collection"]
    return None
