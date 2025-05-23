from typing import List
import discord
from src.components.agents.GroqAgent import agent
from src.components.utils.intentClassifier import is_helpful_category, is_helpful_channel

async def search_messages_for_help(guild: discord.Guild, message: discord.Message, limit_per_channel=50):
    collected = []

    helpful_category: List[discord.CategoryChannel] = []
    for category in guild.categories:
        try:
            if not await is_helpful_category(category.name, message.content):
                print(f"⛔ Skipping unhelpful category: {category.name}")
                continue

            print(f"🔍 Helpful category found: {category.name}")
            helpful_category.append(category)
            
        except Exception as e:
            print(f"⚠️ Error in category {category.name}: {e}")
            continue

    if not helpful_category:
        print("⚠️ No helpful category found")
        return collected

    for category in helpful_category:
        for channel in category.text_channels:
            topic = channel.topic or ""
            try:
                if not await is_helpful_channel(channel.name, message.content, topic):
                    print(f"⛔ Skipping unhelpful channel: {channel.name}")
                    continue

                print(f"🔍 Searching in helpful channel: {channel.name}")
                async for channelMessage in channel.history(limit=limit_per_channel):
                    # Skip own bot messages
                    if channelMessage.author.id == guild.me.id:
                        continue

                    # Start with text content
                    text_content = channelMessage.content.strip()

                    # Extract embed content
                    embed_content = ""
                    for embed in channelMessage.embeds:
                        title = embed.title or ""
                        desc = embed.description or ""
                        fields = "\n".join(f"{f.name}: {f.value}" for f in embed.fields)
                        embed_content += f"{title}\n{desc}\n{fields}\n"

                    full_content = (text_content + "\n" + embed_content).strip()

                    if full_content:
                        sender_type = "BOT" if channelMessage.author.bot else "USER"
                        print(f"📩 Message detected from {sender_type} ({channelMessage.author.display_name}): {full_content}")
                        collected.append((channel.name, channelMessage.author.display_name, full_content))

            except Exception as e:
                print(f"⚠️ Error in channel {channel.name}: {e}")
                continue

    print("✅ COLLECTED MESSAGES:", collected)
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

    response = await agent.arun(message=help_summary_prompt)
    await message.channel.send(f"{message.author.mention} {getattr(response, 'content', '🤖 I tried, but couldn’t generate a helpful answer.')}")
    print("REQUEST HANDLED")