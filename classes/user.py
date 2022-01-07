import constance
from datetime import datetime

db = constance.db


class User(db.Model):
    email = db.Column(db.String(200), primary_key=True)
    password = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '{' + f'"name": "{self.name}"' + '}'
