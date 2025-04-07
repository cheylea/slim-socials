# discord_watcher.py
import discord
from telegram_notifier import send_telegram_message

from dotenv import load_dotenv
import os

# Get tokens and ids from .env file
load_dotenv()  # loads
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
TARGET_CHANNEL_IDS = os.getenv('TARGET_CHANNEL_IDS')

# Discord Watcher
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'[Discord] Logged in as {client.user}')

@client.event
async def on_message(message):
    if str(message.channel.id) in TARGET_CHANNEL_IDS and not message.author.bot:
        alert = f"DISCORD 🎮 [{message.guild.name} > #{message.channel.name}] {message.author.name}: {message.content}"

        if alert:
            send_telegram_message(alert)
        else:
            alert = f"[{message.guild.name} > #{message.channel.name}] {message.author.name}: Content blank"
            send_telegram_message(alert)

def run_discord_bot():
    client.run(DISCORD_BOT_TOKEN)