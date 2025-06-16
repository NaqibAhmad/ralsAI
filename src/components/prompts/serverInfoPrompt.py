import re
import logging
from typing import Dict, Any
from src.components.utils.serverInfo import generate_context_from_guild
import discord

def generate_server_prompt(message: str, guild: discord.Guild) -> str:
    """
    Generates an enhanced prompt for server information queries with comprehensive
    context and clear instructions for AI responses.
    
    Args:
        message: User's original query about the server
        guild: Discord guild object containing server information
        
    Returns:
        Enhanced prompt string with server context and response instructions
    """
    
    # Analyze the user's query for better response targeting
    query_analysis = _analyze_server_query(message)
    
    # Generate comprehensive server context
    server_context = generate_context_from_guild(guild)
    
    # Log debug information
    _log_server_query_debug(message, guild.name, query_analysis)
    
    # Create enhanced server information prompt
    return _create_enhanced_server_prompt(message, server_context, query_analysis, guild)

def _analyze_server_query(message: str) -> Dict[str, Any]:
    """
    Analyzes the user's query to determine what type of server information they're seeking.
    """
    message_lower = message.lower()
    
    # Define query patterns and their corresponding focus areas
    query_patterns = {
        'rules': r'\b(rules?|guidelines?|regulations?|policies?)\b',
        'channels': r'\b(channels?|rooms?|categories?)\b',
        'members': r'\b(members?|users?|people|population|count|how many)\b',
        'roles': r'\b(roles?|permissions?|ranks?|hierarchy)\b',
        'bots': r'\b(bots?|automations?|commands?)\b',
        'events': r'\b(events?|activities?|schedule|calendar)\b',
        'general_info': r'\b(about|info|information|describe|what is|tell me about)\b',
        'features': r'\b(features?|capabilities?|what can|available)\b',
        'moderation': r'\b(moderation|moderators?|mods?|staff|admins?)\b'
    }
    
    detected_topics = []
    for topic, pattern in query_patterns.items():
        if re.search(pattern, message_lower):
            detected_topics.append(topic)
    
    # Determine primary focus
    primary_focus = detected_topics[0] if detected_topics else 'general_info'
    
    # Detect question type
    question_indicators = {
        'what': r'\bwhat\b',
        'how': r'\bhow\b',
        'when': r'\bwhen\b',
        'where': r'\bwhere\b',
        'who': r'\bwho\b',
        'why': r'\bwhy\b',
        'can': r'\bcan\b',
        'is': r'\bis\b'
    }
    
    question_type = None
    for q_type, pattern in question_indicators.items():
        if re.search(pattern, message_lower):
            question_type = q_type
            break
    
    return {
        'detected_topics': detected_topics,
        'primary_focus': primary_focus,
        'question_type': question_type,
        'is_specific_query': len(detected_topics) <= 2,
        'message_length': len(message.split())
    }

def _log_server_query_debug(message: str, guild_name: str, analysis: Dict[str, Any]) -> None:
    """
    Logs server query analysis for debugging and monitoring.
    """
    logging.info(f"SERVER QUERY DEBUG:\n"
                f"Guild: {guild_name}\n"
                f"Query: '{message}'\n"
                f"Analysis: {analysis}")

def _create_enhanced_server_prompt(message: str, server_context: str, 
                                 query_analysis: Dict[str, Any], guild: discord.Guild) -> str:
    """
    Creates the final enhanced prompt with comprehensive instructions.
    """
    
    # Generate response instructions based on query analysis
    response_instructions = _generate_response_instructions(query_analysis)
    
    return f"""
        SERVER INFORMATION REQUEST:
        User Query: "{message}"
        Server: {guild.name}

        QUERY ANALYSIS:
        Primary Focus: {query_analysis['primary_focus'].replace('_', ' ').title()}
        Detected Topics: {', '.join(query_analysis['detected_topics']) if query_analysis['detected_topics'] else 'General'}
        Question Type: {query_analysis['question_type'] or 'Statement/General'}

        AVAILABLE SERVER DATA:
        {server_context}

        RESPONSE INSTRUCTIONS:
        {response_instructions}

        GENERAL GUIDELINES:
        1. Use a casual, friendly tone that matches Discord culture
        2. Be informative but not overwhelming
        3. If asked about something not in the server data, acknowledge what you don't know
        4. Use natural language and avoid overly formal responses
        5. Include relevant emojis if they enhance the message (but don't overuse)
        6. Keep responses concise unless detailed information is specifically requested

        RESPONSE STRUCTURE:
        - Start with a direct answer to their question
        - Include 2-3 most relevant pieces of information
        - End with a helpful note or invitation for more questions if appropriate
        - Aim for 1-3 sentences for simple queries, more for complex ones

        Generate your response now:
        """

