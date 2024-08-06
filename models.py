from flask_sqlalchemy import SQLAlchemy
import datetime
db= SQLAlchemy()
import bcrypt

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class FloorPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dimensions = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False)
    image = db.Column(db.Text, nullable=False)