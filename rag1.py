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

print("一共切出", len(all_chunks), "块")
print("第一块：", all_chunks[0])