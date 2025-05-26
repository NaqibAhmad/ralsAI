from agno.agent import Agent
from agno.models.groq import Groq
import os

import discord

# A separate low-temp model just for classification (or reuse your agent)
intent_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0),
    tools=[],
    instructions=[
        # Clear role definition
        "You are an intent classifier for Discord messages.",
        
        # Explicit task description
        "Your job is to read a user's message and classify it into exactly one of these four categories:",
        "1. 'user_wants_help' - User is asking for help, assistance, or support with something",
        "2. 'server_info' - User is asking for information about the Discord server itself",
        "3. 'user_info' - User is asking for information about a specific user or member",
        "4. 'general' - Everything else (casual chat, jokes, random comments, etc.)",
        
        # Classification rules with examples
        "CLASSIFICATION RULES:",
        "- If message contains words like 'help', 'how do I', 'problem', 'issue', 'can someone help', 'stuck' → use 'user_wants_help'",
        "- If message asks about server rules, channels, bots, server features, member count → use 'server_info'",
        "- If message asks about a specific person's profile, status, or information → use 'user_info'",
        "- If message is greeting, joke, casual conversation, random comment → use 'general'",
        
        # Output format (critical for reliability)
        "IMPORTANT: You must respond with ONLY the classification keyword.",
        "Valid responses: user_wants_help, server_info, user_info, general",
        "Do not include explanations, punctuation, or extra words.",
        "If uncertain, default to 'general'."
    ],
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
