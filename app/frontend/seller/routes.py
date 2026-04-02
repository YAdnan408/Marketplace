from flask import Blueprint, render_template, session
from app.decorators import frontend_seller_required

seller_frontend_bp = Blueprint(
    "seller_frontend",
    __name__,
    template_folder="../../../templates"
)


# ── Seller dashboard ──────────────────────────────────────────────────────────

@seller_frontend_bp.route("/seller/dashboard")
@frontend_seller_required
def seller_dashboard():
    return render_template("seller_dashboard.html", user_name=session["user_name"])