def _generate_response_instructions(query_analysis: Dict[str, Any]) -> str:
    """
    Generates specific response instructions based on the query analysis.
    """
    primary_focus = query_analysis['primary_focus']
    
    # Focus-specific instructions
    focus_instructions = {
        'rules': """
        - Clearly explain the server rules or policies
        - If specific rules are asked about, focus on those
        - Mention where users can find complete rule information
        - Be clear and direct about what is/isn't allowed""",
                
        'channels': """
        - Describe the relevant channels or channel structure
        - Explain what each mentioned channel is used for
        - Help users understand where to find specific content
        - Mention any special channel features or restrictions""",
                
        'members': """
        - Provide member count or community information
        - Describe the community culture if relevant
        - Mention any special member roles or groups
        - Keep privacy in mind - don't share personal member details""",
                
        'roles': """
        - Explain the role system and hierarchy
        - Describe what different roles can do or represent
        - Mention how roles are obtained if asked
        - Focus on publicly available role information""",
                
        'bots': """
        - Describe available bots and their functions
        - Explain how to use bot commands if relevant
        - Focus on publicly available bot features
        - Be helpful about bot-related questions""",
                
        'events': """
        - Share information about server events or activities
        - Mention event schedules if available
        - Explain how users can participate
        - Be encouraging about community participation""",
                
        'moderation': """
        - Explain moderation policies and procedures
        - Describe the moderation team structure if asked
        - Be clear about reporting procedures
        - Maintain appropriate boundaries about mod-only information""",
                
        'features': """
        - Highlight key server features and capabilities
        - Explain what makes this server unique or special
        - Mention any special integrations or tools
        - Be enthusiastic but accurate about features""",
                
        'general_info': """
        - Provide a helpful overview of the server
        - Include the most relevant information for their query
        - Give them a good sense of what the server is about
        - Be welcoming and informative"""
            }
    
    base_instruction = focus_instructions.get(primary_focus, focus_instructions['general_info'])
    
    # Add question-type specific guidance
    if query_analysis['question_type']:
        question_guidance = {
            'what': "Focus on definitions and explanations",
            'how': "Provide step-by-step information or procedures", 
            'when': "Include timing, schedules, or time-related information",
            'where': "Focus on locations, channels, or where to find things",
            'who': "Provide information about people, roles, or responsible parties",
            'why': "Explain reasons, purposes, or motivations",
            'can': "Focus on permissions, capabilities, or possibilities",
            'is': "Provide confirmations, descriptions, or status information"
        }
        
        q_type = query_analysis['question_type']
        if q_type in question_guidance:
            base_instruction += f"\n- {question_guidance[q_type]}"
    
    return base_instruction

def validate_server_prompt_generation(guild: discord.Guild) -> bool:
    """
    Validates that the guild object is suitable for prompt generation.
    """
    return (guild is not None and 
            hasattr(guild, 'name') and 
            hasattr(guild, 'id'))

def get_server_query_categories() -> Dict[str, str]:
    """
    Returns available server query categories for help/documentation.
    """
    return {
        'rules': 'Server rules, guidelines, and policies',
        'channels': 'Channel information and organization', 
        'members': 'Community and member information',
        'roles': 'Role system and permissions',
        'bots': 'Available bots and commands',
        'events': 'Server events and activities',
        'moderation': 'Moderation policies and procedures',
        'features': 'Server features and capabilities',
        'general_info': 'General server information'
    }