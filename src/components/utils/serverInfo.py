import logging
from typing import Dict, Any
from discord import Guild, TextChannel, VoiceChannel, CategoryChannel

def get_server_info(guild: Guild) -> Dict[str, Any]:
    """
    Extracts comprehensive server information from a Discord guild object.
    
    Args:
        guild: Discord guild object containing server information
        
    Returns:
        Dictionary containing detailed server information
    """
    try:
        # Basic server information
        basic_info = {
            "name": guild.name,
            "created_at": guild.created_at.strftime("%B %d, %Y"),
            "member_count": guild.member_count,
            "id": guild.id,
            "description": getattr(guild, 'description', None),
            "verification_level": str(guild.verification_level).replace('_', ' ').title(),
            "boost_level": guild.premium_tier,
            "boost_count": guild.premium_subscription_count,
        }
        
        # Channel information
        channels_info = _get_channels_info(guild)
        basic_info.update(channels_info)
        
        # Role information
        roles_info = _get_roles_info(guild)
        basic_info.update(roles_info)
        
        # Member information
        members_info = _get_members_info(guild)
        basic_info.update(members_info)
        
        # Server features and settings
        features_info = _get_features_info(guild)
        basic_info.update(features_info)
        
        return basic_info
        
    except Exception as e:
        logging.error(f"Error extracting server info for {guild.name}: {e}")
        # Return basic fallback information
        return {
            "name": guild.name,
            "created_at": guild.created_at.strftime("%B %d, %Y") if guild.created_at else "Unknown",
            "member_count": guild.member_count or 0,
            "id": guild.id,
            "error": "Limited information available"
        }

def _get_channels_info(guild: Guild) -> Dict[str, Any]:
    """Extract channel-related information from the guild."""
    try:
        text_channels = [ch for ch in guild.channels if isinstance(ch, TextChannel)]
        voice_channels = [ch for ch in guild.channels if isinstance(ch, VoiceChannel)]
        categories = [ch for ch in guild.channels if isinstance(ch, CategoryChannel)]
        
        # Get notable channels (those with special purposes or many members)
        notable_channels = []
        for channel in text_channels[:10]:  # Limit to prevent overwhelming output
            if hasattr(channel, 'topic') and channel.topic:
                notable_channels.append({
                    'name': channel.name,
                    'topic': channel.topic[:100] + "..." if len(channel.topic) > 100 else channel.topic
                })
            else:
                notable_channels.append({'name': channel.name, 'topic': None})
        
        return {
            "total_channels": len(guild.channels),
            "text_channels_count": len(text_channels),
            "voice_channels_count": len(voice_channels),
            "categories_count": len(categories),
            "notable_channels": notable_channels
        }
    except Exception as e:
        logging.error(f"Error getting channel info: {e}")
        return {
            "total_channels": len(guild.channels) if guild.channels else 0,
            "text_channels_count": 0,
            "voice_channels_count": 0,
            "categories_count": 0,
            "notable_channels": []
        }

def _get_roles_info(guild: Guild) -> Dict[str, Any]:
    """Extract role-related information from the guild."""
    try:
        roles = guild.roles
        
        # Filter out @everyone role and get meaningful roles
        meaningful_roles = [role for role in roles if role.name != "@everyone"]
        
        # Get role hierarchy (top roles)
        top_roles = sorted(meaningful_roles, key=lambda r: r.position, reverse=True)[:10]
        
        # Categorize roles
        staff_roles = []
        special_roles = []
        member_roles = []
        
        for role in meaningful_roles:
            if any(perm in ['administrator', 'manage_guild', 'manage_channels', 'manage_messages'] 
                   for perm, value in role.permissions if value):
                staff_roles.append(role.name)
            elif role.mentionable or role.hoist:
                special_roles.append(role.name)
            else:
                member_roles.append(role.name)
        
        return {
            "total_roles": len(roles),
            "staff_roles": staff_roles[:5],  # Limit output
            "special_roles": special_roles[:8],
            "member_roles_count": len(member_roles),
            "top_roles": [role.name for role in top_roles[:5]]
        }
    except Exception as e:
        logging.error(f"Error getting roles info: {e}")
        return {
            "total_roles": len(guild.roles) if guild.roles else 0,
            "staff_roles": [],
            "special_roles": [],
            "member_roles_count": 0,
            "top_roles": []
        }

def _get_members_info(guild: Guild) -> Dict[str, Any]:
    """Extract member-related information from the guild."""
    try:
        # Note: In many cases, guild.members might not be fully populated
        # unless the bot has proper intents and permissions
        
        online_count = 0
        bot_count = 0
        
        if guild.members:
            for member in guild.members:
                if hasattr(member, 'status') and str(member.status) != 'offline':
                    online_count += 1
                if member.bot:
                    bot_count += 1
        
        return {
            "online_members": online_count if guild.members else "Unknown",
            "bot_count": bot_count,
            "human_members": (guild.member_count - bot_count) if guild.member_count else "Unknown"
        }
    except Exception as e:
        logging.error(f"Error getting members info: {e}")
        return {
            "online_members": "Unknown",
            "bot_count": 0,
            "human_members": guild.member_count or "Unknown"
        }

