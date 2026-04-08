from flask import Blueprint, request, jsonify, session

from app.decorators import customer_required

from .order_repository import OrderRepository
from .order_service import OrderService

order_bp = Blueprint("order", __name__, url_prefix="/api/orders")

# ── Dependency wiring (DIP) ───────────────────────────────────────────────────
# Concrete repo injected into service here at the composition root.
# To swap implementations (e.g. for testing), only this section changes.

_order_service = OrderService(OrderRepository())


# ── Checkout: Place order ─────────────────────────────────────────────────────

@order_bp.route("/checkout", methods=["POST"])
@customer_required
def place_order():
    data = request.json

    cart_items       = data.get("cart_items", [])
    shipping_address = data.get("shipping_address", "")
    shipping_cost    = data.get("shipping_cost", 0)

    result = _order_service.place_order(
        customer_id=session["user_id"],
        cart_items=cart_items,
        shipping_address=shipping_address,
        shipping_cost=shipping_cost,
    )

    return jsonify({
        "message": "Order placed successfully!",
        "order":   result,
    }), 201


# ── Order history: Get all orders for logged-in customer ──────────────────────

@order_bp.route("/", methods=["GET"])
@customer_required
def get_orders():
    orders = _order_service.get_customer_orders(session["user_id"])
    return jsonify(orders), 200