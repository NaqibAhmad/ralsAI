from agno.agent import Agent
from agno.models.groq import Groq
import os

import discord

# A separate low-temp model just for classification (or reuse your agent)
intent_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0),
    tools=[],
    instructions=f"""
        ### ROLE & CONTEXT:
        "You are an expert intent classifier for Discord messages. Analyze the message content and context carefully."
        "Your task is to classify each message into exactly ONE of these four intents based on the PRIMARY PURPOSE of the message:"

        
        #INTENT DEFINITIONS:
        1. **user_wants_help** - set the intent to `user_want_help` only when the below mentioned keywords are present in the message and the user is asking for help or assistance with a specific problem or question"
            - KEYWORDS: " 'HELP:', 'help me' 'how do I' 'can you help' 'I'm stuck' 'problem with' 'need assistance'"
        
        2. **server_info** - set the intent to `server_info` only when The user is asking for general information about THIS Discord server's structure/settings"
            - Examples: 'What are the server rules?' 'How many members are here?' 'What channels do we have?' 'Who are the mods?'"
            - FOCUS: Server configuration rules structure - NOT specific events or activities with detailed answers"
        
        3. **user_info** - set the intent to `user_info` only when The user is requesting specific information ABOUT another user/member"
            - Examples: 'What's John's timezone?' 'When did Sarah join?' 'What's Mike's role here?' 'What activity is Nikki doing?'"
            - CRITICAL: Only classify as user_info if the PRIMARY intent is to GET information ABOUT someone"
        
        4. **general** - set the intent to `general` for All other messages including casual conversation statements jokes greetings casual questions or reactions"
            - Examples: 'Hello everyone' 'That's funny!' 'Good morning' '@user thanks for that info'"
        
            
        #IMPORTANT CLASSIFICATION RULES:
        
        **TAGGING RULES (Critical)**:
        - If someone tags a user but is NOT asking for information ABOUT that user → classify based on actual intent
        - '@user thanks' → 'general' (expressing gratitude)
        - '@user you should see this' → 'general' (sharing/informing)
        - '@user can you help?' → 'user_wants_help' (seeking assistance)
        - '@user what's your favorite color?' → 'user_info' (asking about the user)
        - 'Tell @user about the event' → 'general' (instruction/request not asking about the user)
        
        **CONTEXT ANALYSIS**:
        - Look at the MAIN ACTION the user wants to happen
        - Distinguish between mentioning someone vs asking about someone
        - Consider if the tagged person is the target of information gathering vs just being addressed
        
        **DECISION PROCESS**:
        1. What is the user's PRIMARY goal with this message?
        2. Are they asking FOR something or just communicating?
        3. If asking what type of information or action do they want?
        4. Does mentioning/tagging someone mean they want info ABOUT that person?
        
        OUTPUT FORMAT:
        Respond with ONLY one of these exact words: user_wants_help, server_info, user_info, general
        No explanations no punctuation no extra text whatsoever.
        When in doubt between two intents choose 'general' as the safe default.
 
        REMEMBER: Tags/mentions do NOT automatically mean user_info. Focus on what the user actually wants to achieve.
    """,
    show_tool_calls=True,
    markdown=False,
)

async def classify_intent(message: str) -> str:
    try:
        result = await intent_agent.arun(message=f"Classify this message: '{message}'")
        intent = getattr(result, "content", "general").strip().lower()
        if intent not in ["user_wants_help","server_info", "user_info", "general"]:
            return "general"
        return intent
    except Exception as e:
        print("Intent classification error:", e)
        return "general"


# DYANMIC CHANNEL CLASSIFICATION
async def is_helpful_channel(channel_name: str, message: str, topic: str = "") -> bool:
    from agno.agent import Agent
    from agno.models.groq import Groq
    import os
    print("Message in Params from User: ", message)

    classifier = Agent(
        model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0),
        tools=[],
        instructions= [
            # Clear role and context
            "You are a Discord channel classifier.",
            "Your job is to determine if a specific Discord channel would likely contain helpful information for a user's question.",
            
            # Decision criteria
            "DECISION CRITERIA:",
            "Answer 'yes' if the channel name or topic suggests it contains:",
            "- Help or support content",
            "- Information relevant to the user's question",
            "- Resources or guides related to the query",
            "- Q&A or discussion about similar topics",
            "- Sometimes casual chat such as 'general' and 'announcements' channels can be helpful",
            
            "Answer 'no' if the channel appears to be for:",
            "- Casual chat or off-topic discussion",
            "- Specific games or activities unrelated to the query",
            "- Announcements only",
            "- Private or restricted content",
            
            # Output format
            "IMPORTANT: Respond with only 'yes' or 'no'.",
            "No explanations or additional text.",
            "If uncertain, answer 'no'."
        ],
        show_tool_calls=False,
        markdown=False,
    )

    prompt =  f"""
        CHANNEL ANALYSIS:
        Channel Name: "{channel_name}"
        Channel Topic: "{topic if topic else 'No topic set'}"
        User's Question: "{message}"

        Would this channel likely contain helpful information for this user's question?
        Answer: 
        """
    
    try:
        result = await classifier.arun(message=prompt)
        answer = getattr(result, "content", "").strip().lower()
        return answer == "yes"
    except Exception as e:
        print(f"Channel help detection error: {e}")
        return False
    
async def is_helpful_category(category_name: str, message: str,) -> bool:
    from agno.agent import Agent
    from agno.models.groq import Groq
    import os
    print("Message in Params from User: ", message)

    classifier = Agent(
        model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0),
        tools=[],
        instructions= f"""
            "You are a classifier that determines if a Discord Guild Category is likely to contain messages that are helpful or support questions regarding the user query: '{message}'.
            "Your task is to analyze the category name and user's message, and decide if the category is likely to contain helpful messages or support questions.
            "Return 'yes' if the category is likely to contain helpful messages or support questions. Return 'no' otherwise.",
            "Only return 'yes' or 'no'."
        """,
        show_tool_calls=False,
        markdown=False,
    )

    prompt = f"""
    Category name: {category_name}
    Is this category likely to contain help-related messages: {message}? (yes/no)
    """
    
    try:
        result = await classifier.arun(message=prompt)
        answer = getattr(result, "content", "").strip().lower()
        return answer == "yes" # returns Bool True if answer contains yes else returns False
    except Exception as e:
        print(f"Channel help detection error: {e}")
        return False
