from neo4j import GraphDatabase

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def import_csv(self):
        with self.driver.session() as session:
            # 导入Paragraphs，避免重复
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///Paragraphs.csv' AS row
            MERGE (p:Paragraph {id: row.ParagraphID})
            ON CREATE SET p.text = row.Paragraph, p.name = row.name
            """)

            # 导入Keywords，避免重复
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///Keywords.csv' AS row
            MERGE (k:Keyword {id: row.KeywordID})
            ON CREATE SET k.keyword = row.Keywords, k.name = row.name
            """)

            # 导入Category，避免重复
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///Categories.csv' AS row
            MERGE (c:Category {id: row.CategoryID})
            ON CREATE SET c.category = row.Category, c.name = row.name
            """)

            # 导入Country，避免重复
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///Countries.csv' AS row
            MERGE (c:Country {id: row.CountryID})
            ON CREATE SET c.country = row.Country, c.name = row.name
            """)

            # 创建Keyword到Category的关系，避免重复
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///KeywordCategories.csv' AS row
            MATCH (k:Keyword {id: row.KeywordID}), (c:Category {id: row.CategoryID})
            MERGE (k)-[:BELONGS_TO]->(c)
            """)
            # 导入ParagraphKeywords关系
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///ParagraphKeywords.csv' AS row
            MATCH (paragraph:Paragraph {id: row.ParagraphID}), (keyword:Keyword {id: row.KeywordID})
            MERGE (paragraph)-[:CONTAINS]->(keyword)
            """)

             # 导入CategoryCountries关系
            session.run("""
            LOAD CSV WITH HEADERS FROM 'file:///CategoryCountries.csv' AS row
            MATCH (category:Category {id: row.CategoryID}), (country:Country {id: row.CountryID})
            MERGE (category)-[:CONTAINSCOUNTRY]->(country)
            """)



if __name__ == "__main__":
    uri = "bolt://localhost:7687"  
    user = "neo4j"  
    password = "neo4j123"  #
    importer = Neo4jImporter(uri, user, password)
    importer.clear_database()  # 清空数据库
    importer.import_csv()  # 导入CSV数据
    importer.close()
