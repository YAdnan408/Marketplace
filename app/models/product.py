from ..extensions import db
from datetime import datetime


class Product(db.Model):

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    image_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    seller_id = db.Column(db.Integer, db.ForeignKey("sellers.id"), nullable=False)
