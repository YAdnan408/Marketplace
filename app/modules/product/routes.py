import os
from flask import Blueprint, request, jsonify, session, current_app
from .service import ProductService
from app.decorators import login_required, seller_required, customer_required

product_bp = Blueprint("product", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ── Customer: Get categories ──────────────────────────────────────────────────

@product_bp.route("/customer/categories", methods=["GET"])
@login_required
def get_categories_customer():
    categories = ProductService.get_categories()
    return jsonify(categories), 200


# ── Customer/Seller: Browse products (role-aware) ─────────────────────────────

@product_bp.route("/products", methods=["GET"])
@login_required
def get_products():
    user_id = session["user_id"]
    user_type = session.get("user_type")

    if user_type == "customer":
        products = ProductService.get_all_products()
    elif user_type == "seller":
        products = ProductService.get_seller_products(user_id)
    else:
        return jsonify({"error": "Invalid user type"}), 400

    return jsonify(products), 200


# ── Customer: Get single product detail ──────────────────────────────────────

@product_bp.route("/product/<int:product_id>", methods=["GET"])
@customer_required
def get_product_detail(product_id):
    product = ProductService.get_product_detail(product_id)
    if product is None:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product), 200


# ── Seller: Add product ───────────────────────────────────────────────────────

@product_bp.route("/product", methods=["POST"])
@seller_required
def add_product():
    data = request.json
    result, error = ProductService.add_product(session["user_id"], data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Product added successfully.", "product": result}), 201


# ── Seller: Update product ────────────────────────────────────────────────────

@product_bp.route("/product/<int:product_id>", methods=["PUT"])
@seller_required
def update_product(product_id):
    data = request.json
    result, error = ProductService.update_product(session["user_id"], product_id, data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Product updated successfully.", "product": result}), 200


# ── Seller: Delete product ────────────────────────────────────────────────────

@product_bp.route("/product/<int:product_id>", methods=["DELETE"])
@seller_required
def delete_product(product_id):
    result = ProductService.delete_product(session["user_id"], product_id)
    return jsonify(result), 200


# ── Seller: Upload product image ──────────────────────────────────────────────

@product_bp.route("/product/<int:product_id>/image", methods=["POST"])
@seller_required
def upload_product_image(product_id):
    if "image" not in request.files:
        return jsonify({"error": "No image file provided."}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp."}), 400

    upload_folder = os.path.join(current_app.static_folder, "uploads", "product_images")
    os.makedirs(upload_folder, exist_ok=True)

    ext = file.filename.rsplit(".", 1)[1].lower()
    image_name = f"product_{product_id}_{session['user_id']}.{ext}"
    file.save(os.path.join(upload_folder, image_name))

    updated = ProductService.update_product_image(session["user_id"], product_id, image_name)
    return jsonify({
        "message": "Product image uploaded successfully.",
        "product": updated
    }), 200


# ── Seller: Get categories ────────────────────────────────────────────────────

@product_bp.route("/seller/categories", methods=["GET"])
@seller_required
def get_categories_seller():
    categories = ProductService.get_categories()
    return jsonify(categories), 200
