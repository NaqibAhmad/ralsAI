from agno.agent import Agent
from dotenv import load_dotenv
import os
from agno.models.groq import Groq

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
groq_api_key = os.getenv('GROQ_API_KEY')

agent = Agent(model = Groq(id= "meta-llama/llama-4-scout-17b-16e-instruct", api_key=groq_api_key),
                tools=[],
                show_tool_calls=True,
                instructions=[
                    "You are a discord moderator that contains information about the server. Your job is to provide responses to the user's queries. Generate Plain Text with no formatting as responses. Keep the responses short , concise and to the point",
                    "Server Name : THE RALS , Server Owner: The server actually have 4 owners. Kat, Anu also known as Lips wala Owner , Tribb , Muski. Muski is co owner and other 3 are equally owners"
                    "Top Members : Umair and Nikki",                    
                ],
                markdown=True,
                debug_mode=True,
                )