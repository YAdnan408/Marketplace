from ...extensions import db
from ...models.order import Order
from ...models.order_item import OrderItem
from ...models.product import Product
from .interfaces import IOrderRepository


class OrderRepository(IOrderRepository):

    def create_order(self, customer_id: int, total_price: float, shipping_address: str):
        order = Order(
            customer_id=customer_id,
            total_price=total_price,
            shipping_address=shipping_address,
            status="pending",
        )
        db.session.add(order)
        db.session.flush()   # obtain order.id without committing yet
        return order

    def create_order_item(
        self,
        order_id: int,
        product_id: int,
        seller_id: int,
        quantity: int,
        price: float,
    ):
        item = OrderItem(
            order_id=order_id,
            product_id=product_id,
            seller_id=seller_id,
            quantity=quantity,
            price=price,
        )
        db.session.add(item)
        return item

    def get_product_for_checkout(self, product_id: int):
        """Row-level lock ensures safe concurrent stock decrement."""
        return Product.query.with_for_update().get(product_id)

    def decrement_stock(self, product, quantity: int):
        product.stock_quantity -= quantity
        return product

    def get_orders_by_customer(self, customer_id: int):
        return (
            Order.query
            .filter_by(customer_id=customer_id)
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_order_by_id_and_customer(self, order_id: int, customer_id: int):
        return Order.query.filter_by(
            id=order_id,
            customer_id=customer_id,
        ).first_or_404()

    def commit(self) -> None:
        db.session.commit()

    def rollback(self) -> None:
        db.session.rollback()