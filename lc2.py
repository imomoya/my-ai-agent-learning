import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)

all_chunks = []
for name in os.listdir("knowledge"):
    if name.endswith(".txt"):
        with open(os.path.join("knowledge", name), encoding="utf-8") as f:
            text = f.read()
        all_chunks.extend(splitter.split_text(text))

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma.from_texts(
    texts=all_chunks,
    embedding=embeddings,
    ids=[f"chunk-{i}" for i in range(len(all_chunks))],
)
print("一共切出", len(all_chunks), "块")
results = vectorstore.similarity_search("agent能自己办事吗", k=1)
print(results[0].page_content)