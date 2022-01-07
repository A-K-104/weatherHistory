from flask import Blueprint, session, render_template, request
from werkzeug.utils import redirect
import constance
from classes.user import check_hashed_password, User, get_hashed_password

db = constance.db
sess = constance.sess
user_handling = Blueprint('user_handling', __name__)


def checkIfInSession():
    if not ('email' in session):
        return False
    return True


@user_handling.route('/CreateAccount', methods=['GET', 'POST'])
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


@user_handling.route('/login', methods=['GET', 'POST'])
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


@user_handling.route('/killSession', methods=['GET', 'POST'])
def killSession():
    session.clear()
    return redirect('/login')
