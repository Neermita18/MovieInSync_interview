from flask_sqlalchemy import SQLAlchemy
import datetime
from datetime import UTC
db= SQLAlchemy()
import bcrypt



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    

class FloorPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    dimensions = db.Column(db.String(80), nullable=False)
    coordinates = db.Column(db.String(80), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.UTC)
    image = db.Column(db.Text, nullable=True)

class MeetingRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    booked_by = db.Column(db.String(80), nullable=True)



