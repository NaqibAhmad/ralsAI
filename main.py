import discord
import os
from src.components.agents.GroqAgent import agent
from src.components.utils.intentClassifier import classify_intent
from src.components.prompts.serverInfoPrompt import generate_server_prompt
from src.components.prompts.userInfoPrompt import generate_user_prompt
from src.components.utils.messageUtils import extract_clean_user_message

from dotenv import load_dotenv
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))  # Ensure it's an integer
print(f"Channel ID: {CHANNEL_ID}")

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

    # Only respond if bot is mentioned and in the correct channel
    if client.user in message.mentions:
        user_mention = message.author.mention
        user_message = extract_clean_user_message(message, client.user.id)

        print(f"📩 Mention detected from {user_mention}: {user_message}")

        try:
            intent = classify_intent(user_message)
            print(f"🔍 Detected intent: {intent}")

            # 🔁 Inject prompt based on intent
            if intent == "server_info":
                input_prompt = generate_server_prompt(user_message, message.guild)
            elif intent == "user_info":
                input_prompt = generate_user_prompt(user_message, message)
            else:
                input_prompt = f"This is the message from user: {user_message}. Generate a response according to the user message"

            # 💬 Run through LLM agent
            agent_response = agent.run(message=input_prompt)
            assistant_message = getattr(agent_response, "content", None) or "🤖 I couldn't generate a response."

            await message.channel.send(f"{user_mention} {assistant_message}")

        except Exception as e:
            print("❌ Error:", e)
            await message.channel.send(f"{user_mention} Sorry, I encountered an error while trying to respond.")

client.run(DISCORD_BOT_TOKEN)
