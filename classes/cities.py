from datetime import datetime
import constance

db = constance.db


class Cities(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nameOfCity = db.Column(db.String(200))
    location = db.Column(db.JSON(200))
    enabled = db.Column(db.Boolean, default=True)
    createDateTime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<enabled %r>' % self.enabled
