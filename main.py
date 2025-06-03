import discord
import os
from dotenv import load_dotenv

from src.components.agents.GroqAgent import agent
from src.components.utils.intentClassifier import classify_intent
from src.components.prompts.serverInfoPrompt import generate_server_prompt
from src.components.prompts.userInfoPrompt import generate_user_prompt
from src.components.utils.messageUtils import extract_clean_user_message
from src.components.utils.eventReminder import handle_event_or_reminder
from src.components.utils.helpResolver import handle_help_request_optimized as handle_help_request

# Updated import for improved personality manager
from src.components.utils.personalityManager import (
    set_personality, 
    get_personality, 
    format_with_personality,
    get_available_personalities,
    get_personality_help_text
)

load_dotenv()
from fast_api import keep_alive

keep_alive()  # Start the dummy web server



# Your Discord bot logic below
DISCORD_BOT_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
print(f"Channel ID: {CHANNEL_ID}")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True

client = discord.Client(intents=intents)

# Updated to use the improved personality system
VALID_PERSONALITIES = get_available_personalities()  # Now gets from the improved system

TRUSTED_BOT_IDS = [
    1336350743837409341,  
    1372896968233189516   
]

@client.event
async def on_ready():
    print(f'✅ Logged in as {client.user} (ID: {client.user.id})')


@client.event
async def on_message(message: discord.Message):
    if message.author.bot and message.author.id not in TRUSTED_BOT_IDS:
        print(f"⛔ Skipping message from untrusted bot: {message.author.name} (ID: {message.author.id})")
        return
    
    if await handle_event_or_reminder(message):
        return

    if client.user in message.mentions:
        user_mention = message.author.mention
        # Use improved extraction
        user_message = extract_clean_user_message(message, client.user.id, client.user.name)
        
        # Debug: See what extraction produces (remove in production)
        print(f"Original: {message.content}")
        print(f"Cleaned: {user_message}")

        # 🧠 Enhanced personality management with improved validation
        if "set personality to" in user_message.lower():
            parts = user_message.lower().split("set personality to")
            if len(parts) > 1:
                new_persona = parts[1].strip()
                
                # Use improved personality system with better validation
                if set_personality(message.guild.id, new_persona):
                    await message.channel.send(f"{user_mention} Personality switched to **{new_persona}** 🧠")
                else:
                    # Send helpful error message with all available personalities
                    available_personalities = ", ".join(VALID_PERSONALITIES.keys())
                    await message.channel.send(
                        f"{user_mention} Invalid personality. Choose one of: {available_personalities}"
                    )
                return
        
        # 🧠 Show personality help
        if "personality help" in user_message.lower() or "list personalities" in user_message.lower():
            help_text = get_personality_help_text()
            await message.channel.send(f"{user_mention}\n{help_text}")
            return

        try:
            # 🧠 Intent classification using improved classifier
            intent = await classify_intent(user_message)
            print(f"🔍 Detected intent: {intent}")

            # 🧠 Handle different intents with improved prompts
            if intent == "user_wants_help":     # Intent: Help detection
                await handle_help_request(message)
                return

            elif intent == "server_info":   # Intent: Server info
                input_prompt = generate_server_prompt(user_message, message.guild)
                
            elif intent == "user_info":  # Intent: User info (using improved user prompt)
                input_prompt = generate_user_prompt(user_message, message)
                
            else:   # Intent: General conversation
                input_prompt = f"User message: {user_message}"

            # 🧠 Enhanced personality formatting with context
            personality = get_personality(message.guild.id)
            # Pass Discord moderator context to the improved personality system
            final_prompt = format_with_personality(
                input_prompt, 
                personality, 
                context="You are a Discord AI moderator for the server 'The Rals'"
            )
            
            print(f"🎭 Applied personality: {personality}")
            print(f"📝 Final prompt: {final_prompt[:200]}...")  # Truncated for cleaner logs

            # 💬 Generate response
            agent_response = await agent.arun(message=final_prompt)
            assistant_message = getattr(agent_response, "content", None) or "🤖 I couldn't generate a response."

            await message.channel.send(f"{user_mention} {assistant_message}")

        except Exception as e:
            print(f"❌ Error: {e}")
            await message.channel.send(f"{user_mention} Sorry, I encountered an error while trying to respond.")

client.run(DISCORD_BOT_TOKEN)