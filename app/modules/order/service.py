from .repository import OrderRepository


class OrderService:

    @staticmethod
    def place_order(customer_id, cart_items, shipping_address, shipping_cost=0):
        """
        Creates an order and all its order_items from the cart.
        Validates stock, decrements quantities atomically.
        Returns (order_dict, error_message).
        """

        # ── Validate cart ─────────────────────────────────────────
        if not cart_items:
            return None, "Your cart is empty."

        if not shipping_address or not shipping_address.strip():
            return None, "Shipping address is required."

        # ── Validate stock and lock products ──────────────────────
        validated_items = []

        for item in cart_items:
            product_id = item.get("id")
            qty = item.get("qty", 0)

            if not product_id or qty <= 0:
                return None, f"Invalid cart item: {item.get('name', 'Unknown')}."

            product = OrderRepository.get_product_for_checkout(product_id)

            if product is None:
                return None, f"Product '{item.get('name')}' no longer exists."

            if product.stock_quantity < qty:
                return None, (
                    f"Not enough stock for '{product.name}'. "
                    f"Available: {product.stock_quantity}, requested: {qty}."
                )

            validated_items.append({
                "product":    product,
                "qty":        qty,
                "price":      float(product.price),   # always use DB price
                "seller_id":  product.seller_id
            })

        # ── Compute total from DB prices + shipping ───────────────
        subtotal    = sum(i["price"] * i["qty"] for i in validated_items)
        total_price = subtotal + float(shipping_cost)

        try:
            # ── Create order ──────────────────────────────────────
            order = OrderRepository.create_order(
                customer_id=customer_id,
                total_price=total_price,
                shipping_address=shipping_address.strip()
            )

            # ── Create order items + decrement stock ──────────────
            for item in validated_items:
                OrderRepository.create_order_item(
                    order_id=order.id,
                    product_id=item["product"].id,
                    seller_id=item["seller_id"],
                    quantity=item["qty"],
                    price=item["price"]
                )
                OrderRepository.decrement_stock(item["product"], item["qty"])

            OrderRepository.commit()

        except Exception as e:
            OrderRepository.rollback()
            return None, f"Order could not be placed. Please try again. ({str(e)})"

        return {
            "order_id":    order.id,
            "total_price": float(total_price),
            "status":      order.status,
            "item_count":  len(validated_items)
        }, None

    @staticmethod
    def get_customer_orders(customer_id):
        orders = OrderRepository.get_orders_by_customer(customer_id)
        result = []
        for order in orders:
            items = []
            for oi in order.order_items:
                product = oi.product
                items.append({
                    "product_id":   oi.product_id,
                    "product_name": product.name if product else "Deleted product",
                    "image_name":   product.image_name if product else "",
                    "quantity":     oi.quantity,
                    "unit_price":   float(oi.price),       # read from correct column
                    "subtotal":     float(oi.price) * oi.quantity
                })
            result.append({
                "id":               order.id,
                "status":           order.status,
                "total_price":      float(order.total_price),
                "shipping_address": order.shipping_address or "",
                "created_at":       order.created_at.strftime("%d %b %Y, %I:%M %p"),
                "item_count":       len(items),
                "items":            items
            })
        return result