import os
from flask import Blueprint, request, jsonify, session, current_app

from app.decorators import login_required
from app.shared import allowed_file,get_extension,save_upload

from .customer_repository import CustomerRepository
from .seller_repository import SellerRepository
from .customer_service import CustomerService
from .seller_service import SellerService
from .exceptions import (
    UserValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)

user_bp = Blueprint("user", __name__, url_prefix="/api")

# ── Dependency wiring (DIP) ───────────────────────────────────────────────────
# Concrete repos injected into services here at the composition root.
# To swap implementations (e.g. for testing), only this section changes.

_customer_service = CustomerService(CustomerRepository())
_seller_service = SellerService(SellerRepository())


def _get_service(user_type: str):
    if user_type == "customer":
        return _customer_service
    if user_type == "seller":
        return _seller_service
    return None


# ── Signup ────────────────────────────────────────────────────────────────────

@user_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    service = _get_service(data.get("user_type"))
    if service is None:
        return jsonify({"error": "Invalid account type. Choose customer or seller."}), 400

    try:
        result = service.signup(data)
    except (UserValidationError, UserAlreadyExistsError) as exc:
        return jsonify({"error": str(exc)}), 400

    session["user_id"] = result["id"]
    session["user_name"] = result["name"]
    session["user_type"] = result["user_type"]
    return jsonify({"message": "Account created successfully", "user": result}), 201


# ── Login ─────────────────────────────────────────────────────────────────────

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    service = _get_service(data.get("user_type"))
    if service is None:
        return jsonify({"error": "Invalid account type. Choose customer or seller."}), 400

    try:
        result = service.login(data)
    except UserValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    except (UserNotFoundError, InvalidCredentialsError) as exc:
        return jsonify({"error": str(exc)}), 401

    session["user_id"] = result["id"]
    session["user_name"] = result["name"]
    session["user_type"] = result["user_type"]
    return jsonify({"message": "Login successful", "user": result}), 200


# ── Logout ────────────────────────────────────────────────────────────────────

@user_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# ── Session check ─────────────────────────────────────────────────────────────

@user_bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "id": session["user_id"],
        "name": session["user_name"],
        "user_type": session["user_type"],
    }), 200


# ── Profile: Get ──────────────────────────────────────────────────────────────

@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    service = _get_service(session["user_type"])
    profile = service.get_profile(session["user_id"])
    return jsonify(profile), 200


# ── Profile: Update ───────────────────────────────────────────────────────────

@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    data = request.json
    if not data.get("name", "").strip():
        return jsonify({"error": "Name cannot be empty."}), 400

    service = _get_service(session["user_type"])
    updated = service.update_profile(session["user_id"], data)
    session["user_name"] = updated["name"]
    return jsonify({"message": "Profile updated successfully", "profile": updated}), 200


# ── Profile: Upload image ─────────────────────────────────────────────────────

@user_bp.route("/profile/image", methods=["POST"])
@login_required
def upload_profile_image():
    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify({"error": "No image file provided."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp."}), 400

    user_id = session["user_id"]
    user_type = session["user_type"]
    ext = get_extension(file.filename)
    image_name = f"{user_type}_{user_id}_avatar.{ext}"

    upload_folder = os.path.join(current_app.static_folder, "uploads", "profile_images")
    save_upload(file, upload_folder, image_name)

    service = _get_service(user_type)
    service.update_profile_image(user_id, image_name)
    return jsonify({
        "message": "Profile image updated successfully",
        "profile_image": image_name,
    }), 200
