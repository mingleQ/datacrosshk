import json
import faiss
import numpy as np
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os

load_dotenv()
api_id = os.getenv('ZHIPU_API_ID')

api_key = api_id
def get_vector(sentence):
    client = ZhipuAI(api_key=api_key) 
    response = client.embeddings.create(
        model="embedding-2", 
        input=sentence,
    )
    emb = response.data[0].embedding
    return emb

index = faiss.read_index('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/embedding/faiss_index.index')
with open('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/embedding/paragraphs.json', 'r', encoding='utf-8') as f:
    paragraphs_with_index = json.load(f)

index_to_paragraph = {item['index']: item['content'] for item in paragraphs_with_index}


def search_from_vector(query, k=3):
    query_vector = get_vector(query)
    D, I = index.search(np.array([query_vector], dtype=np.float32), k)  
    res = []
    for idx in I[0]:
        res.append(index_to_paragraph[idx])
    return ';'.join(res)