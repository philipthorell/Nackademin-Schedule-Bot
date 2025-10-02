import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

from datetime import date
import os
import logging

import scrape


load_dotenv()


today = str(date.today())

school_info = scrape.get_schoolday_info(today)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("DiscordBot")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


class DisplayInfo(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


@tasks.loop(hours=24)
async def daily_schedule():
    channel = bot.get_channel(CHANNEL_ID)
    embed = discord.Embed(
        title="📅 Daily Schedule",
        description="Here’s today’s plan:",
        color=discord.Color.blue()
    )
    embed.add_field(name="Monday", value="Math", inline=False)
    embed.add_field(name="Tuesday", value="Physics", inline=False)
    embed.add_field(name="Wednesday", value="Programming", inline=False)
    await channel.send(embed=embed)


@bot.event
async def on_ready():
    daily_schedule.start()


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
