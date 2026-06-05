from .interfaces import IOrderService, IOrderRepository
from .exceptions import (
    OrderValidationError,
    InsufficientStockError,
    OrderStatusError,
)

# Valid status transitions a seller may trigger
_SELLER_ALLOWED_TRANSITIONS = {
    "pending": "approved",
}


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

    @staticmethod
    def _serialize_seller_order(order, seller_id: int) -> dict:
        """Serialise an order from the seller's perspective.

        Includes all items but flags which belong to this seller.
        Includes the customer's name and a seller-specific subtotal.
        """
        all_items = []
        seller_subtotal = 0.0

        for oi in order.order_items:
            product = oi.product
            item_dict = {
                "product_id":   oi.product_id,
                "product_name": product.name if product else "Deleted product",
                "image_name":   product.image_name if product else "",
                "quantity":     oi.quantity,
                "unit_price":   float(oi.price),
                "subtotal":     float(oi.price) * oi.quantity,
                "is_mine":      oi.seller_id == seller_id,
            }
            all_items.append(item_dict)
            if oi.seller_id == seller_id:
                seller_subtotal += item_dict["subtotal"]

        customer = order.customer
        return {
            "id":               order.id,
            "status":           order.status,
            "total_price":      float(order.total_price),
            "seller_subtotal":  round(seller_subtotal, 2),
            "shipping_address": order.shipping_address or "",
            "created_at":       order.created_at.strftime("%d %b %Y, %I:%M %p"),
            "item_count":       len(all_items),
            "items":            all_items,
            "customer_name":    customer.name if customer else "Unknown",
            "customer_email":   customer.email if customer else "",
        }

    # ── Customer: Place order ─────────────────────────────────────────────────

    def place_order(
        self,
        customer_id: int,
        cart_items: list,
        shipping_address: str,
        shipping_cost: float = 0,
    ) -> dict:
        # ── 1. Validate inputs (no DB) ────────────────────────────
        if not cart_items:
            raise OrderValidationError("Your cart is empty.")

        if not shipping_address or not shipping_address.strip():
            raise OrderValidationError("Shipping address is required.")

        # ── 2. Validate cart item shapes and build id→qty map ─────
        # Done before any DB call so we fail fast on bad input.
        requested: dict[int, dict] = {}
        for item in cart_items:
            product_id = item.get("id")
            qty        = item.get("qty", 0)

            if not product_id or qty <= 0:
                raise OrderValidationError(
                    f"Invalid cart item: {item.get('name', 'Unknown')}."
                )

            requested[int(product_id)] = {"qty": qty, "name": item.get("name")}

        # ── 3. Single batch query: lock all rows at once ──────────
        # Rows are locked in ascending id order, which guarantees every
        # concurrent transaction acquires locks in the same sequence and
        # therefore makes deadlocks impossible.
        products = self._repo.get_products_for_checkout(list(requested.keys()))
        products_by_id = {p.id: p for p in products}

        # ── 4. Validate stock in pure Python (no further DB calls) ─
        validated_items = []
        for product_id, meta in requested.items():
            product = products_by_id.get(product_id)
            qty     = meta["qty"]

            if product is None:
                raise OrderValidationError(
                    f"Product '{meta['name']}' no longer exists."
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

        # ── 5. Compute totals (never trust client-submitted prices) ─
        subtotal    = sum(i["price"] * i["qty"] for i in validated_items)
        total_price = subtotal + float(shipping_cost)

        # ── 6. Persist atomically ─────────────────────────────────
        order = self._repo.create_order(
            customer_id=customer_id,
            total_price=total_price,
            shipping_address=shipping_address.strip(),
        )

        # single INSERT ... VALUES (...), (...), ... for all items
        self._repo.create_order_items(order.id, validated_items)

        # in-memory only — no DB calls, flushed together on commit
        for item in validated_items:
            self._repo.decrement_stock(item["product"], item["qty"])

        # repo commits and rolls back on failure — re-raises for global handler
        self._repo.atomic_commit()

        return {
            "order_id":    order.id,
            "total_price": float(total_price),
            "status":      order.status,
            "item_count":  len(validated_items),
        }

    # ── Customer: Get order history ───────────────────────────────────────────

    def get_customer_orders(self, customer_id: int) -> list:
        orders = self._repo.get_orders_by_customer(customer_id)
        return [
            self._serialize_order(
                order,
                [self._serialize_order_item(oi) for oi in order.order_items],
            )
            for order in orders
        ]

    # ── Seller: Get received orders ───────────────────────────────────────────

    def get_seller_orders(self, seller_id: int) -> list:
        orders = self._repo.get_orders_by_seller(seller_id)
        return [
            self._serialize_seller_order(order, seller_id)
            for order in orders
        ]

    # ── Seller: Approve an order ──────────────────────────────────────────────

    def approve_order(self, seller_id: int, order_id: int) -> dict:
        order = self._repo.get_order_by_id_and_seller(order_id, seller_id)

        new_status = _SELLER_ALLOWED_TRANSITIONS.get(order.status)
        if new_status is None:
            raise OrderStatusError(
                f"Cannot approve an order with status '{order.status}'. "
                f"Only pending orders can be approved."
            )

        updated = self._repo.update_order_status(order, new_status)
        return {"order_id": updated.id, "status": updated.status}