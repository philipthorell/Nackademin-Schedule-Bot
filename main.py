import discord
import requests
from bs4 import BeautifulSoup

from datetime import date


URL = "https://cloud.timeedit.net/nackademin/web/1/ri165vYy57Y405QYfZQ7826XZ10QQ.html"

#response = requests.get(URL)

with open("index.html", "r") as f:
    content = f.read()

#soup = BeautifulSoup(response.content, "html.parser")
soup = BeautifulSoup(content, "html.parser")

table = soup.find("table", class_="restable")

days = table.find_all("tr", class_="rr clickable2")

today = str(date.today())


school_day_info = {}

found_today = False

for day in days:
    date_tag = day.find("td", class_="time timeextra c-1 right t")
    date = date_tag.text.strip()

    am_time_tag = day.find("td", class_="time tt c-1")
    am_time = am_time_tag.text.strip()

    if date == "2025-10-08":
        school_day_info["date"] = date
        school_day_info["am_time"] = am_time
        found_today = True

    elif found_today:
        break

print(school_day_info)
