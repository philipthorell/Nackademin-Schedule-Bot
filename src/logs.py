import os
import logging
import sys


log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)  # ensures the folder exists

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