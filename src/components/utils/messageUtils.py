import discord
import re

def extract_clean_user_message(message: discord.Message, bot_id, bot_name):
    """
    Extract clean user message by removing bot mentions and other noise.
    Returns the actual message content for intent classification.
    """
    # Start with clean_content (Discord already converts mentions to readable format)
    content = message.clean_content.strip()
    
    # Remove bot mention patterns (multiple formats)
    bot_mention_patterns = [
        f"@{bot_name}",  # @BotName
        f"<@{bot_id}>",  # Raw mention format
        f"<@!{bot_id}>", # Nickname mention format
    ]
    
    for pattern in bot_mention_patterns:
        content = content.replace(pattern, "").strip()
    
    # Remove extra whitespace and clean up
    content = re.sub(r'\s+', ' ', content).strip()
    
    # Remove leading/trailing punctuation that might be left over
    content = content.strip('.,!?;:')
    
    return content