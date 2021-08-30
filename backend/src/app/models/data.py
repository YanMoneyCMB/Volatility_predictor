from app.models import db

class ML(db.Model):
    ticker = db.Column(db.String(50))
    period = db.Column(db.Integer)
    model = db.Column(db.PickleType)
    updated_DateTime = db.Column(db.DateTime)

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self
