import chromadb
import numpy as np
from .embedding import EmbeddingGenerator
from pprint import pprint


class NeighborIndex:
    def __init__(self, chroma_db_path="chroma_db", collection_name="default"):
        self.embedding_generator = EmbeddingGenerator()
        self.client = chromadb.PersistentClient(path=chroma_db_path)
        self.collection = self.client.get_or_create_collection(name=collection_name, embedding_function=self.embedding_generator)

    def add_collection(self, collection_ids, documents):
        self.collection.add(
            ids=collection_ids,
            documents= documents,
            embeddings=self.embedding_generator.get_embedding(documents) if isinstance(documents, list) else self.embedding_generator.get_embedding([documents])
        )

    def search(self, query, top_k=1, context_window=5):
        query_emb = np.array(self.embedding_generator.get_embedding(query), dtype=np.float32)
        # Get all embeddings and their ids from the collection
        # Get embeddings
        data = self.collection.query(query_emb)
        if not data:
            return []
        # Extract embeddings and ids from the data
        # Ensure embeddings are numpy arrays of float32
        embeddings = [self.embedding_generator.get_embedding(doc) for doc in data.get("documents") or []]
        ids = data.get("ids") or []
        # Ensure embeddings are numpy arrays of float32
        embeddings = [np.array(emb, dtype=np.float32) for emb in embeddings if emb is not None]
        similarities = []
        for i, emb in enumerate(embeddings):
            if emb is not None and emb.shape == query_emb.shape:
                sim = float(np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb)))
            else:
                sim = -1.0
            similarities.append((i, sim))
        similarities.sort(key=lambda x: x[1], reverse=True)
        results = []
        for idx, _ in similarities[:top_k]:
            start = max(0, idx - context_window)
            end = min(len(ids[0]), idx + context_window + 1)
            context_ids = [ids[0][i] for i in range(start, end)]
            context = self.collection.get(ids=context_ids) # type: ignore
            result = {
                'hit': self.collection.get(ids=[ids[0][idx]]),
                'context': context
            }
            pprint({"search_result": result})
            results.append(result)
        return results
