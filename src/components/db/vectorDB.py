from agno.knowledge.url import UrlKnowledge
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.cohere import CohereEmbedder

class VectorDBKnowledge:
    def __init__(self):
        self.knowledge = UrlKnowledge(
            urls=["https://docs.google.com/document/d/1c5nmmUoRD6qnki09GONhxRqSuSY0uPkB88fooaK_ua8/edit?usp=sharing"],
            vector_db=LanceDb(
                uri="tmp/lancedb",
                table_name="server_docs",
                search_type=SearchType.hybrid,
                embedder=CohereEmbedder(api_key="ssIR2YhhbXS1bXQB6Ow0EkZlAVGDO6FS8c9GEyqJ"),
            ),
        )
        self.knowledge.load(recreate=False)

    

    def __call__(self, query: str):
        return self.knowledge.search(query)
