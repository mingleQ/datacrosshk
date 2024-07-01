import re
import json
import faiss
from zhipuai import ZhipuAI
import numpy as np

# 你的 API 密钥
api_key = 'd8a04c079082c2420ab790fa73b99249.WTqJ5WJqPSKjuWnH'

# 定义生成向量的函数
def get_vector(sentence):
    client = ZhipuAI(api_key=api_key) 
    response = client.embeddings.create(
        model="embedding-2",  # 填写需要调用的模型名称
        input=sentence,
    )
    emb = response.data[0].embedding
    return emb

# 读取文档内容
with open('./datacross.txt', 'r', encoding='utf-8') as file:
    document_content = file.read()

# 使用正则表达式将文档按句号和换行符切分
sentences = re.split(r'\n', document_content)

# 根据字数和句号进行段落切分
documents = []
current_doc = ""
for sentence in sentences:
    if len(current_doc) + len(sentence) > 350:
        if current_doc:
            documents.append(current_doc.strip())
        current_doc = sentence
    else:
        current_doc += sentence

if current_doc:
    documents.append(current_doc.strip())

print(f"总共有 {len(documents)} 个段落")

# 初始化Faiss索引
dimension = 1024  # 嵌入模型的输出向量维度
index = faiss.IndexFlatL2(dimension)

# 创建一个列表来存储段落内容和索引
paragraphs_with_index = []

# 将每个段落转化为向量并添加到Faiss索引
for i, document in enumerate(documents):
    vector = get_vector(document)
    index.add(np.array([vector], dtype=np.float32))
    paragraphs_with_index.append({'index': i, 'content': document})

# 保存Faiss索引到文件
faiss.write_index(index, 'faiss_index.index')

# 保存段落内容和索引到JSON文件
with open('paragraphs.json', 'w', encoding='utf-8') as f:
    json.dump(paragraphs_with_index, f, ensure_ascii=False, indent=4)

print("Faiss索引和段落内容已保存。")
