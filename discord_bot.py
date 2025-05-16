import discord
import os
from test import agent
from dotenv import load_dotenv
load_dotenv()


# Replace this with your actual token
DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = 1372894680823369769

intents = discord.Intents.default()
intents.message_content = True  # Required to read messages
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user} (ID: {client.user.id})')

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return  # Ignore other bots

    # if message.channel.id == CHANNEL_ID:
    #     user_message = message.content
    #     print(f"📩 Message received: {user_message}")
    
    # Check if bot is mentioned
    if client.user in message.mentions and message.channel.id == CHANNEL_ID:
        user_message = message.content
        print(f"📩 Mention detected: {user_message}")

        # Generate a response using your agent
        agent_response = agent.run(message=
            f"This is the message from user: {user_message}. Generate a response according to the user message"
        )
        print(f"🤖 Agent response: {agent_response}")
        
        # Extract only the assistant message content
        assistant_message = next(
            (msg.content for msg in getattr(agent_response, "messages", []) if msg.role == "assistant"),
            None
        )

        if not assistant_message:
            assistant_message = "🤖 I couldn't generate a response."


        await message.channel.send(assistant_message)

client.run(DISCORD_BOT_TOKEN)
