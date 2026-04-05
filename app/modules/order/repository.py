from ...extensions import db
from ...models.order import Order
from ...models.order_item import OrderItem
from ...models.product import Product


class OrderRepository:

    @staticmethod
    def create_order(customer_id, total_price, shipping_address):
        order = Order(
            customer_id=customer_id,
            total_price=total_price,
            shipping_address=shipping_address,
            status="pending"
        )
        db.session.add(order)
        db.session.flush()   # Gets order.id without committing yet
        return order

    @staticmethod
    def create_order_item(order_id, product_id, seller_id, quantity, price):
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            seller_id=seller_id,     # required by DB schema
            quantity=quantity,
            price=price              # matches DB column name (not unit_price)
        )
        db.session.add(item)
        return item

    @staticmethod
    def get_product_for_checkout(product_id):
        """Fetch product with a row lock to safely decrement stock."""
        return Product.query.with_for_update().get(product_id)

    @staticmethod
    def decrement_stock(product, quantity):
        product.stock_quantity -= quantity
        return product

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()

    @staticmethod
    def get_orders_by_customer(customer_id):
        return (Order.query
                .filter_by(customer_id=customer_id)
                .order_by(Order.created_at.desc())
                .all())

    @staticmethod
    def get_order_by_id_and_customer(order_id, customer_id):
        return Order.query.filter_by(
            id=order_id,
            customer_id=customer_id
        ).first_or_404()