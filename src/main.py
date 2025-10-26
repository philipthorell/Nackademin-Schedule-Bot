import signal

from src.discord_bot import *


def handle_shutdown(signal_number: int, frame):
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


log = logging.getLogger("DiscordBot")

signal.signal(signal.SIGTERM, handle_shutdown)
signal.signal(signal.SIGINT, handle_shutdown)


if __name__ == "__main__":
    version = "1.2.0"
    log.info(f"🟢 Starting Discord bot! (version: {version})")

    # Run the discord bot and log if there is a crash
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        log.error(f"⚠️ Bot crashed with exception: {e}", exc_info=True)
