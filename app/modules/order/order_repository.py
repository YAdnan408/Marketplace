from ...extensions import db
from ...models.order import Order
from ...models.order_item import OrderItem
from ...models.product import Product
from .interfaces import IOrderRepository


class OrderRepository(IOrderRepository):

    # ── Write / checkout ──────────────────────────────────────────────────────

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

    def create_order_items(self, order_id: int, validated_items: list) -> None:
        """Bulk-insert all order items in a single round-trip."""
        db.session.add_all([
            OrderItem(
                order_id=order_id,
                product_id=item["product"].id,
                seller_id=item["seller_id"],
                quantity=item["qty"],
                price=item["price"],
            )
            for item in validated_items
        ])

    def get_products_for_checkout(self, product_ids: list[int]) -> list:
        """Batch row-level lock ordered by id.

        Locking all rows in one round-trip (vs. N individual queries) minimises
        lock-hold time.  The ORDER BY id guarantee means every concurrent
        transaction acquires locks in the same sequence, making deadlocks
        impossible.
        """
        return (
            Product.query
            .filter(Product.id.in_(product_ids))
            .order_by(Product.id)
            .with_for_update()
            .all()
        )

    def decrement_stock(self, product, quantity: int):
        product.stock_quantity -= quantity
        return product

    # ── Customer reads ────────────────────────────────────────────────────────

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

    # ── Seller reads + writes ─────────────────────────────────────────────────

    def get_orders_by_seller(self, seller_id: int):
        """Return all distinct orders containing at least one item from this seller."""
        return (
            Order.query
            .join(Order.order_items)
            .filter(OrderItem.seller_id == seller_id)
            .distinct()
            .order_by(Order.created_at.desc())
            .all()
        )

    def get_order_by_id_and_seller(self, order_id: int, seller_id: int):
        """Prevent sellers from accessing orders that contain none of their items."""
        return (
            Order.query
            .join(Order.order_items)
            .filter(Order.id == order_id, OrderItem.seller_id == seller_id)
            .first_or_404()
        )

    def update_order_status(self, order, new_status: str):
        order.status = new_status
        db.session.commit()
        return order

    # ── Transaction control ───────────────────────────────────────────────────

    def atomic_commit(self) -> None:
        """Commit the transaction; rollback and re-raise on any DB error.

        Keeping commit/rollback inside the repo means the service never
        touches transaction control — it only expresses business intent.
        """
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise