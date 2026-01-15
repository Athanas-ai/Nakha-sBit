from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200), nullable=True)
    availability = db.Column(db.String(20), nullable=False, default='available')  # available, out_of_stock, made_to_order
    size = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)

class CustomOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_type = db.Column(db.String(50), nullable=False)
    material = db.Column(db.String(50), nullable=True)
    color = db.Column(db.String(50), nullable=True)
    occasion = db.Column(db.String(50), nullable=True)
    size = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    whatsapp_number = db.Column(db.String(20), nullable=False, default='8132981738')
