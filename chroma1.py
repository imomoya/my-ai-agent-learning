import os
import chromadb
from sentence_transformers import SentenceTransformer

def chunk_text(text, size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

all_chunks = []
for name in os.listdir("knowledge"):
    if name.endswith(".txt"):
        with open(os.path.join("knowledge", name), encoding="utf-8") as f:
            text = f.read()
        all_chunks.extend(chunk_text(text))

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
client = chromadb.Client()
collection = client.create_collection("knowledge")

ids = [f"chunk-{i}" for i in range(len(all_chunks))]
collection.add(
    ids=ids,
    documents=all_chunks,
    embeddings=[model.encode(c).tolist() for c in all_chunks],
)

question = "mysql"
qv = model.encode(question).tolist()
result = collection.query(query_embeddings=[qv], n_results=1)
print(result["documents"])