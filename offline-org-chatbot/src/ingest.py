# Intrabot-Ai/src/ingest.py
"""
Simple ingest script:
- Reads .md/.txt files from data/
- Splits into chunks
- Embeds chunks with sentence-transformers
- Stores chunks + embeddings into a local ChromaDB collection
"""

import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

# ----- CONFIG -----
MODEL_NAME = "all-MiniLM-L6-v2"
DATA_DIR = Path("data")
CHROMA_DIR = Path(".chromadb")
COLLECTION_NAME = "intrabot_docs"
CHUNK_SIZE_WORDS = 150     # small chunk size is safe on CPU
CHUNK_OVERLAP = 30
BATCH_SIZE = 32
# -------------------

def load_text_files(data_dir=DATA_DIR):
    print(f"Looking for files in: {data_dir}")
    docs = []
    for p in sorted(data_dir.glob("*.*")):
        if p.suffix.lower() in [".md", ".txt"]:
            text = p.read_text(encoding="utf8")
            docs.append({"id": str(p), "source": p.name, "text": text})
    return docs

def chunk_text(text, chunk_size=CHUNK_SIZE_WORDS, overlap=CHUNK_OVERLAP):
    words = text.split()
    chunks = []
    i = 0
    if not words:
        return []
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def main():
    print("Running ingest for project: Intrabot-Ai")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Data directory path: {DATA_DIR.resolve()}")
    model = SentenceTransformer(MODEL_NAME)
    print(f"Loaded embedding model: {MODEL_NAME}")

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(COLLECTION_NAME)
    print(f"Using ChromaDB collection: {COLLECTION_NAME} (persist dir: {CHROMA_DIR})")

    docs = load_text_files()
    print(f"Found {len(docs)} files in {DATA_DIR}/")

    all_texts, metadatas, ids = [], [], []
    for d in docs:
        chunks = chunk_text(d["text"])
        print(f" - {d['source']} -> {len(chunks)} chunk(s)")
        for idx, c in enumerate(chunks):
            all_texts.append(c)
            metadatas.append({"source": d["source"]})
            ids.append(f"{d['source']}_chunk_{idx}")

    if not all_texts:
        print("No text chunks found. Add .md/.txt files into the data/ folder and re-run.")
        return

    print(f"Creating embeddings for {len(all_texts)} chunks (batch {BATCH_SIZE}) ...")
    embeddings = model.encode(all_texts, show_progress_bar=True, batch_size=BATCH_SIZE)

    print("Adding documents + embeddings to ChromaDB ...")
    collection.add(documents=all_texts, metadatas=metadatas, ids=ids, embeddings=embeddings.tolist())
    print("Ingest complete. ChromaDB persisted to:", CHROMA_DIR)

if __name__ == "__main__":
    main()