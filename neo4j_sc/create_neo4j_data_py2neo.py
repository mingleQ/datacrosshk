import pandas as pd
from py2neo import Graph, Node, Relationship

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.graph = Graph(uri, auth=(user, password))

    def clear_database(self):
        self.graph.delete_all()

    def import_csv(self):
        # 导入Paragraphs，避免重复
        paragraphs = pd.read_csv('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/neo4j/neo4j_csv/Paragraphs.csv')
        for index, row in paragraphs.iterrows():
            node = Node('Paragraph', id=row['ParagraphID'], text=row['Paragraph'], name=row['name'])
            self.graph.merge(node, 'Paragraph', 'id')
        print("import paragraph")

        # 导入Keywords，避免重复
        keywords = pd.read_csv('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/neo4j/neo4j_csv/Keywords.csv')
        for index, row in keywords.iterrows():
            node = Node('Keyword', id=row['KeywordID'], keyword=row['Keywords'], name=row['name'])
            self.graph.merge(node, 'Keyword', 'id')
        print("import keywords")

        # 导入Category，避免重复
        categories = pd.read_csv('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/neo4j/neo4j_csv/Categories.csv')
        for index, row in categories.iterrows():
            node = Node('Category', id=row['CategoryID'], category=row['Category'], name=row['name'])
            self.graph.merge(node, 'Category', 'id')
        print("import categories")

        # 导入Country，避免重复
        countries = pd.read_csv('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/neo4j/neo4j_csv/Countries.csv')
        for index, row in countries.iterrows():
            node = Node('Country', id=row['CountryID'], country=row['Country'], name=row['name'])
            self.graph.merge(node, 'Country', 'id')
        print("import countries")

        # 创建Keyword到Category的关系，避免重复
        keyword_categories = pd.read_csv('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/neo4j/neo4j_csv/KeywordCategories.csv')
        for index, row in keyword_categories.iterrows():
            keyword_node = self.graph.nodes.match('Keyword', id=row['KeywordID']).first()
            category_node = self.graph.nodes.match('Category', id=row['CategoryID']).first()
            if keyword_node and category_node:
                rel = Relationship(keyword_node, 'BELONGS_TO', category_node)
                self.graph.merge(rel)
        print("keyword_categories")

        # 导入ParagraphKeywords关系
        paragraph_keywords = pd.read_csv('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/neo4j/neo4j_csv/ParagraphKeywords.csv')
        for index, row in paragraph_keywords.iterrows():
            paragraph_node = self.graph.nodes.match('Paragraph', id=row['ParagraphID']).first()
            keyword_node = self.graph.nodes.match('Keyword', id=row['KeywordID']).first()
            if paragraph_node and keyword_node:
                rel = Relationship(paragraph_node, 'CONTAINS', keyword_node)
                self.graph.merge(rel)
        print("paragraph_keywords")

        # 导入CategoryCountries关系
        category_countries = pd.read_csv('/Users/qinmingming/workspace/rag_neo4j_llm_datacross/neo4j/neo4j_csv/CategoryCountries.csv')
        for index, row in category_countries.iterrows():
            category_node = self.graph.nodes.match('Category', id=row['CategoryID']).first()
            country_node = self.graph.nodes.match('Country', id=row['CountryID']).first()
            if category_node and country_node:
                rel = Relationship(category_node, 'CONTAINS', country_node)
                self.graph.merge(rel)
        print("category_countries")

if __name__ == "__main__":
    uri = "bolt://localhost:7687"  
    user = "neo4j"  
    password = "neo4j123"  
    importer = Neo4jImporter(uri, user, password)
    importer.clear_database()  # 清空数据库
    importer.import_csv()  # 导入CSV数据
