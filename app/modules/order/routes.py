from flask import Blueprint, request, jsonify, session

from app.decorators import customer_required, seller_required, login_required

from .order_repository import OrderRepository
from .order_service import OrderService

order_bp = Blueprint("order", __name__, url_prefix="/api/orders")

# ── Dependency wiring (DIP) ───────────────────────────────────────────────────
# Concrete repo injected into service here at the composition root.
# To swap implementations (e.g. for testing), only this section changes.

_order_service = OrderService(OrderRepository())


# ── Customer: Place order ─────────────────────────────────────────────────────

@order_bp.route("/checkout", methods=["POST"])
@customer_required
def place_order():
    data = request.json

    result = _order_service.place_order(
        customer_id=session["user_id"],
        cart_items=data.get("cart_items", []),
        shipping_address=data.get("shipping_address", ""),
        shipping_cost=data.get("shipping_cost", 0),
    )

    return jsonify({
        "message": "Order placed successfully!",
        "order":   result,
    }), 201


# ── Customer / Seller: Get order history (role-aware) ─────────────────────────

@order_bp.route("/", methods=["GET"])
@login_required
def get_orders():
    user_type = session.get("user_type")
    if user_type == "customer":
        return jsonify(_order_service.get_customer_orders(session["user_id"])), 200
    if user_type == "seller":
        return jsonify(_order_service.get_seller_orders(session["user_id"])), 200
    return jsonify({"error": "Invalid user type"}), 400


# ── Seller: Approve an order ──────────────────────────────────────────────────

@order_bp.route("/approve/<int:order_id>", methods=["PATCH"])
@seller_required
def approve_order(order_id):
    result = _order_service.approve_order(session["user_id"], order_id)
    return jsonify({
        "message": f"Order #{order_id} has been approved.",
        "order":   result,
    }), 200