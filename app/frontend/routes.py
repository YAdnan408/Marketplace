from flask import Blueprint, render_template, session, redirect, url_for
from app.decorators import frontend_login_required

frontend_bp = Blueprint(
    "frontend",
    __name__,
    template_folder="../../templates"
)


# ── Root redirect ─────────────────────────────────────────────────────────────
# No decorator — must be public

@frontend_bp.route("/")
def index():
    if "user_id" in session:
        if session["user_type"] == "seller":
            return redirect(url_for("seller_frontend.seller_dashboard"))
        return redirect(url_for("customer_frontend.customer_dashboard"))
    return redirect(url_for("frontend.login"))


# ── Auth pages ────────────────────────────────────────────────────────────────
# No decorator — publicly accessible

@frontend_bp.route("/signup")
def signup():
    if "user_id" in session:
        return redirect(url_for("frontend.index"))
    return render_template("signup.html")


@frontend_bp.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("frontend.index"))
    return render_template("login.html")


# ── Profile page (shared — both customers and sellers use this) ───────────────

@frontend_bp.route("/profile")
@frontend_login_required
def profile():
    return render_template("profile.html")


# ── Products page (shared — serves correct template based on user_type) ───────

@frontend_bp.route("/products")
@frontend_login_required
def products():
    if session["user_type"] == "seller":
        return render_template("seller_products.html", user_name=session["user_name"])
    return render_template("customer_products.html", user_name=session["user_name"])
