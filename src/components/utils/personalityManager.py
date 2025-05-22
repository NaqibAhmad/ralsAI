# personalityManager.py

from collections import defaultdict

server_personality = defaultdict(lambda: "normal")  # Default to "normal"

def set_personality(server_id: int, personality: str):
    server_personality[server_id] = personality.lower()

def get_personality(server_id: int) -> str:
    return server_personality[server_id]

def format_with_personality(prompt: str, personality: str) -> str:
    personality = personality.lower()

    if personality == "friendly":
        return f"You are a friendly, cheerful assistant who is always kind and encouraging.\nUser asked: {prompt}"
    
    elif personality == "sarcastic":
        return f"You are a sarcastic assistant with a witty attitude. Respond with clever humor and light mocking.\nUser asked: {prompt}"
    
    elif personality == "dark humor":
        return (
            f"You are an assistant with a taste for dry, dark humor. Respond in a bold, darkly funny tone—but stay subtle and intelligent.\n"
            f"Never cross offensive boundaries. Be edgy but tasteful.\nUser asked: {prompt}"
        )

    elif personality == "dark humor sarcastic":
        return (
            f"You are a dark-humored, sarcastic assistant. Blend cynicism, clever jokes, and dry wit.\n"
            f"Never be cruel or offensive. Just edgy enough to entertain while staying smart.\nUser asked: {prompt}"
        )
    
    elif personality == "flirty":
        return f"You are a flirty assistant with a playful attitude. Respond with charm and light-hearted teasing.\nUser asked: {prompt}"
    
    else:  # normal/default
        return f"The user asked: {prompt}"
