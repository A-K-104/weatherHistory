from datetime import datetime
from flask import Flask, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import redirect
import bcrypt as bcrypt
from flask_session import Session

import weatherDataCollector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'randKey'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {'data': 'sqlite:///user.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
sess = Session(app)
db = SQLAlchemy(app)


class User(db.Model):
    email = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '{' + f'"name": "{self.name}"' + '}'


class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nameOfCity = db.Column(db.String(200))
    location = db.Column(db.JSON(200))
    enabled = db.Column(db.Boolean, default=True)
    createDateTime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<enabled %r>' % self.enabled


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


# todo: filter double locations and already enabled locations.
@app.route('/addLocation', methods=['GET', 'POST'])
def add_location():
    if not checkIfInSession():
        return redirect("login")
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
            return render_template('addLocation.html', cities=found_cities_options)

    return render_template('addLocation.html', cities=[])


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
        if not (user is None):
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
