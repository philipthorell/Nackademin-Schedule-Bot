import requests
from bs4 import BeautifulSoup


URL = "https://cloud.timeedit.net/nackademin/web/1/ri165vYy57Y405QYfZQ7826XZ10QQ.html"


def get_soup(url=URL):
    #response = requests.get(url)

    with open("index.html", "r") as f:
        content = f.read()

    #soup = BeautifulSoup(response.content, "html.parser")
    soup = BeautifulSoup(content, "html.parser")

    return soup


def get_schoolday_info(today_date):
    soup = get_soup()

    table = soup.find("table", class_="restable")

    days = table.find_all("tr", class_="rr clickable2")

    school_day_info = {}
    found_today = False

    for day in days:
        date_tag = day.find("td", class_="time timeextra c-1 right t")
        date = date_tag.text.strip()

        time_tag = day.find("td", class_="time tt c-1")
        time = time_tag.text.strip()

        weekday_tag = day.find("td", class_="time timeextra c-1 left t")
        weekday = weekday_tag.text.strip()

        teacher_tag = day.find("td", class_="column1 columnLine nw c-1")
        teacher = teacher_tag.text.strip()

        course_tag = day.find("td", class_="column1 columnLine c-1")
        if course_tag is None:
            course_tag = day.find_all("td", class_="column1 columnLine nw c-1")[1]
        course = course_tag.text.strip()

        try:
            classroom_tag = day.find_all("td", class_="column0 columnLine nw c-1")[1]
        except IndexError:
            classroom_tag = day.find("td", class_="column0 columnLine c-1")
        classroom = classroom_tag.text.strip()

        if date == "2025-12-09":
            school_day_info["date"] = date
            school_day_info["weekday"] = weekday
            school_day_info["teacher"] = teacher
            school_day_info["course"] = course
            school_day_info["classroom"] = classroom
            school_day_info["time_1"] = time
            found_today = True

        elif found_today and weekday:
            school_day_info["time_2"] = ""
            break

        elif found_today:
            school_day_info["time_2"] = time
            break

    return school_day_info
