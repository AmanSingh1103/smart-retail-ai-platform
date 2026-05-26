from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

KB_PATH = "app/rag/retail_knowledge.txt"

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def load_documents():
    if not os.path.exists(KB_PATH):
        return []

    with open(KB_PATH, "r", encoding="utf-8") as file:
        text = file.read()

    chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]
    return chunks

documents = load_documents()

if documents:
    document_embeddings = model.encode(documents)
else:
    document_embeddings = []

def search_knowledge_base(query: str, top_k: int = 2):
    if not documents:
        return []

    query_embedding = model.encode([query])
    scores = cosine_similarity(query_embedding, document_embeddings)[0]

    ranked_indexes = scores.argsort()[::-1][:top_k]

    results = []
    for index in ranked_indexes:
        results.append({
            "content": documents[index],
            "score": float(scores[index])
        })

    return results