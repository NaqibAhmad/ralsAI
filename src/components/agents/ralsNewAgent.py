from agno.agent import Agent
from dotenv import load_dotenv
import os
# from agno.models.groq import Groq
from agno.models.openai import OpenAIChat

from src.components.db.vectorDB import knowledge

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
# groq_api_key = os.getenv('GROQ_API_KEY')
open_ai_key = os.getenv("OPENAI_API_KEY")


# agent = Agent(model = Groq(id= "meta-llama/llama-4-scout-17b-16e-instruct", api_key=groq_api_key),
agent = Agent(model = OpenAIChat(id= "gpt-4.1-mini", api_key=open_ai_key),
        tools=[],
        show_tool_calls=True,
        instructions=[
            "You are a discord moderator that contains information about the server."
            "Your job is to provide responses to the user's queries."
            "Generate Plain Text with no formatting as responses. "
            "Generate short 1 line responses (Add details if necessary). Keep the responses short, concise and to the point",             
            "Keep the tone casual, friendly, engaging and Human-like."
            "Use dark humour in your response only if explicitly mentioned"
            ],
        knowledge=knowledge,
        markdown=True,
        debug_mode=True,
        )