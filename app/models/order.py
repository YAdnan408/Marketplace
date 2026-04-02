from ..extensions import db
from datetime import datetime


class Order(db.Model):

    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="pending")
    shipping_address = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)

    # Relationships
    order_items = db.relationship("OrderItem", backref="order", lazy=True)
