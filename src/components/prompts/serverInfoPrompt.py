import re
from src.components.utils.serverInfo import generate_context_from_guild

# Simple pattern matching for server-related questions
def is_server_info_query(message: str) -> bool:
    server_keywords = [
        r"when.*(server|this).*created",
        r"who.*(owner|owns).*server",
        r"how many (members|people)",
        r"(server|guild).*info",
        r"what.*server",
        r"total.*members",
        r"who.*admin",
    ]
    return any(re.search(pattern, message.lower()) for pattern in server_keywords)


def generate_server_prompt(message: str, guild) -> str:
    context = generate_context_from_guild(guild)
    return (
        f"User asked: '{message}'\n"
        f"Here is the server context:\n{context}\n"
        f"Respond based on the context above in a concise, casual way."
    )
