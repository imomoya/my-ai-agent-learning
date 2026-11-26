from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

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

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma.from_texts(
    texts=all_chunks,
    embedding=embeddings,
    ids=[f"chunk-{i}" for i in range(len(all_chunks))],
)
results = vectorstore.similarity_search("agent能自己办事吗", k=1)
print(results[0].page_content)