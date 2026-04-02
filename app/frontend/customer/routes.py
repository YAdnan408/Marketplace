from flask import Blueprint, render_template, session
from app.decorators import frontend_customer_required

customer_frontend_bp = Blueprint(
    "customer_frontend",
    __name__,
    template_folder="../../../templates"
)


# ── Customer dashboard ────────────────────────────────────────────────────────

@customer_frontend_bp.route("/customer/dashboard")
@frontend_customer_required
def customer_dashboard():
    return render_template("customer_dashboard.html", user_name=session["user_name"])


# ── Product detail page ───────────────────────────────────────────────────────

@customer_frontend_bp.route("/product/<int:product_id>")
@frontend_customer_required
def product_detail(product_id):
    return render_template("product_detail.html", user_name=session["user_name"])


# ── Cart page ─────────────────────────────────────────────────────────────────

@customer_frontend_bp.route("/cart")
@frontend_customer_required
def cart():
    return render_template("cart.html", user_name=session["user_name"])