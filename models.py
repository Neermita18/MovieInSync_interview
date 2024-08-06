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
    username = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dimensions = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(db.String(100), nullable=False)
    image = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)