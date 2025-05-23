import re
from src.components.utils.serverInfo import generate_context_from_guild

def generate_server_prompt(message: str, guild) -> str:
    context = generate_context_from_guild(guild)
    return (
        f"User asked: '{message}'\n"
        f"Here is the server context:\n{context}\n"
        f"Respond based on the context above in a concise, casual way."
    )
