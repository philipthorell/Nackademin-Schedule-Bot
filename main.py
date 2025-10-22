import discord

from datetime import date, datetime, timedelta
import asyncio
import os
import logging
import sys
import signal

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


def handle_shutdown(signal_number, frame):
    """
    Handles the shutdown of the program, when Docker container is stopped
    :param signal_number: Integer of the signal status-code
    :param frame: Unknown
    :return: None
    """
    log.info("🔴 Shutting down Discord bot!")
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Schedule async cleanup - don't block the signal handler
            asyncio.create_task(shutdown_bot())
        else:
            # If loop isn't running, close it synchronously
            loop.run_until_complete(shutdown_bot())
    except Exception as e:
        log.error(f"⚠️ Error during shutdown: {e}", exc_info=True)


async def shutdown_bot():
    """
    Handles the shutdown of the discord-bot
    :return: None
    """
    if bot.is_closed():
        return
    try:
        await bot.close()
    except Exception as e:
        log.error(f"⚠️ Error while closing Discord bot: {e}", exc_info=True)


# Give the bot basic intents to only send messages
intents = discord.Intents.default()
bot = discord.Client(intents=intents)

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


def get_color(course: str):
    """
    Returns a color to use for the bot message-embed, depending on what course it is
    :param course: String with the current course for today
    :return: Discord-Color object
    """
    if "Pythonprogrammering" in course:
        color = discord.Color.blue()                                    # blue
    elif "Affärsmannaskap" in course:
        color = discord.Color.green()                                   # green
    elif "Databasteknik" in course:
        color = discord.Color.orange()                                  # orange
    elif "Devops" in course:
        color = discord.Color.light_gray()                              # light gray
    elif "Webbramverk i Python" in course:
        color = discord.Color.teal()                                    # teal
    elif "Maskininlärning, teori och praktisk tillämpning" in course:
        color = discord.Color.blurple()                                 # blurple
    elif "Maskininlärning och Deep Learning" in course:
        color = discord.Color.brand_red()                               # brand-red
    else:
        color = discord.Color.purple()                                  # purple

    return color


async def daily_schedule_task():
    """
    Runs the scraping and bot every day at the targeted time.
    Starts by sleeping until that targeted time, then scrapes the schedule website,
    and finally sends a discord message with the information about tomorrow's
    lecture, if there is a lecture for tomorrow.
    :return: None
    """
    # Wait for the bot to be fully ready before entering the while loop
    await bot.wait_until_ready()
    while not bot.is_closed():
        # Create a datetime object for the current time, and the target time
        now = datetime.now()
        target_time = now.replace(hour=20, minute=0, second=0, microsecond=0)

        # if the target time has already passed today, then schedule for tomorrow
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
        tomorrow = str(date.today() + timedelta(days=1))
        school_info = scrape.get_schoolday_info(tomorrow)

        # Get the channel to send the message in
        channel = bot.get_channel(CHANNEL_ID)
        if not channel:
            log.error(f"⚠️ Couldn't find the discord channel")
        elif channel and school_info:
            # Get the color for the message embed
            color = get_color(school_info["course"])

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
                title=f"📅 Schemat för imorgon! ({school_info['weekday']}, {school_info['date']})",
                description=description,
                color=color
            )

            # Send schedule message
            await channel.send(embed=embed)

            # Log the information that was sent
            log.info(
                "✅ Sent message!\n"
                f"   ├─ Date: {school_info['date'] or 'N/A'} ({school_info['weekday'] or 'N/A'})\n"
                f"   ├─ Course: {school_info['course'] or 'N/A'}\n"
                f"   ├─ Teacher: {school_info['teacher'] or 'N/A'}\n"
                f"   ├─ Classroom: {school_info['classroom'] or 'N/A'}\n"
                f"   ├─ Time: {time or 'N/A'}\n"
                f"   └─ Class groups: {school_info['class_group'] or 'N/A'}"
            )
        else:
            log.info("❌ No lecture for tomorrow!")


@bot.event
async def on_ready():
    """
    This function runs when the discord bot is up and running for the first time
    :return: None
    """
    # Create a task for the daily scraping & message sending
    bot.loop.create_task(daily_schedule_task())


if __name__ == "__main__":
    version = "1.1.0"
    log.info(f"🟢 Starting Discord bot! (version: {version})")

    # Run the discord bot and log if there is a crash
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        log.error(f"⚠️ Bot crashed with exception: {e}", exc_info=True)
