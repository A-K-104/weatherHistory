from datetime import datetime
import requests as requests

import constance


def fetByLatLon(latlon):
    contents = requests.get(
      f'https://api.openweathermap.org/data/2.5/onecall?'
      f'lat={latlon[0]}&lon={latlon[1]}&units=metric&exclude=hourly,daily&appid={constance.apiKey}')
    return contents.json()


def getHistoryByLatLon(latlon, time):
    contents = requests.get(
        f"https://api.openweathermap.org/data/2.5/onecall/timemachine?"
        f"lat={latlon[0]}&lon={latlon[1]}&dt={getUnix(time)}&units=metric&appid={constance.apiKey}")

    return contents.json()


def getCityInRadios(latlon):
    contents = requests.get(
        f'https://api.openweathermap.org/data/2.5/find?'
        f'lat={latlon[0]}&lon={latlon[1]}&cnt=50&units=metric&appid={constance.apiKey}')
    return contents.json()


def getByCity(city):
    contents = requests.get(
        f'http://api.openweathermap.org/data/2.5/weather?'
        f'q={city},uk&APPID=f7a95220f7b9e21e7e97065dfc77f7ea')
    return contents.json()


def getUnix(dt: datetime):
    timestamp = int(dt.timestamp())
    return timestamp



