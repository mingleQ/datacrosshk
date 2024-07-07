import jieba
from py2neo import  ConnectionUnavailable
from neo4j import GraphDatabase
import pandas as pd
import os 
from difflib import SequenceMatcher
current_dir = os.getcwd()  

# 定义关键词CSV文件的相对路径
keyword_txt_path = os.path.join(current_dir, 'neo4j_sc/keyword.txt')
jieba.load_userdict(keyword_txt_path)
keyword_csv_path = os.path.join(current_dir, 'neo4j_sc/neo4j_csv/Keywords.csv')
keyword_pd = pd.read_csv(keyword_csv_path)
keyword_dict = dict(zip(keyword_pd['Keywords'],keyword_pd['KeywordID']))


try:
    uri = "bolt://localhost:7687"  
    user = "neo4j"  
    password = "neo4j123"  
    driver = GraphDatabase.driver(uri, auth=(user, password))

except ConnectionUnavailable  as e:
    print("未连接neo4j")
    pass


def search_paragraphs_by_category(category_name):
    paragraph_list = []
    query = """
    MATCH (c:Category {category: $category_name})<-[:BELONGS_TO]-(k:Keyword)<-[:CONTAINS]-(p:Paragraph)
    RETURN p.text AS paragraph_text
    """
    with driver.session() as session:
        result = session.run(query, category_name=category_name)
        for record in result:
            paragraph_list.append(record["paragraph_text"])
            
    return ';'.join(paragraph_list)

def search_paragraphs_by_country_and_keyword(keyword_name,country_name):
    paragraph_list = []
    query = """
    MATCH (country:Country {country: $country_name})<-[:CONTAINSCOUNTRY]-(category:Category)<-[:BELONGS_TO]-(keyword:Keyword {keyword: $keyword_name})<-[:CONTAINS]-(paragraph:Paragraph)
    RETURN paragraph.text AS paragraph_text
    """
    paragraph_list = []
    with driver.session() as session:
        result = session.run(query, country_name=country_name, keyword_name=keyword_name)
        for record in result:
            paragraph_list.append(record["paragraph_text"])
    return ';'.join(paragraph_list)

def search_paragraphs_by_keyword(keyword_name):
    query = """
    MATCH (keyword:Keyword {keyword: $keyword_name})<-[:CONTAINS]-(paragraph:Paragraph)
    RETURN paragraph.text AS paragraph_text
    """
    paragraph_list = []
    with driver.session() as session:
        result = session.run(query, keyword_name=keyword_name)
        for record in result:
            paragraph_list.append(record["paragraph_text"])
    return ';'.join(paragraph_list)

# def search_from_neo4j(user_input, country): 
#     country_flag = False 
#     if len(country) > 1:
#         country_flag = True
#     keywords = jieba.lcut(user_input)
#     hit_keywords_content = {}
#     for keyword in keywords:
#         if len(keyword) > 1 and  keyword in keyword_dict:
#                 if country_flag:
#                     content_from_neo4j = search_paragraphs_by_country_and_keyword(keyword_name=keyword, country_name=country)
#                     hit_keywords_content[keyword] = content_from_neo4j
#                 else:
#                     content_from_neo4j = search_paragraphs_by_keyword(keyword_name=keyword)
#                     hit_keywords_content[keyword] = content_from_neo4j
#     return hit_keywords_content

thresholds = 0.5

def search_from_neo4j(user_input, country):
    country_flag = False
    if len(country) > 1:
        country_flag = True
    
    keywords = jieba.lcut(user_input)
    hit_keywords_content = {}

    for keyword in keywords:
        if len(keyword) > 1:
            # 找到与当前keyword相似度超过阈值的keyword_dict中的key
            similar_keywords = [(key, SequenceMatcher(None, keyword, key).ratio()) for key in keyword_dict.keys() if SequenceMatcher(None, keyword, key).ratio() > thresholds]
            
            if similar_keywords:
                # 找到相似度最高的key
                best_match = max(similar_keywords, key=lambda x: x[1])
                best_keyword = best_match[0]
                
                if country_flag:
                    content_from_neo4j = search_paragraphs_by_country_and_keyword(keyword_name=best_keyword, country_name=country)
                    hit_keywords_content[keyword] = content_from_neo4j
                else:
                    content_from_neo4j = search_paragraphs_by_keyword(keyword_name=best_keyword)
                    hit_keywords_content[keyword] = content_from_neo4j

    return hit_keywords_content

