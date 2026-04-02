from ..extensions import db
from datetime import datetime


class Seller(db.Model):

    __tablename__ = "sellers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    business_address = db.Column(db.Text, nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(20), nullable=False, default="seller")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    products = db.relationship("Product", backref="seller", lazy=True)
