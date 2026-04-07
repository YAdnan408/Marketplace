from ..extensions import db


class OrderItem(db.Model):

    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)   # matches DB column name

    # Foreign keys
    order_id   = db.Column(db.Integer, db.ForeignKey("orders.id"),    nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"),  nullable=False)
    seller_id  = db.Column(db.Integer, db.ForeignKey("sellers.id"),   nullable=False)

    # Relationships
    product = db.relationship("Product", lazy="joined")
    seller  = db.relationship("Seller",  lazy="joined")
