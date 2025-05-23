import discord
import os
from dotenv import load_dotenv

from src.components.agents.GroqAgent import agent
from src.components.utils.intentClassifier import classify_intent
from src.components.prompts.serverInfoPrompt import generate_server_prompt
from src.components.prompts.userInfoPrompt import generate_user_prompt
from src.components.utils.messageUtils import extract_clean_user_message
from src.components.utils.eventReminder import handle_event_or_reminder
from src.components.utils.personalityManager import set_personality, get_personality, format_with_personality
from src.components.utils.helpResolver import handle_help_request

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
print(f"Channel ID: {CHANNEL_ID}")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

VALID_PERSONALITIES = {"normal", "friendly", "sarcastic", "dark humor", "dark humor sarcastic", "flirty"}

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user} (ID: {client.user.id})')


@client.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if await handle_event_or_reminder(message):
        return

    if client.user in message.mentions:
        user_mention = message.author.mention
        user_message = extract_clean_user_message(message, client.user.id)

        print(f"📩 Mention detected from {user_mention}: {user_message}")

        # 🧠 Check if the user is trying to change personality
        if "set personality to" in user_message.lower():
            parts = user_message.lower().split("set personality to")
            if len(parts) > 1:
                new_persona = parts[1].strip()
                if new_persona in VALID_PERSONALITIES:
                    set_personality(message.guild.id, new_persona)
                    await message.channel.send(f"{user_mention} Personality switched to **{new_persona}** 🧠")
                else:
                    await message.channel.send(
                        f"{user_mention} Invalid personality. Choose one of: {', '.join(VALID_PERSONALITIES)}"
                    )
                return

        try:
            
            # 🧠 Intent classification
            intent = classify_intent(user_message)
            print(f"🔍 Detected intent: {intent}")

            intent = classify_intent(user_message)

            # 🧠 Handle different intents            
            if intent == "user_wants_help":     # Intent: Help detection
                await handle_help_request(message)
                return

            if intent == "server_info":   # Intent: Server info
                input_prompt = generate_server_prompt(user_message, message.guild)
            elif intent == "user_info":  # Intent: User info
                input_prompt = generate_user_prompt(user_message, message)
            else:   # Intent: General conversation
                input_prompt = f"This is the message from user: {user_message}. Generate a response according to the user message"

            # 🧠 Personality formatting
            personality = get_personality(message.guild.id)
            input_prompt = format_with_personality(input_prompt, personality)

            # 💬 Generate response
            agent_response = agent.run(message=input_prompt)
            assistant_message = getattr(agent_response, "content", None) or "🤖 I couldn't generate a response."

            await message.channel.send(f"{user_mention} {assistant_message}")

        except Exception as e:
            print("❌ Error:", e)
            await message.channel.send(f"{user_mention} Sorry, I encountered an error while trying to respond.")

client.run(DISCORD_BOT_TOKEN)
