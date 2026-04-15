import faiss
import numpy as np
from openai import OpenAI

from image.pdf_utils import chunk_text

client = OpenAI()

DIM = 1536

# ---------- PDF MEMORY ----------
pdf_index = faiss.IndexFlatL2(DIM)
pdf_store = []

# ---------- IMAGE MEMORY (optional future use) ----------
image_store = []

# ---------- EMBEDDING ----------
def embed(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(res.data[0].embedding, dtype="float32")

# ---------- PDF ADD ----------
def add_pdf_to_memory(text):
    chunks = chunk_text(text)

    for chunk in chunks:
        vec = embed(chunk)
        pdf_index.add(np.array([vec]))
        pdf_store.append(chunk)

# ---------- PDF SEARCH ----------
def search_pdf(query, k=3):
    if len(pdf_store) == 0:
        return []

    q = embed(query)
    D, I = pdf_index.search(np.array([q]), k)

    return [pdf_store[i] for i in I[0] if i < len(pdf_store)]