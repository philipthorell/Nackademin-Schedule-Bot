import discord
from discord.ext import tasks
from dotenv import load_dotenv

from datetime import date
import os
import logging

import scrape


load_dotenv()


# För test
# 2025-10-14 branschdag
# 2025-10-15 digitalundervisning
# 2025-10-21 affärsmannaskap
# 2025-10-24 pythonprogrammering
# 2025-11-06 databasteknik
# 2025-12-04 devops
# 2025-12-10 affärsmannaskap (fler klasser)
#today = "2025-12-04"
today = str(date.today())

school_info = scrape.get_schoolday_info(today)

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.getLogger("discord.client").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
log = logging.getLogger("DiscordBot")


intents = discord.Intents.default()
bot = discord.Client(intents=intents)

course = school_info["course"].lower()
if "pythonprogrammering" in course:
    color = discord.Color.blue()        # blue
elif "affärsmannaskap" in course:
    color = discord.Color.green()       # green
elif "databasteknik" in course:
    color = discord.Color.orange()      # orange
elif "devops" in course:
    color = discord.Color.light_gray()  # light gray
else:
    color = discord.Color.purple()      # purple


@tasks.loop(hours=24)
async def daily_schedule():
    channel = bot.get_channel(CHANNEL_ID)

    time = f"{school_info['time_1']} - lunch - {school_info['time_2']}" if school_info["time_2"] else school_info["time_1"]

    description = "\u200b\n"
    description += f"**• 📚 Kurs:** {school_info['course']}\n\n"
    description += f"**• 👨‍🏫 Lärare:** {school_info['teacher']}\n\n" if school_info["teacher"] else ""
    description += f"**• 🏫 Sal:** {school_info['classroom']}\n\n" if school_info["classroom"] else ""
    description += f"**• ⏰ Tid:** {time}\n\n"
    description += f"**• 👥 Klasser:** {school_info['class_group']}" if school_info["class_group"].lower() != "pia25" else ""

    embed = discord.Embed(
        title=f"📅 Dagens Schema! ({school_info['weekday']}, {school_info['date']})",
        description=description,
        color=color
    )

    await channel.send(embed=embed)
    log.info(
        "Sent message: "
        f"{school_info['weekday']} ({school_info['date']}) | "
        f"course: {school_info['course']} | "
        f"teacher: {school_info['teacher']} | "
        f"classroom: {school_info['classroom']} | "
        f"time: {school_info['time_1']} - lunch - {school_info['time_2']} | "
        f"class-group: {school_info['class_group']}"
    )


@bot.event
async def on_ready():
    log.info("Discord bot is running!")
    daily_schedule.start()


if __name__ == "__main__":
    log.info("Starting discord bot...")
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        log.error(f"Bot crashed with exception: {e}", exc_info=True)
    finally:
        log.info("Program exited!")
