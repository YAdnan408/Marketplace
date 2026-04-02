import os
from flask import Blueprint, request, jsonify, session, current_app
from .service import CustomerService, SellerService
from app.decorators import login_required

user_bp = Blueprint("user", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Signup ────────────────────────────────────────────────────────────────────
# No decorator — public route

@user_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json
    user_type = data.get("user_type")

    if user_type == "customer":
        result, error = CustomerService.signup(data)
    elif user_type == "seller":
        result, error = SellerService.signup(data)
    else:
        return jsonify({"error": "Invalid account type. Choose customer or seller."}), 400

    if error:
        return jsonify({"error": error}), 400

    session["user_id"] = result["id"]
    session["user_name"] = result["name"]
    session["user_type"] = result["user_type"]

    return jsonify({"message": "Account created successfully", "user": result}), 201


# ── Login ─────────────────────────────────────────────────────────────────────
# No decorator — public route

@user_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user_type = data.get("user_type")

    if user_type == "customer":
        result, error = CustomerService.login(data)
    elif user_type == "seller":
        result, error = SellerService.login(data)
    else:
        return jsonify({"error": "Invalid account type. Choose customer or seller."}), 400

    if error:
        return jsonify({"error": error}), 401

    session["user_id"] = result["id"]
    session["user_name"] = result["name"]
    session["user_type"] = result["user_type"]

    return jsonify({"message": "Login successful", "user": result}), 200


# ── Logout ────────────────────────────────────────────────────────────────────
# No decorator — safe to call even when not logged in

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
        "user_type": session["user_type"]
    }), 200


# ── Profile: Get ──────────────────────────────────────────────────────────────

@user_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    user_id = session["user_id"]
    user_type = session["user_type"]

    if user_type == "customer":
        profile = CustomerService.get_profile(user_id)
    else:
        profile = SellerService.get_profile(user_id)

    return jsonify(profile), 200


# ── Profile: Update info ──────────────────────────────────────────────────────

@user_bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    user_id = session["user_id"]
    user_type = session["user_type"]
    data = request.json

    if not data.get("name", "").strip():
        return jsonify({"error": "Name cannot be empty."}), 400

    if user_type == "customer":
        updated = CustomerService.update_profile(user_id, data)
    else:
        updated = SellerService.update_profile(user_id, data)

    session["user_name"] = updated["name"]

    return jsonify({"message": "Profile updated successfully", "profile": updated}), 200


# ── Profile: Upload image ─────────────────────────────────────────────────────

@user_bp.route("/profile/image", methods=["POST"])
@login_required
def upload_profile_image():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp."}), 400

    user_id = session["user_id"]
    user_type = session["user_type"]

    upload_folder = os.path.join(current_app.static_folder, "uploads", "profile_images")
    os.makedirs(upload_folder, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[1].lower()
    image_name = f"{user_type}_{user_id}_avatar.{ext}"
    file.save(os.path.join(upload_folder, image_name))

    if user_type == "customer":
        CustomerService.update_profile_image(user_id, image_name)
    else:
        SellerService.update_profile_image(user_id, image_name)

    return jsonify({
        "message": "Profile image updated successfully",
        "profile_image": image_name
    }), 200
