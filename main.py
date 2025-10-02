import discord
from discord.ext import commands

from datetime import date
import os
import logging

from discord.app_commands import command

import scrape


today = str(date.today())

school_info = scrape.get_schoolday_info(today)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID =    os.getenv("CHANNEL_ID")

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("DiscordBot")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


class DisplayInfo(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")


@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
