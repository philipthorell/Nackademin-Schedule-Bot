import asyncio
import discord

from datetime import date, datetime, timedelta
import os
import logging

import scrape


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

def get_color(course):
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

    return color


async def daily_schedule_task():
    await bot.wait_until_ready()
    while not bot.is_closed():
        now = datetime.now()
        target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)

        # if 6:00 has already passed today, then schedule for tomorrow
        if now >= target_time:
            target_time += timedelta(days=1)

        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        # För test
        # 2025-10-14 branschdag
        # 2025-10-15 digitalundervisning
        # 2025-10-21 affärsmannaskap
        # 2025-10-24 pythonprogrammering
        # 2025-11-06 databasteknik
        # 2025-12-04 devops
        # 2025-12-10 affärsmannaskap (fler klasser)
        # today = "2025-12-04"
        today = str(date.today())
        school_info = scrape.get_schoolday_info(today)

        # Send schedule message
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            log.error(f"Couldn't find discord channel ({channel})")
        elif channel and school_info:
            color = get_color(school_info["course"].lower())

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
    bot.loop.create_task(daily_schedule_task())


if __name__ == "__main__":
    log.info("Starting discord bot...")
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        log.error(f"Bot crashed with exception: {e}", exc_info=True)
    finally:
        log.info("Program exited!")
