import discord
from src.components.agents.GroqAgent import agent
from src.components.utils.intentClassifier import classify_intent, is_helpful_channel

async def search_messages_for_help(guild: discord.Guild, message: discord.Message, limit_per_channel=10):
    collected = []

    for channel in guild.text_channels:
        if not isinstance(channel, discord.TextChannel):
            continue

        # Use channel topic if available
        topic = channel.topic or ""

        try:
            if not is_helpful_channel(channel.name, message, topic):
                print(f"⛔ Skipping unhelpful channel: {channel.name}")
                continue

            print(f"🔍 Searching in helpful channel: {channel.name}")
            async for message in channel.history(limit=limit_per_channel):
                if not message.author.bot:
                    intent = classify_intent(message.content)
                    if intent == "user_wants_help":
                        collected.append((channel.name, message.author.display_name, message.content))

        except Exception as e:
            print(f"⚠️ Error in channel {channel.name}: {e}")
            continue

    return collected

async def handle_help_request(message: discord.Message):
    guild = message.guild
    help_messages = await search_messages_for_help(guild, message)

    if not help_messages:
        await message.channel.send(f"{message.author.mention} I couldn't find any unresolved help queries in the server.")
        return

    combined = "\n".join(
        f"[#{ch}] {author}: {content}" for ch, author, content in help_messages[:10]
    )

    help_summary_prompt = f"""
            The user said: '{message.content}'.
            Here are some recent messages where users seemed to need help:

            {combined}

            Based on the above, offer a useful, helpful response if you can, or summarize what kinds of help people seem to need.
            """

    response = agent.run(message=help_summary_prompt)
    await message.channel.send(f"{message.author.mention} {getattr(response, 'content', '🤖 I tried, but couldn’t generate a helpful answer.')}")
