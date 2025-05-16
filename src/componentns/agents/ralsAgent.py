from agno.agent import Agent
from agno.models.groq import Groq
from agno.tools.reasoning import ReasoningTools
from agno.tools.discord import DiscordTools
from agno.vectordb.lancedb import LanceDb
from src.componentns.db.vectorDB import VectorDBKnowledge
from dotenv import load_dotenv
import os

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
groq_api_key = os.getenv('GROQ_API_KEY')
class RalsAgent:
    def __init__(self):
        self.agent = Agent(
            name="RalsAgent",
            model=Groq(id= "deepseek-r1-distill-llama-70b", api_key=groq_api_key),
            instructions=[
                "list_channels (guild_id: '818835838821203979')"
                "get_channel_messages (channel_id: '1372894680823369769')",
                "Use the provided context to answer the user's question.",
                "If the context is insufficient, respond accordingly."
            ],
            knowledge=VectorDBKnowledge(),
            tools=[ReasoningTools(add_instructions=True), DiscordTools(bot_token=discord_token)],
            markdown=True
        )

        self.agent.print_response("Send `Hello! from the Rals AI Agent.` to channel `1372894680823369769` ")

    def respond(self, query: str) -> str:
        return self.agent.run(query)
