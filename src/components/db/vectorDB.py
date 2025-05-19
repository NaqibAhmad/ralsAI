import os
from agno.knowledge.url import UrlKnowledge
from agno.vectordb.pgvector import PgVector, SearchType
from agno.embedder.openai import OpenAIEmbedder
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')
open_ai_key = os.getenv("OPENAI_API_KEY")


db_url = "postgresql+psycopg2://ai:ai@localhost:5532/ai"

vector_db = PgVector(table_name="rals_ai", 
                        db_url=db_url, 
                        search_type=SearchType.hybrid,
                        embedder=OpenAIEmbedder(id="text-embedding-3-small", api_key=open_ai_key),
                        )

knowledge = UrlKnowledge(
    urls=["https://docs.google.com/document/d/1c5nmmUoRD6qnki09GONhxRqSuSY0uPkB88fooaK_ua8/edit?usp=sharing"],
    vector_db=vector_db,
)

# knowledge.load(recreate= True, skip_existing=True)