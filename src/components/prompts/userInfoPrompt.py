import discord
from datetime import datetime, timezone
from typing import List, Dict, Optional
import logging

def generate_user_prompt(user_message: str, message: discord.Message) -> str:
    """
    Generates an enhanced prompt with comprehensive user information for AI responses.
    
    Args:
        user_message: The original user's message/query
        message: Discord message object containing mentions and context
        
    Returns:
        Formatted prompt string with user information and clear instructions
    """
    
    # Enhanced user filtering with better validation
    target_users = _get_valid_mentioned_users(message)
    
    if not target_users:
        return _generate_no_user_prompt(user_message)
    
    # Get the primary target user (first mentioned)
    target_user = target_users[0]
    
    # Gather comprehensive user information
    user_info = _gather_user_information(target_user, message.guild)
    
    # Log debug information
    _log_user_query_debug(user_message, user_info)
    
    # Generate enhanced prompt
    return _create_enhanced_user_prompt(user_message, user_info, target_user)

def _get_valid_mentioned_users(message: discord.Message) -> List[discord.Member]:
    """
    Filters mentioned users, excluding bots and the current bot.
    """
    if not message.mentions:
        return []
    
    # Filter out bots and the current bot instance
    valid_users = []
    for member in message.mentions:
        if (hasattr(message.guild, 'me') and 
            member.id != message.guild.me.id and 
            not member.bot):  # Exclude all bots for better responses
            valid_users.append(member)
    
    return valid_users

def _gather_user_information(user: discord.Member, guild: discord.Guild) -> Dict[str, str]:
    """
    Collects comprehensive information about a Discord user.
    """
    try:
        # Basic user information
        user_info = {
            "Display Name": user.display_name or "Unknown",
            "Username": f"{user.name}#{user.discriminator}" if user.discriminator != "0" else f"@{user.name}",
            "User ID": str(user.id),
            "Account Type": "Bot" if user.bot else "User"
        }
        
        # Server-specific information
        user_info.update(_get_server_specific_info(user, guild))
        
        # Role information
        user_info.update(_get_role_information(user))
        
        # Activity and status
        user_info.update(_get_activity_status(user))
        
        # Permissions summary
        user_info.update(_get_permission_summary(user))
        
        return user_info
        
    except Exception as e:
        logging.error(f"Error gathering user information: {e}")
        return {"Error": "Could not retrieve user information"}

def _get_server_specific_info(user: discord.Member, guild: discord.Guild) -> Dict[str, str]:
    """
    Gathers server-specific user information.
    """
    info = {}
    
    # Server ownership
    info["Server Owner"] = "Yes" if user == guild.owner else "No"
    
    # Join date with better formatting
    if user.joined_at:
        joined_date = user.joined_at.strftime("%B %d, %Y at %I:%M %p UTC")
        # Calculate days since joining
        days_since_join = (datetime.now(timezone.utc) - user.joined_at).days
        info["Joined Server"] = f"{joined_date} ({days_since_join} days ago)"
    else:
        info["Joined Server"] = "Unknown"
    
    # Account creation date
    if user.created_at:
        created_date = user.created_at.strftime("%B %d, %Y")
        info["Account Created"] = created_date
    
    # Server nickname vs username
    if user.nick and user.nick != user.display_name:
        info["Server Nickname"] = user.nick
    
    return info

def _get_role_information(user: discord.Member) -> Dict[str, str]:
    """
    Collects detailed role information.
    """
    # Filter out @everyone and organize roles
    meaningful_roles = [role for role in user.roles if role.name != "@everyone"]
    
    if not meaningful_roles:
        return {"Roles": "No special roles (only @everyone)"}
    
    # Sort roles by position (highest first)
    meaningful_roles.sort(key=lambda r: r.position, reverse=True)
    role_names = [role.name for role in meaningful_roles]
    
    # Get highest role info
    highest_role = meaningful_roles[0]
    
    return {
        "Roles": ", ".join(role_names),
        "Highest Role": f"{highest_role.name} (Position: {highest_role.position})",
        "Role Count": str(len(meaningful_roles))
    }

