from agno.agent import Agent
from agno.tools.discord import DiscordTools
from dotenv import load_dotenv
import os
from agno.models.groq import Groq

load_dotenv()

discord_token = os.getenv('DISCORD_TOKEN')
groq_api_key = os.getenv('GROQ_API_KEY')

agent = Agent(  model = Groq(id= "deepseek-r1-distill-llama-70b", api_key=groq_api_key),
                tools=[DiscordTools(bot_token=discord_token)],
                show_tool_calls=True,
                introduction=[
                    "list_channels (guild_id: '818835838821203979')"
                    "channel_id: '1372894680823369769' "
                    "Whever you detect a message in the channel reply with `Hello this is rals AI`"
                    "If the context is insufficient, respond accordingly."
                ],
                markdown=True,
                debug_mode=True,
                
                )

agent.print_response("Get all messages from the discord channel (1372894680823369769) and generate a response according to the user query and send it to the channel, ")