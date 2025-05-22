from discord import Guild

def get_server_info(guild: Guild) -> dict:
    return {
        "name": guild.name,
        "created_at": guild.created_at.strftime("%B %d, %Y"),
        "member_count": guild.member_count,
        "owner": "This server has 4 owners, Kat, Anu, Muski, Tribb. Muski is co-owner, the rest are equal owners.",
        "id": guild.id,
    }

def generate_context_from_guild(guild: Guild) -> str:
    info = get_server_info(guild)
    return (
        f"Server Name: {info['name']}\n"
        f"Created On: {info['created_at']}\n"
        f"Total Members: {info['member_count']}\n"
        f"Server Owner: {info['owner']}\n"
        f"Server ID: {info['id']}"
    )
