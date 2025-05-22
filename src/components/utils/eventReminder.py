import asyncio
import re
from datetime import datetime, timedelta
from discord import Message, TextChannel, User

# In-memory store (could be replaced with DB later)
scheduled_reminders = []

REMINDER_REGEX = re.compile(r"remind me to (.+?) in (\d+) (second|seconds|minute|minutes|hour|hours|day|days)", re.IGNORECASE)

async def handle_event_or_reminder(message: Message) -> bool:
    content = message.content.lower()

    reminder_match = REMINDER_REGEX.search(content)
    if reminder_match:
        task = reminder_match.group(1).strip()
        amount = int(reminder_match.group(2))
        unit = reminder_match.group(3)

        delay_seconds = convert_to_seconds(amount, unit)
        remind_time = datetime.utcnow() + timedelta(seconds=delay_seconds)

        scheduled_reminders.append({
            'user': message.author,
            'channel': message.channel,
            'task': task,
            'time': remind_time
        })

        await message.channel.send(f"⏰ Okay {message.author.mention}, I will remind you to '{task}' in {amount} {unit}.")
        asyncio.create_task(send_reminder(message.author, message.channel, task, delay_seconds))

        return True

    return False


def convert_to_seconds(amount: int, unit: str) -> int:
    unit = unit.lower()
    if 'second' in unit:
        return amount
    elif 'minute' in unit:
        return amount * 60
    elif 'hour' in unit:
        return amount * 3600
    elif 'day' in unit:
        return amount * 86400
    return amount


async def send_reminder(user: User, channel: TextChannel, task: str, delay: int):
    await asyncio.sleep(delay)
    await channel.send(f"🔔 Hey {user.mention}, just a reminder to: {task}")
