import discord
import asyncio

import os
import datetime
import logging

import scrape


class DiscordClient(discord.Client):
    # Gets the discord token and the discord channel id from .env file
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

    # Get the basic intents to only send messages
    INTENTS = discord.Intents.default()

    def __init__(self):
        # Give the bot the chosen intents
        super().__init__(intents=self.INTENTS)

        # Get the logger object
        self.log = logging.getLogger("DiscordBot")

        # Get the channel to send the message in
        self.channel = self.get_channel(self.CHANNEL_ID)
        if not self.channel:
            self.log.error(f"⚠️ Couldn't find the discord channel")
            self.close()
        else:
            self.run(self.DISCORD_TOKEN)

    async def on_ready(self) -> None:
        """
        This method runs when the discord bot is up and running for the first time
        """
        # Create a task for the daily scraping & message sending
        self.loop.create_task(self.daily_schedule_task())

    @staticmethod
    def get_embed_color(course: str) -> discord.Color:
        """
        Returns a color to use for the bot message-embed, depending on what course it is
        :param course: String with the current course for today
        :return: Discord-Color object
        """
        if "Pythonprogrammering" in course:
            color = discord.Color.blue()  # blue
        elif "Affärsmannaskap" in course:
            color = discord.Color.green()  # green
        elif "Databasteknik" in course:
            color = discord.Color.orange()  # orange
        elif "Devops" in course:
            color = discord.Color.light_gray()  # light gray
        elif "Webbramverk i Python" in course:
            color = discord.Color.teal()  # teal
        elif "Maskininlärning, teori och praktisk tillämpning" in course:
            color = discord.Color.blurple()  # blurple
        elif "Maskininlärning och Deep Learning" in course:
            color = discord.Color.brand_red()  # brand-red
        else:
            color = discord.Color.purple()  # purple

        return color

    async def daily_schedule_task(self) -> None:
        """
        Runs the scraping and bot every day at the targeted time.
        Starts by sleeping until that targeted time, then scrapes the schedule website,
        and finally sends a discord message with the information about tomorrow's
        lecture, if there is a lecture for tomorrow.
        """
        # Wait for the bot to be fully ready before entering the while loop
        await self.wait_until_ready()
        while not self.is_closed():
            # Create a datetime object for the current time, and the target time
            now = datetime.datetime.now()
            target_time = now.replace(hour=20, minute=0, second=0, microsecond=0)

            # if the target time has already passed today, then schedule for tomorrow
            if now >= target_time:
                target_time += datetime.timedelta(days=1)

            # Get the time to wait in seconds and sleep for that long
            wait_seconds = (target_time - now).total_seconds()
            await asyncio.sleep(wait_seconds)

            # Get the date for today and the scraped information
            tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))
            school_info = scrape.get_schoolday_info(tomorrow)

            if school_info:
                # Get the color for the message embed
                color = self.get_embed_color(school_info["course"])

                # Add the second tags time if there was an associated second tag
                time = f"{school_info['time_1']} - lunch - {school_info['time_2']}" if school_info["time_2"] else \
                school_info["time_1"]

                # Create the description for the message embed
                description = "\u200b\n"  # "\u200b" is an invisible character
                description += f"**• 📚 Course:** {school_info['course']}\n\n"
                description += f"**• 👨‍🏫 Teacher:** {school_info['teacher']}\n\n" if school_info["teacher"] else ""
                description += f"**• 🏫 Room:** {school_info['classroom']}\n\n" if school_info["classroom"] else ""
                description += f"**• ⏰ Time:** {time}\n\n"
                description += f"**• 👥 Classes:** {school_info['class_group']}" if school_info["class_group"].lower() != "pia25" else ""

                # Create the embed for the discord message
                embed = discord.Embed(
                    title=f"📅 Tomorrow's Schedule! ({school_info['weekday']}, {school_info['date']})",
                    description=description,
                    color=color
                )

                # Send schedule message
                await self.channel.send(embed=embed)

                space = " " * 29

                # Log the information that was sent
                self.log.info(
                    "✅ Sent message!\n"
                    f"{space}├─ Date: {school_info['date'] or 'N/A'} ({school_info['weekday'] or 'N/A'})\n"
                    f"{space}├─ Course: {school_info['course'] or 'N/A'}\n"
                    f"{space}├─ Teacher: {school_info['teacher'] or 'N/A'}\n"
                    f"{space}├─ Classroom: {school_info['classroom'] or 'N/A'}\n"
                    f"{space}├─ Time: {time or 'N/A'}\n"
                    f"{space}└─ Class groups: {school_info['class_group'] or 'N/A'}"
                )
            else:
                self.log.info("❌ No lecture for tomorrow!")
