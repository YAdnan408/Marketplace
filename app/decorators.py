from functools import wraps
from flask import session, redirect, url_for
from app.shared.exceptions import UnauthorizedError, ForbiddenError


# ── API decorators (raise domain exceptions) ──────────────────────────────────
# Use these on /api/... backend routes

def login_required(f):
    """Blocks API access if the user is not logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            raise UnauthorizedError()
        return f(*args, **kwargs)
    return decorated


def seller_required(f):
    """Blocks API access if the user is not a logged-in seller."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            raise UnauthorizedError()
        if session.get("user_type") != "seller":
            raise ForbiddenError("Seller access required.")
        return f(*args, **kwargs)
    return decorated


def customer_required(f):
    """Blocks API access if the user is not a logged-in customer."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            raise UnauthorizedError()
        if session.get("user_type") != "customer":
            raise ForbiddenError("Customer access required.")
        return f(*args, **kwargs)
    return decorated


# ── Frontend decorators (redirect to login page) ──────────────────────────────
# Use these on page-rendering frontend routes

def frontend_login_required(f):
    """Redirects to login page if the user is not logged in."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("frontend.login"))
        return f(*args, **kwargs)
    return decorated


def frontend_seller_required(f):
    """Redirects to login page if the user is not a logged-in seller."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("user_type") != "seller":
            return redirect(url_for("frontend.login"))
        return f(*args, **kwargs)
    return decorated


def frontend_customer_required(f):
    """Redirects to login page if the user is not a logged-in customer."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("user_type") != "customer":
            return redirect(url_for("frontend.login"))
        return f(*args, **kwargs)
    return decorated