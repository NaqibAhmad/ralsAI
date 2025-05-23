from agno.agent import Agent
from agno.models.groq import Groq
import os

# A separate low-temp model just for classification (or reuse your agent)
intent_agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"), temperature=0),
    tools=[],
    instructions=[
        "You are an intent classifier. Your job is to classify the user's query into one of the following categories: "
        "'server_info', 'user_info', or 'general'. "
        " Some discord users might change their usernames, so use the user ID to identify them. "
        "Only return the classification keyword without explanation."
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

def classify_intent(message: str) -> str:
    try:
        result = intent_agent.run(message=f"Classify this message: '{message}'")
        intent = getattr(result, "content", "general").strip().lower()
        if intent not in ["user_wants_help","server_info", "user_info", "general"]:
            return "general"
        return intent
    except Exception as e:
        print("Intent classification error:", e)
        return "general"


# DYANMIC CHANNEL CLASSIFICATION
def is_helpful_channel(channel_name: str, message: str, topic: str = "") -> bool:
    from agno.agent import Agent
    from agno.models.groq import Groq
    import os

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
    Is this channel likely to contain help-related messages? (yes/no)
    """
    
    try:
        result = classifier.run(message=prompt)
        answer = getattr(result, "content", "").strip().lower()
        return answer == "yes"
    except Exception as e:
        print(f"Channel help detection error: {e}")
        return False
