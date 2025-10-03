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
        info = day.find_all("td")

        date = info[2].text.strip()
        time = info[3].text.strip()
        weekday = info[1].text.strip()
        teacher = info[5].text.strip()
        course = info[7].text.strip()
        classroom = info[6].text.strip()

        if date == today_date:
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
