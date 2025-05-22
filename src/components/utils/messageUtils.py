def extract_clean_user_message(message, bot_id):
    # Remove only the bot mention from the clean content
    parts = message.clean_content.split()
    cleaned_parts = [part for part in parts if part != f"<@{bot_id}>"]
    return " ".join(cleaned_parts).strip()
