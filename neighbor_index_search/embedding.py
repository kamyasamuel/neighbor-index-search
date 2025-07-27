import numpy as np
import ollama
from chromadb import EmbeddingFunction, Documents, Embeddings

class EmbeddingGenerator(EmbeddingFunction):
    def __init__(self, model="all-minilm:latest"):
        self.model = model
        self.dimension = None

    def __call__(self, input: Documents) -> Embeddings:
        """
        Generate an embedding for the given text using Ollama's embed function.
        """
        try:
            embedding = ollama.embed("all-minilm:latest", input).embeddings[0]
            if embedding is None:
                raise Exception("Embedding not found in Ollama's output.")
            embedding_vector = np.array(embedding, dtype=np.float32)
            if self.dimension is None:
                self.dimension = len(embedding_vector)
            return embedding_vector.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

    def get_embedding(self, text):
        """
        Generate an embedding for the given text using Ollama's embed function.
        """
        try:
            embedding = ollama.embed("all-minilm:latest", text).embeddings[0]
            if embedding is None:
                raise Exception("Embedding not found in Ollama's output.")
            embedding_vector = np.array(embedding, dtype=np.float32)
            if self.dimension is None:
                self.dimension = len(embedding_vector)
            return embedding_vector.tolist()
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise

if __name__ == "__main__":
    # Example usage
    generator = EmbeddingGenerator()
    text = "Hello, world!"
    #embedding = generator.get_embedding(text)
    #print(f"Embedding for '{text}': {embedding}")