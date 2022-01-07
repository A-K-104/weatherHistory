from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

apiKey = "{API KEY}"
# TODO: add your api key from: https://openweathermap.org
app = Flask(__name__)
app.config['SECRET_KEY'] = 'randKey'
app.config["SESSION_PERMANENT"] = False
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
app.config['SQLALCHEMY_BINDS'] = {'data': 'sqlite:///user.db'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
sess = Session(app)
db = SQLAlchemy(app)