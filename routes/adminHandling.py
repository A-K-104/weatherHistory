from flask import Blueprint, render_template, request
from werkzeug.utils import redirect

import constance
import weatherDataCollector
from classes.cities import Cities
from routes.userHandling import checkIfInSession

db = constance.db
sess = constance.sess
admin_handling = Blueprint('admin_handling', __name__)


@admin_handling.route('/addLocation', methods=['GET', 'POST'])
def add_location():
    latLonR = ["", "", ""]
    nameOfCity = ''
    if not checkIfInSession():
        return redirect("login")
    found_cities_options = []
    if request.method == 'POST':
        if 'by' in request.args:
            for city in request.form:
                city_name = city[5:]
                if city.__contains__('name_'):
                    if Cities.query.filter_by(nameOfCity=city_name).first() is None:
                        new_city = Cities(nameOfCity=city_name, location=[float(request.form[f'coord_lat_{city_name}']),
                                                                          float(request.form[f'coord_lon_{city_name}'])]
                                          )
                        db.session.add(new_city)
                db.session.commit()
            return redirect("admin")
        else:
            if request.form['nameOfCity'] != "":
                found_cities_options = [weatherDataCollector.getByCity(request.form['nameOfCity'])]
            else:
                found_cities_options = weatherDataCollector.getCityInRadios([request.form['lat'],
                                                                             request.form['lon']],
                                                                            request.form['radios'])
                found_cities_options = {each['name']: each for each in found_cities_options}.values()
            latLonR = [request.form['lat'], request.form['lon'], request.form['radios']]
            nameOfCity = request.form['nameOfCity']
            print(found_cities_options)
    return render_template('addLocation.html', cities=found_cities_options, latLonR=latLonR, nameOfCity=nameOfCity)


@admin_handling.route('/admin', methods=['GET', 'POST'])
def admin():
    if not checkIfInSession():
        return redirect("login")
    cities = list(Cities.query.order_by(Cities.nameOfCity))
    if request.method == "POST":
        for city in cities:
            if f"radio_{city.nameOfCity}" in request.form:
                if 'delete' in request.form:
                    db.session.delete(city)
                else:
                    city.enabled = not city.enabled
        db.session.commit()
        return redirect('/admin')
    return render_template("admin.html", cities=cities)
