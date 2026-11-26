import os
from langchain_openai import ChatOpenAI
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

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

llm = ChatOpenAI(
    model="deepseek-flash",
    base_url="https://api.deepseek.com",
    openai_api_key=os.environ.get("DEEPSEEK_API_KEY"),
)

docs = vectorstore.similarity_search("agent能自己办事吗", k=1)
best = docs[0].page_content

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个问答助手，只根据下面提供的资料回答问题，不要用自己的知识编造。"),
    ("human", "资料：{context}\n问题：{question}"),
])
chain = prompt | llm

response = chain.invoke({"context": best, "question": "agent能自己办事吗"})
print(response.content)