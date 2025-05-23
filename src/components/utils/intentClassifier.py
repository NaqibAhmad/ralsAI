from agno.agent import Agent
from agno.models.groq import Groq
import os

import discord

# A separate low-temp model just for classification (or reuse your agent)
intent_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0),
    tools=[],
    instructions=[
        """
            ### ENFORCED INSTRUCTIONS FOR INTENT CLASSIFICATION
                a. You are an intent classifier. Your job is to classify the user's query into one of the following categories:
                    - 'user_wants_help'
                    - 'server_info'
                    - 'user_info'
                    - 'general'
                b. Based on the user's message, determine if they are asking for help or assistance regarding something, or the user is asking for information about the server or a specific user.
                c. If the user is asking for help, classify it as 'user_wants_help'. If the user is asking for information about the server, classify it as 'server_info'. If the user is asking for information about a specific user, classify it as 'user_info'. If none of these apply, classify it as 'general'.
                d. Only return the classification keyword without explanation.
        
            """
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
        instructions= f"""
            "You are a classifier that determines if a Discord channel is likely to contain messages that are helpful or support questions regarding the user query: '{message}'.
            "Your task is to analyze the channel name and topic, and decide if the channel is likely to contain helpful messages or support questions.
            "Return 'yes' if the channel is likely to contain helpful messages or support questions. Return 'no' otherwise.",
            "Only return 'yes' or 'no'."
        """,
        show_tool_calls=False,
        markdown=False,
    )

    prompt = f"""
    Channel name: {channel_name}
    Channel topic: {topic}
    Is this channel likely to contain help-related messages about the user query? : {message} (yes/no)
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
