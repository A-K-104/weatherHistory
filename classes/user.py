import bcrypt

import constance
from datetime import datetime

db = constance.db


class User(db.Model):
    email = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '{' + f'"name": "{self.name}"' + '}'


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())


def check_hashed_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password.encode('utf-8'), hashed_password)
