from flask import Blueprint, request, jsonify, session
from .service import OrderService
from app.decorators import customer_required

order_bp = Blueprint("order", __name__, url_prefix="/api")


# ── Checkout: Place order ─────────────────────────────────────────────────────

@order_bp.route("/checkout", methods=["POST"])
@customer_required
def place_order():
    data = request.json

    cart_items       = data.get("cart_items", [])
    shipping_address = data.get("shipping_address", "")
    shipping_cost    = data.get("shipping_cost", 0)     # received from frontend

    result, error = OrderService.place_order(
        customer_id=session["user_id"],
        cart_items=cart_items,
        shipping_address=shipping_address,
        shipping_cost=shipping_cost
    )

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "Order placed successfully!",
        "order": result
    }), 201


# ── Order history: Get all orders for logged-in customer ──────────────────────

@order_bp.route("/orders", methods=["GET"])
@customer_required
def get_orders():
    orders = OrderService.get_customer_orders(session["user_id"])
    return jsonify(orders), 200