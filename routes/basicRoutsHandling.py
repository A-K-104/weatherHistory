from datetime import datetime
from flask import Blueprint, render_template, request
from werkzeug.utils import redirect
import weatherDataCollector
from classes.cities import Cities

basic_routs_handling = Blueprint('basic_routs_handling', __name__)


@basic_routs_handling.route('/', methods=['GET', 'POST'])
def baseRoute():
    return redirect("/home")


@basic_routs_handling.route('/home', methods=['GET', 'POST'])
def home():
    cities = list(Cities.query.filter_by(enabled=True).all())
    list_of_locations = []
    if request.method == "POST":
        pickedDate = request.form['filterDate']
        for city in cities:
            list_of_locations.append([city.nameOfCity, weatherDataCollector.getHistoryByLatLon(
                city.location, datetime.strptime(pickedDate, '%Y-%m-%d'))])
        return render_template("home.html",
                               weatherList=list_of_locations,
                               nameOfCity=request.form['nameOfCity'],
                               selectedDate=request.form['filterDate'])
    for city in cities:
        list_of_locations.append([city.nameOfCity, weatherDataCollector.fetByLatLon(city.location)])
    return render_template("home.html",
                           weatherList=list_of_locations,
                           nameOfCity="",
                           selectedDate="")
