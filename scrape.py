import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

import os


load_dotenv()


URL = os.getenv("SCHEDULE_URL")


def get_soup(url=URL):
    # Gets the code of the schedule website and makes it into a soup object to be used for scraping
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")

    return soup


def get_schoolday_info(target_date: str):
    """
    Gets the information about today's lecture, if there is a lecture today
    :param target_date: String containing the target-date (the date to find the information about), e.g. 2025-10-04
    :return: Dictionary with the information about today's class, or empty dict if there's no lecture for today
    """
    soup = get_soup()
    table = soup.find("table", class_="restable")
    if not table:
        print("DIDN'T FIND <TABLE> TAG!")
        return {}

    days = table.find_all("tr", class_="rr clickable2")

    school_day_info = {}
    found_today = False

    for day in days:

        # Get all the information about the tag
        info = day.find_all("td")
        weekday = info[1].text.strip()
        date = info[2].text.strip()
        time = info[3].text.strip()
        class_group = info[4].text.strip()
        teacher = info[5].text.strip()
        classroom = info[6].text.strip()
        course = info[7].text.strip()

        # If the current tag is about today, then store all the information
        if date == target_date:
            school_day_info["date"] = date
            school_day_info["weekday"] = weekday
            school_day_info["teacher"] = teacher
            school_day_info["course"] = course
            school_day_info["classroom"] = classroom
            school_day_info["time_1"] = time
            school_day_info["class_group"] = class_group
            found_today = True

        # If the first tag is found and the second one is a new day/lecture, then don't add that time
        elif found_today and weekday:
            school_day_info["time_2"] = ""
            break

        # If the first tag is found, get the second tags time, for the afternoon time
        elif found_today:
            school_day_info["time_2"] = time
            break

    return school_day_info