def _get_features_info(guild: Guild) -> Dict[str, Any]:
    """Extract server features and settings information."""
    try:
        features = []
        
        # Check for common Discord features
        if hasattr(guild, 'features'):
            feature_map = {
                'COMMUNITY': 'Community Server',
                'VERIFIED': 'Verified Server',
                'PARTNERED': 'Discord Partner',
                'DISCOVERABLE': 'Server Discovery',
                'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
                'MEMBER_VERIFICATION_GATE_ENABLED': 'Member Screening',
                'INVITE_SPLASH': 'Custom Invite Splash',
                'VANITY_URL': 'Custom Invite Link',
                'ANIMATED_ICON': 'Animated Server Icon',
                'BANNER': 'Server Banner'
            }
            
            for feature in guild.features:
                if feature in feature_map:
                    features.append(feature_map[feature])
        
        return {
            "server_features": features,
            "explicit_content_filter": str(guild.explicit_content_filter).replace('_', ' ').title(),
            "default_notifications": str(guild.default_notifications).replace('_', ' ').title(),
            "mfa_level": "Required" if guild.mfa_level else "Not Required"
        }
    except Exception as e:
        logging.error(f"Error getting features info: {e}")
        return {
            "server_features": [],
            "explicit_content_filter": "Unknown",
            "default_notifications": "Unknown",
            "mfa_level": "Unknown"
        }

