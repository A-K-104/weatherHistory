from datetime import datetime
from flask import request, render_template, session
from werkzeug.utils import redirect
import bcrypt as bcrypt
import constance
import weatherDataCollector
from classes.cities import Cities
from classes.user import User

app = constance.app
db = constance.db
sess = constance.sess


@app.before_first_request
def create_tables():
    db.create_all()


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())


def check_hashed_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)


def checkIfInSession():
    if not ('email' in session):
        return False
    return True


@app.route('/', methods=['GET', 'POST'])
def baseRoute():
    return redirect("/home")


@app.route('/home', methods=['GET', 'POST'])
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


@app.route('/addLocation', methods=['GET', 'POST'])
def add_location():
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
    return render_template('addLocation.html', cities=found_cities_options)


@app.route('/CreateAccount', methods=['GET', 'POST'])
def CreateAccount():
    if request.method == "POST":
        email = request.form['email']
        password = get_hashed_password(request.form['password'])
        if User.query.filter_by(email=email).first() is None:
            new_user = User(email=email, password=password)
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect('/login')
            except Exception as e:
                return f"There was an error adding the new user... {e}"
        return render_template("CreateAccount.html", message="email already exist")
    else:
        return render_template("CreateAccount.html", message="")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user = User.query.get(email)
        if user is not None:
            if check_hashed_password(password, user.password):
                session["email"] = user.email
                return redirect("admin")
            return render_template("login.html", status="password issue", email=email, password=password)
        return render_template("login.html", status="user wasn't found", email=email, password=password)
    return render_template("login.html", status="")


@app.route('/admin', methods=['GET', 'POST'])
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


@app.route('/killSession', methods=['GET', 'POST'])
def killSession():
    session.clear()
    return redirect('/login')


if __name__ == "__main__":
    app.run()
