import discord

from datetime import date, datetime, timedelta
import asyncio
import os
import logging
import sys

import scrape


# Gets the discord token and the discord channel id from .env file
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # ensures the folder exists inside container

# Setup basic logging config, and save logs to a file
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("logs/bot.log", encoding="utf-8"),  # Save logs to a file
        logging.StreamHandler(sys.stdout)                               # To view logs live
    ]
)
# Suppress the standard logs from the discord bot, and make a log object to write logs with
logging.getLogger("discord.client").setLevel(logging.WARNING)
logging.getLogger("discord.gateway").setLevel(logging.WARNING)
log = logging.getLogger("DiscordBot")

# Give the bot basic intents to only send messages
intents = discord.Intents.default()
bot = discord.Client(intents=intents)


def get_color(course: str):
    """
    Returns a color to use for the bot message-embed, depending on what course it is
    :param course: String with the current course for today
    :return: Discord-Color object
    """
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
    """
    Runs the scraping and bot every day at 6:00 in the morning.
    Starts by sleeping until 6:00, then scrapes the schedule website,
    and finally sends a discord message with the information about today's
    lecture, if there is a lecture for today
    :return: None
    """
    # Wait for the bot to be fully ready before entering the while loop
    await bot.wait_until_ready()
    while not bot.is_closed():
        # Create a datetime object for the current time, and the target time
        now = datetime.now()
        target_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

        # if 6:00 has already passed today, then schedule for tomorrow
        if now >= target_time:
            target_time += timedelta(days=1)

        # Get the time to wait in seconds and sleep for that long
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)

        # For quick testing
        # 2025-10-14 branschdag
        # 2025-10-15 digitalundervisning
        # 2025-10-21 affärsmannaskap
        # 2025-10-24 pythonprogrammering
        # 2025-11-06 databasteknik
        # 2025-12-04 devops
        # 2025-12-10 affärsmannaskap (fler klasser)
        # today = "2025-12-04"

        # Get the date for today and the scraped information
        today = str(date.today())
        school_info = scrape.get_schoolday_info(today)

        # Get the channel to send the message in
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            log.error(f"Couldn't find discord channel ({channel})")
        elif channel and school_info:
            # Get the color for the message embed
            color = get_color(school_info["course"].lower())

            # Add the second tags time if there was an associated second tag
            time = f"{school_info['time_1']} - lunch - {school_info['time_2']}" if school_info["time_2"] else school_info["time_1"]

            # Create the description for the message embed
            description = "\u200b\n"  # "\u200b" is an invisible character
            description += f"**• 📚 Kurs:** {school_info['course']}\n\n"
            description += f"**• 👨‍🏫 Lärare:** {school_info['teacher']}\n\n" if school_info["teacher"] else ""
            description += f"**• 🏫 Sal:** {school_info['classroom']}\n\n" if school_info["classroom"] else ""
            description += f"**• ⏰ Tid:** {time}\n\n"
            description += f"**• 👥 Klasser:** {school_info['class_group']}" if school_info["class_group"].lower() != "pia25" else ""

            # Create the embed for the discord message
            embed = discord.Embed(
                title=f"📅 Dagens Schema! ({school_info['weekday']}, {school_info['date']})",
                description=description,
                color=color
            )

            # Send schedule message
            await channel.send(embed=embed)

            # Log the information that was sent
            log.info(
                "Sent message: "
                f"{school_info['weekday']} ({school_info['date']}) | "
                f"course: {school_info['course']} | "
                f"teacher: {school_info['teacher']} | "
                f"classroom: {school_info['classroom']} | "
                f"time: {school_info['time_1']} - lunch - {school_info['time_2']} | "
                f"class-group: {school_info['class_group']}"
            )
        else:
            log.info("No lecture for today")


@bot.event
async def on_ready():
    """
    This function runs when the discord bot is up and running for the first time
    :return: None
    """
    log.info("Discord bot is running!")
    # Create a task for the daily scraping & message sending
    bot.loop.create_task(daily_schedule_task())


if __name__ == "__main__":
    version = "1.0.0"
    log.info(f"Starting discord bot version=[{version}]")

    # Run the discord bot and log if there is a crash, or the program just exits
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        log.error(f"Bot crashed with exception: {e}", exc_info=True)
    finally:
        log.info("Program exited!")
