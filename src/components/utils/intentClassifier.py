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
    ],
    show_tool_calls=True,
    markdown=False,
)

def classify_intent(message: str) -> str:
    try:
        result = intent_agent.run(message=f"Classify this message: '{message}'")
        intent = getattr(result, "content", "general").strip().lower()
        if intent not in ["server_info", "user_info", "general"]:
            return "general"
        return intent
    except Exception as e:
        print("Intent classification error:", e)
        return "general"
