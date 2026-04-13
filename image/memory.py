import faiss
import numpy as np
from openai import OpenAI

client = OpenAI()

DIM = 1536

# FAISS index (L2 distance)
index = faiss.IndexFlatL2(DIM)
memory_store = []


# ---------------------------
# EMBEDDING FUNCTION
# ---------------------------
def embed(text: str):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    vec = np.array(res.data[0].embedding, dtype="float32")

    # Normalize (VERY IMPORTANT for better similarity search)
    vec = vec / np.linalg.norm(vec)

    return vec


# ---------------------------
# ADD MEMORY
# ---------------------------
def add_memory(text: str):
    vec = embed(text)

    index.add(np.array([vec]))  # shape (1, DIM)
    memory_store.append(text)


# ---------------------------
# SEARCH MEMORY (RAG)
# ---------------------------
def search_memory(query: str, k: int = 3):

    # ❗ SAFE GUARD
    if index.ntotal == 0:
        return []

    q = embed(query)
    q = np.array([q])  # shape (1, DIM)

    distances, indices = index.search(q, k)

    results = []
    for i in indices[0]:
        if 0 <= i < len(memory_store):
            results.append(memory_store[i])

    return results