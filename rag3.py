import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


def chunk_text(text, size=200, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

def retrieve(question, chunks):
    best = None
    best_score = -1
    for c in chunks:
        score = 0
        for ch in question:
            if ch in c:
                score += 1
        if score > best_score:
            best_score = score
            best = c
    return best

all_chunks = []
for name in os.listdir("knowledge"):
    if name.endswith(".txt"):
        with open(os.path.join("knowledge", name), encoding="utf-8") as f:
            text = f.read()
        all_chunks.extend(chunk_text(text))
        
question = "agent由哪几部分组成"
best=retrieve(question,all_chunks)

messages = [
    {"role": "system", "content": "你是一个问答助手，只根据下面提供的资料回答问题，不要用自己的知识编造。"},
    {"role": "user", "content": f"资料：{best}\n问题：{question}"},
]

response = client.chat.completions.create(model="deepseek-flash", messages=messages)
print(response.choices[0].message.content)