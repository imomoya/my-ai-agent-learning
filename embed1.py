import math
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")

def cosine(a, b):
    dot = 0
    na = 0
    nb = 0
    for i, x in enumerate(a):
        dot += x * b[i]
        na += x * x
        nb += b[i] * b[i]
    return dot / (math.sqrt(na) * math.sqrt(nb))

s1 = "agent是可以自主完成用户需求的智能体"
s2 = "agent能自己帮用户把事情办完"
s3 = "mysql是由表格组成的数据库"
v1 = model.encode(s1)
v2 = model.encode(s2)
v3 = model.encode(s3)
print("向量长度：", len(v1))
print("s1 和 s2 的相似度：", cosine(v1, v2))
print("s1 和 s3 的相似度：", cosine(v1, v3))