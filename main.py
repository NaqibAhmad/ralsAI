import discord
import os
from src.components.agents.ralsNewAgent import agent
from dotenv import load_dotenv
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Ensure it's an integer

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user} (ID: {client.user.id})')

@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return  # Ignore messages from bots

    # Only respond if mentioned and in correct channel
    if client.user in message.mentions and message.channel.id == CHANNEL_ID:
        user_mention = message.author.mention
        user_message = message.clean_content.replace(f"<@{client.user.id}>", "").strip()

        print(f"📩 Mention detected from {user_mention}: {user_message}")

        try:
            # Generate response from agent
            agent_response = agent.run(
                message=f"This is the message from user: {user_message}. Generate a response according to the user message"
            )
            print(f"🤖 Agent response: {agent_response}")

            # Extract assistant message
            assistant_message = next(
                (msg.content for msg in getattr(agent_response, "messages", []) if msg.role == "assistant"),
                None
            )

            if not assistant_message:
                assistant_message = "🤖 I couldn't generate a response."

            # Reply by mentioning the user
            await message.channel.send(f"{user_mention} {assistant_message}")

        except Exception as e:
            print("❌ Error:", e)
            await message.channel.send(f"{user_mention} Sorry, I encountered an error while trying to respond.")

client.run(DISCORD_BOT_TOKEN)