def _get_activity_status(user: discord.Member) -> Dict[str, str]:
    """
    Gets user's current activity and status.
    """
    info = {}
    
    # Online status
    status_map = {
        discord.Status.online: "Online",
        discord.Status.idle: "Idle",
        discord.Status.dnd: "Do Not Disturb",
        discord.Status.offline: "Offline"
    }
    info["Status"] = status_map.get(user.status, "Unknown")
    
    # Current activity
    if user.activity:
        activity_type = type(user.activity).__name__
        if hasattr(user.activity, 'name'):
            activity_name = user.activity.name
            info["Current Activity"] = f"{activity_type}: {activity_name}"
        else:
            info["Current Activity"] = activity_type
    else:
        info["Current Activity"] = "None"
    
    return info

def _get_permission_summary(user: discord.Member) -> Dict[str, str]:
    """
    Provides a summary of important permissions.
    """
    perms = user.guild_permissions
    
    # Check for important administrative permissions
    admin_perms = []
    if perms.administrator:
        admin_perms.append("Administrator")
    if perms.manage_guild:
        admin_perms.append("Manage Server")
    if perms.manage_channels:
        admin_perms.append("Manage Channels")
    if perms.manage_roles:
        admin_perms.append("Manage Roles")
    if perms.kick_members:
        admin_perms.append("Kick Members")
    if perms.ban_members:
        admin_perms.append("Ban Members")
    
    permission_level = "Standard User"
    if admin_perms:
        if "Administrator" in admin_perms:
            permission_level = "Administrator"
        elif len(admin_perms) >= 3:
            permission_level = "Senior Moderator"
        else:
            permission_level = "Moderator"
    
    return {
        "Permission Level": permission_level,
        "Key Permissions": ", ".join(admin_perms) if admin_perms else "None"
    }

def _log_user_query_debug(user_message: str, user_info: Dict[str, str]) -> None:
    """
    Logs debug information for troubleshooting.
    """
    debug_output = "\n".join([f"  {k}: {v}" for k, v in user_info.items()])
    logging.info(f"USER QUERY DEBUG:\n"
                f"Query: '{user_message}'\n"
                f"User Information:\n{debug_output}")

def _generate_no_user_prompt(user_message: str) -> str:
    """
    Generates prompt when no valid user is mentioned.
    """
    return f"""
QUERY ANALYSIS:
User Message: "{user_message}"
Issue: No valid user was mentioned or found.

INSTRUCTIONS:
The user asked about another member but didn't properly mention them using @username.
Provide a helpful response explaining:
1. You need them to mention a specific user with @username
2. Briefly explain how to mention users in Discord
3. Offer to help once they provide a proper mention

Keep the response friendly and instructional.
"""

def _create_enhanced_user_prompt(user_message: str, user_info: Dict[str, str], target_user: discord.Member) -> str:
    """
    Creates the final enhanced prompt with comprehensive instructions.
    """
    # Format user information clearly
    formatted_info = "\n".join([f"  • {k}: {v}" for k, v in user_info.items()])
    
    return f"""
USER INFORMATION REQUEST:
Query: "{user_message}"
Target User: @{target_user.display_name}

AVAILABLE USER DATA:
{formatted_info}

RESPONSE INSTRUCTIONS:
1. Generate a friendly, informative response about this user
2. Use the provided information to answer the user's specific question
3. Keep the tone casual and engaging
4. Include relevant details but don't overwhelm with information
5. If the query asks for specific info not available, mention what you don't have access to
6. Be respectful of the mentioned user's privacy

RESPONSE GUIDELINES:
- Start with a direct answer to their question
- Use natural, conversational language
- Include 2-3 most relevant pieces of information
- End on a positive, friendly note
- Keep response length appropriate (1-3 sentences typically)

Generate your response now:
"""

# Utility function for testing and validation
def validate_user_prompt_generation(message: discord.Message) -> bool:
    """
    Validates that the message is suitable for user prompt generation.
    """
    return (hasattr(message, 'mentions') and 
            hasattr(message, 'guild') and 
            message.guild is not None and
            len(message.mentions) > 0)