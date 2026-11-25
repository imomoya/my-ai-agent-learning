import os
import chromadb
from openai import OpenAI
from sentence_transformers import SentenceTransformer

client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

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

chroma_client = chromadb.Client()
collection = chroma_client.create_collection("knowledge")
ids = [f"chunk-{i}" for i in range(len(all_chunks))]
collection.add(
    ids=ids,
    documents=all_chunks,
    embeddings=[model.encode(c).tolist() for c in all_chunks],
)

question = "agent能自己办事吗"
qv = model.encode(question).tolist()
result = collection.query(query_embeddings=[qv], n_results=1)
best = result["documents"][0][0]

messages = [
    {"role": "system", "content": "你是一个问答助手，只根据下面提供的资料回答问题，不要用自己的知识编造。"},
    {"role": "user", "content": f"资料：{best}\n问题：{question}"},
]
response = client.chat.completions.create(model="deepseek-flash", messages=messages)
print(response.choices[0].message.content)