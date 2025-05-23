import discord


def generate_user_prompt(user_message: str, message: discord.Message) -> str:
    # Filter out the bot itself from mentions
    target_users = [member for member in message.mentions if member.id != message.guild.me.id]

    if not target_users:
        return "The user asked something about another member, but no valid user was mentioned."

    target_user = target_users[0]  # First valid mentioned user (excluding the bot)

    roles = [role.name for role in target_user.roles if role.name != "@everyone"]
    joined_at = target_user.joined_at.strftime("%B %d, %Y") if target_user.joined_at else "Unknown"

    user_info = {
        "Name": target_user.display_name,
        "User ID": target_user.id,
        "Server Owner": "Yes" if target_user == message.guild.owner else "No",
        "Joined Server": joined_at,
        "Roles": ", ".join(roles) if roles else "No roles"
    }

    debug_output = "\n".join([f"{k}: {v}" for k, v in user_info.items()])
    print(f"DEBUG The user asked: '{user_message}'\nHere is some metadata about the mentioned user:\n{debug_output}")

    return (
        f"The user asked: '{user_message}'\n"
        f"Here is some metadata about the mentioned user:\n{debug_output}\n"
        f"Use this info to generate a short, friendly, response describing the user."
    )