def generate_context_from_guild(guild: Guild) -> str:
    """
    Generates comprehensive server context string with detailed information
    formatted for AI consumption.
    
    Args:
        guild: Discord guild object containing server information
        
    Returns:
        Formatted string containing comprehensive server information
    """
    info = get_server_info(guild)
    
    # Build context sections
    context_sections = []
    
    # Basic Information Section
    basic_section = f"""BASIC SERVER INFORMATION:
    Server Name: {info['name']}
    Created On: {info['created_at']}
    Server ID: {info['id']}
    Total Members: {info['member_count']}
    Verification Level: {info.get('verification_level', 'Unknown')}
    general server info: 
    🎮 Overview of THE RALS
    •	Server Name: THE RALS
    •	Creation Date: March 9, 2021
    •	Member Count: Approximately 4344 members
    •	Online Users: Around 2048 online at a time
    •	Language: English, Hindi, Urdu
    •	Region: Global
    •	Invite Link: discord.gg/therals

    THE RALS is designed as a safe and inclusive community for making friends, chilling, and enjoyment under one roof. It welcomes everyone regardless of age, gender, religion, etc. The server offers a variety of activities, including movie nights, song sessions, voice chat sessions, gaming, and daily streams. It also hosts fun events, activities, and weekly tournaments. Additionally, THE RALS has its own gaming clan that members can benefit from.


    👥 Staff & Community Structure
    the server is described as having a dedicated staff that actively moderates daily to ensure a chill and safe environment for everyone. 
    Owners/Founders: Kat ( Pakistani ) , Anu and Tribb (Indian)
    Co-Owner: Muski ( Pakistani/Canadian )

    Admins: Asad, Liam, Todo

    Moderator: Sarurah

    Staff and Tournament Manager: botMAN

    Community Features
    •	Events & Activities:
    o	Movie Nights
    o	Game Nights
    o	Tournaments with great prizes
    o	Daily fun activities
    o	QOTD (Question of the Day)
    o	Polls
    Channels & Bots:
    •	Dedicated text channels for various topics
    •	Separate and numerous voice channels for each topic
    •	Fun bots like Dank Memer, Idle RPG, etc.

    Community Engagement:
    •	Welcoming and friendly public community
    •	Supportive environment for gamers, content creators, and individuals seeking support
    Encouragement for sharing artistic creations and helping with school work

    📌 Organizational Highlights
    •	Inclusivity: THE RALS embraces diversity and welcomes everyone with open arms, regardless of age, sexuality, race, or religion. 
    •	Level 3 Perks: The server has achieved Level 3 perks, indicating a high level of community engagement and support. 
    •	Gaming Clan: Members can benefit from THE RALS' own gaming clan, which provides additional opportunities for collaboration and competition. 

    🏆 THE RALS: A Rising Esports Organization with a Thriving Community and Big Ambitions
    THE RALS is not just a popular Discord server — it's an emerging esports organization rooted in community, competition, and creativity. Known for hosting regular tournaments, engaging events, and supporting a wide range of competitive games, THE RALS has quickly built a name for itself within the Pakistani gaming scene. The organization has successfully run weekly events, scrims, and clan wars across titles like Valorant, PUBG, with participation from both amateur and semi-pro players.
    In the near future, THE RALS plans to:
    •	Launch official esports rosters across multiple games.
    •	Collaborate with influencers and streamers to expand its reach.
    •	Host sponsored tournaments with cash prizes and brand partnerships.
    •	Develop a content creation wing featuring YouTube and Twitch streams.
    •	Establish a mentorship and coaching program for rising talent in the community.
    Backed by an engaged team and a passionate player base, THE RALS is on track to become a major force in the regional esports ecosystem.


"""
    
    if info.get('description'):
        basic_section += f"\nServer Description: {info['description']}"
    
    context_sections.append(basic_section)
    
    # Server Features Section
    if info.get('server_features') or info.get('boost_level', 0) > 0:
        features_section = "SERVER FEATURES & SETTINGS:"
        
        if info.get('boost_level', 0) > 0:
            features_section += f"\nBoost Level: {info['boost_level']} (from {info.get('boost_count', 0)} boosts)"
        
        if info.get('server_features'):
            features_section += f"\nSpecial Features: {', '.join(info['server_features'])}"
        
        features_section += f"\nContent Filter: {info.get('explicit_content_filter', 'Unknown')}"
        features_section += f"\nDefault Notifications: {info.get('default_notifications', 'Unknown')}"
        features_section += f"\n2FA Requirement: {info.get('mfa_level', 'Unknown')}"
        
        context_sections.append(features_section)
    
    # Channels Section
    channels_section = f"""CHANNELS INFORMATION:
Total Channels: {info.get('total_channels', 0)}
Text Channels: {info.get('text_channels_count', 0)}
Voice Channels: {info.get('voice_channels_count', 0)}
Categories: {info.get('categories_count', 0)}"""
    
    if info.get('notable_channels'):
        channels_section += "\n\nNotable Channels:"
        for channel in info['notable_channels'][:5]:  # Limit to prevent overwhelming
            channels_section += f"\n  • #{channel['name']}"
            if channel.get('topic'):
                channels_section += f": {channel['topic']}"
    
    context_sections.append(channels_section)
    
    # Roles Section
    if info.get('total_roles', 0) > 1:  # More than just @everyone
        roles_section = f"ROLES & PERMISSIONS:\nTotal Roles: {info['total_roles']}"
        
        if info.get('staff_roles'):
            roles_section += f"\nStaff Roles: {', '.join(info['staff_roles'])}"
        
        if info.get('special_roles'):
            roles_section += f"\nSpecial Roles: {', '.join(info['special_roles'])}"
        
        if info.get('top_roles'):
            roles_section += f"\nTop Hierarchy Roles: {', '.join(info['top_roles'])}"
        
        context_sections.append(roles_section)
    
    # Members Section
    members_section = f"""COMMUNITY INFORMATION:
Total Members: {info['member_count']}
Human Members: {info.get('human_members', 'Unknown')}
Bots: {info.get('bot_count', 0)}"""
    
    if info.get('online_members') != "Unknown":
        members_section += f"\nCurrently Online: {info['online_members']}"
    
    context_sections.append(members_section)
    
    # Add error notice if there was an issue
    if info.get('error'):
        context_sections.append(f"NOTE: {info['error']}")
    
    return "\n\n".join(context_sections)

def validate_guild_for_context_generation(guild: Guild) -> bool:
    """
    Validates that the guild object is suitable for context generation.
    
    Args:
        guild: Discord guild object to validate
        
    Returns:
        Boolean indicating if guild is valid for processing
    """
    if not guild:
        return False
    
    required_attributes = ['name', 'id', 'created_at']
    
    for attr in required_attributes:
        if not hasattr(guild, attr) or getattr(guild, attr) is None:
            logging.warning(f"Guild missing required attribute: {attr}")
            return False
    
    return True

def get_server_context_summary(guild: Guild) -> str:
    """
    Generates a concise summary of server information for quick reference.
    
    Args:
        guild: Discord guild object
        
    Returns:
        Brief summary string of key server information
    """
    if not validate_guild_for_context_generation(guild):
        return f"Server: {getattr(guild, 'name', 'Unknown')} (Limited information available)"
    
    info = get_server_info(guild)
    
    summary_parts = [
        f"**{info['name']}**",
        f"{info['member_count']} members",
        f"Created {info['created_at']}"
    ]
    
    if info.get('boost_level', 0) > 0:
        summary_parts.append(f"Level {info['boost_level']} boosted")
    
    if info.get('server_features'):
        summary_parts.append(f"Features: {', '.join(info['server_features'][:2])}")
    
    return " • ".join(summary_parts)