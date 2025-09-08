from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

query = "How do I apply for leave?"
embedding = model.encode([query])

print("Query embedding shape:", embedding.shape)