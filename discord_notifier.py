# discord_notifier.py
import discord
import asyncio
from dotenv import load_dotenv
import os

# Get tokens and ids from .env file
load_dotenv()  # loads
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

# Singleton client (so we don't reconnect every time)
_client = None

async def _get_client():
    global _client
    if _client is None:
        intents = discord.Intents.default()
        _client = discord.Client(intents=intents)

        # Start the client in the background
        asyncio.create_task(_client.start(BOT_TOKEN))

        # Wait until it's connected
        while not _client.is_ready():
            await asyncio.sleep(1)

    return _client


async def _send_async(message):
    client = await _get_client()
    user = await client.fetch_user(USER_ID)
    if user:
        await user.send(message)
    else:
        print("⚠️ Could not find user! Check USER_ID.")


def send_discord_message(message):
    """
    Call this safely from any normal (non-async) Python code.
    It automatically handles the asyncio parts.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        asyncio.create_task(_send_async(message))
    else:
        asyncio.run(_send_async(message))