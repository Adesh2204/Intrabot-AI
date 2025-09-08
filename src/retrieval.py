# Intrabot-Ai/src/retrieval.py
from sentence_transformers import SentenceTransformer
import chromadb

MODEL_NAME = "all-MiniLM-L6-v2"
CHROMA_DIR = "offline-org-chatbot/.chromadb"
COLLECTION_NAME = "intrabot_docs"
TOP_K = 4

def search(query_text, top_k=TOP_K):
    # load embedding model
    model = SentenceTransformer(MODEL_NAME)

    # open ChromaDB (same persist dir used during ingest)
    client = chromadb.PersistentClient(path=CHROMA_DIR)
    try:
        collection = client.get_collection(COLLECTION_NAME)
    except Exception:
        # fallback in case collection isn't found
        collection = client.get_or_create_collection(COLLECTION_NAME)

    # embed query
    q_emb = model.encode([query_text])[0].tolist()

    # run vector search
    results = collection.query(query_embeddings=[q_emb], n_results=top_k)
    return results

if __name__ == "__main__":
    q = input("Enter a question (e.g. 'How do I apply for leave?'): ").strip()
    if not q:
        print("Empty query. Exiting.")
        raise SystemExit(0)
    res = search(q, top_k=TOP_K)
    # format and print results
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    if not docs:
        print("No results found. Did you run the ingest step?")
    else:
        print(f"\nTop {len(docs)} results for: {q}\n")
        for i, doc in enumerate(docs):
            meta = metas[i] if i < len(metas) else {}
            dist = dists[i] if i < len(dists) else None
            print("-" * 60)
            print(f"Result #{i+1} | source = {meta.get('source')} | distance = {dist}")
            print()
            print(doc)
            print()