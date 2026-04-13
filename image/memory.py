import faiss
import numpy as np
from openai import OpenAI

client = OpenAI()

DIM = 1536
index = faiss.IndexFlatL2(DIM)
memory_store = []

def embed(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    vec = np.array(res.data[0].embedding, dtype="float32")
    vec = vec / np.linalg.norm(vec)
    return vec

def add_memory(text):
    vec = embed(text)
    index.add(np.array([vec]))
    memory_store.append(text)

def search_memory(query, k=3):
    if index.ntotal == 0:
        return []

    q = embed(query)
    q = np.array([q])

    D, I = index.search(q, k)

    return [memory_store[i] for i in I[0] if i < len(memory_store)]