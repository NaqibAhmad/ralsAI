import discord
def extract_clean_user_message(message: discord.Message, bot_id, bot_name):
    # Get all display mentions like "@The Rals"
    mention_names = [f"@{user.display_name}" for user in message.mentions]

    # Cleaned message with mentions removed
    parts = message.clean_content.split()
    cleaned_parts = [part for part in parts if part not in mention_names]

    return " ".join(cleaned_parts).strip()
