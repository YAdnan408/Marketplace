from .interfaces import IOrderService, IOrderRepository
from .exceptions import (
    OrderValidationError,
    InsufficientStockError,
    OrderPlacementError,
)


class OrderService(IOrderService):

    def __init__(self, repo: IOrderRepository) -> None:
        self._repo = repo

    # ── Serializers ───────────────────────────────────────────────────────────

    @staticmethod
    def _serialize_order(order, items: list) -> dict:
        return {
            "id":               order.id,
            "status":           order.status,
            "total_price":      float(order.total_price),
            "shipping_address": order.shipping_address or "",
            "created_at":       order.created_at.strftime("%d %b %Y, %I:%M %p"),
            "item_count":       len(items),
            "items":            items,
        }

    @staticmethod
    def _serialize_order_item(oi) -> dict:
        product = oi.product
        return {
            "product_id":   oi.product_id,
            "product_name": product.name if product else "Deleted product",
            "image_name":   product.image_name if product else "",
            "quantity":     oi.quantity,
            "unit_price":   float(oi.price),
            "subtotal":     float(oi.price) * oi.quantity,
        }

    # ── Place order ───────────────────────────────────────────────────────────

    def place_order(
        self,
        customer_id: int,
        cart_items: list,
        shipping_address: str,
        shipping_cost: float = 0,
    ) -> dict:
        # ── Validate inputs ───────────────────────────────────────
        if not cart_items:
            raise OrderValidationError("Your cart is empty.")

        if not shipping_address or not shipping_address.strip():
            raise OrderValidationError("Shipping address is required.")

        # ── Validate stock and lock products ──────────────────────
        validated_items = []

        for item in cart_items:
            product_id = item.get("id")
            qty        = item.get("qty", 0)

            if not product_id or qty <= 0:
                raise OrderValidationError(
                    f"Invalid cart item: {item.get('name', 'Unknown')}."
                )

            product = self._repo.get_product_for_checkout(product_id)

            if product is None:
                raise OrderValidationError(
                    f"Product '{item.get('name')}' no longer exists."
                )

            if product.stock_quantity < qty:
                raise InsufficientStockError(
                    f"Not enough stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}, requested: {qty}."
                )

            validated_items.append({
                "product":   product,
                "qty":       qty,
                "price":     float(product.price),   # always use server-side DB price
                "seller_id": product.seller_id,
            })

        # ── Compute totals (never trust client-submitted prices) ──
        subtotal    = sum(i["price"] * i["qty"] for i in validated_items)
        total_price = subtotal + float(shipping_cost)

        # ── Persist atomically ────────────────────────────────────
        try:
            order = self._repo.create_order(
                customer_id=customer_id,
                total_price=total_price,
                shipping_address=shipping_address.strip(),
            )

            for item in validated_items:
                self._repo.create_order_item(
                    order_id=order.id,
                    product_id=item["product"].id,
                    seller_id=item["seller_id"],
                    quantity=item["qty"],
                    price=item["price"],
                )
                self._repo.decrement_stock(item["product"], item["qty"])

            self._repo.commit()

        except (OrderValidationError, InsufficientStockError):
            self._repo.rollback()
            raise
        except Exception as exc:
            self._repo.rollback()
            raise OrderPlacementError(
                f"Order could not be placed. Please try again. ({exc})"
            )

        return {
            "order_id":    order.id,
            "total_price": float(total_price),
            "status":      order.status,
            "item_count":  len(validated_items),
        }

    # ── Get order history ─────────────────────────────────────────────────────

    def get_customer_orders(self, customer_id: int) -> list:
        orders = self._repo.get_orders_by_customer(customer_id)
        return [
            self._serialize_order(
                order,
                [self._serialize_order_item(oi) for oi in order.order_items],
            )
            for order in orders
        ]