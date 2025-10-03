import discord
from discord.ext import tasks
from dotenv import load_dotenv

from datetime import date
import os
import logging

import scrape


load_dotenv()


#today = str(date.today())
today = "2025-10-14"

school_info = scrape.get_schoolday_info(today)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("DiscordBot")


intents = discord.Intents.default()
bot = discord.Client(intents=intents)


class DisplayInfo(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)


@tasks.loop(hours=24)
async def daily_schedule():
    log.info(f"{school_info["weekday"]} ({school_info["date"]}) | "
             f"course: {school_info["course"]} | "
             f"teacher: {school_info["teacher"]} | "
             f"classroom: {school_info["classroom"]} | "
             f"time: {school_info["time_1"]} - lunch - {school_info["time_2"]}")

    channel = bot.get_channel(CHANNEL_ID)
    embed = discord.Embed(
        title="📅 Dagens Schema!",
        description=f"**Här är dagens schema ({school_info["weekday"]}, {school_info["date"]}):**",
        color=discord.Color.blue()
    )
    embed.add_field(name="Kurs", value=school_info["course"], inline=False)
    if school_info["teacher"]:
        embed.add_field(name="Lärare", value=school_info["teacher"], inline=False)
    if school_info["classroom"]:
        embed.add_field(name="Sal", value=school_info["classroom"], inline=False)
    embed.add_field(name="Tid", value=f"{school_info["time_1"]} - lunch - {school_info["time_2"]}", inline=False)
    await channel.send(embed=embed)


@bot.event
async def on_ready():
    daily_schedule.start()


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
