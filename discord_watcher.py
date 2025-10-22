# discord_watcher.py
import discord

from dotenv import load_dotenv
import os

# Get tokens and ids from .env file
load_dotenv()  # loads
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
USER_ID = os.getenv('USER_ID')

# Discord Watcher

class MyDiscordBot(discord.Client):
    async def on_ready(self):
        print(f"✅ Logged in as {self.user}")

    async def on_message(self, message):
        # Prevent self-replies
        if message.author == self.user:
            return

        # Example: respond when you message the bot
        if message.content.lower().startswith("ping"):
            await message.channel.send("Pong!")
        elif message.content.lower().startswith("status"):
            await message.channel.send("📬 Watching your inbox...")

def run_discord_bot():
    intents = discord.Intents.default()
    intents.messages = True
    bot = MyDiscordBot(intents=intents)
    bot.run(BOT_TOKEN)