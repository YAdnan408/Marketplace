import os
from flask import Blueprint, request, jsonify, session, current_app

from app.decorators import login_required, seller_required, customer_required
from app.shared.file_upload import allowed_file, get_extension, save_upload

from .product_repository import ProductRepository
from .category_repository import CategoryRepository
from .product_service import ProductService
from .exceptions import ProductValidationError, ProductNotFoundError, DuplicateCategoryError

product_bp = Blueprint("product", __name__, url_prefix="/api/products")

# ── Dependency wiring (DIP) ───────────────────────────────────────────────────

_product_service = ProductService(ProductRepository(), CategoryRepository())


# ── Customer: Get categories ──────────────────────────────────────────────────

@product_bp.route("/categories", methods=["GET"])
@login_required
def get_categories_customer():
    return jsonify(_product_service.get_categories()), 200

@product_bp.route("/categories", methods=["POST"])
@login_required
def add_category():
    try:
        name = request.json.get("name", "").strip()
        description = request.json.get("description", "").strip()
        if not name:
            return jsonify({"error": "Category name is required."}), 400

        category = _product_service.add_category(name, description)
        return jsonify({"message": "Category added successfully.", "category": category}), 201
    except DuplicateCategoryError as exc:
        return jsonify({"error": str(exc)}), 400


# ── Customer/Seller: Browse products (role-aware) ─────────────────────────────

@product_bp.route("/", methods=["GET"])
@login_required
def get_products():
    user_type = session.get("user_type")
    if user_type == "customer":
        return jsonify(_product_service.get_all_products()), 200
    if user_type == "seller":
        return jsonify(_product_service.get_seller_products(session["user_id"])), 200
    return jsonify({"error": "Invalid user type"}), 400


# ── Customer: Get single product detail ──────────────────────────────────────

@product_bp.route("/<int:product_id>", methods=["GET"])
@customer_required
def get_product_detail(product_id):
    try:
        product = _product_service.get_product_detail(product_id)
    except ProductNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    return jsonify(product), 200


# ── Seller: Add product ───────────────────────────────────────────────────────

@product_bp.route("/", methods=["POST"])
@seller_required
def add_product():
    try:
        result = _product_service.add_product(session["user_id"], request.json)
    except ProductValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"message": "Product added successfully.", "product": result}), 201


# ── Seller: Update product ────────────────────────────────────────────────────

@product_bp.route("/<int:product_id>", methods=["PUT"])
@seller_required
def update_product(product_id):
    try:
        result = _product_service.update_product(session["user_id"], product_id, request.json)
    except ProductValidationError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"message": "Product updated successfully.", "product": result}), 200


# ── Seller: Delete product ────────────────────────────────────────────────────

@product_bp.route("/<int:product_id>", methods=["DELETE"])
@seller_required
def delete_product(product_id):
    result = _product_service.delete_product(session["user_id"], product_id)
    return jsonify(result), 200


# ── Seller: Upload product image ──────────────────────────────────────────────

@product_bp.route("/image/<int:product_id>", methods=["POST"])
@seller_required
def upload_product_image(product_id):
    file = request.files.get("image")
    if file is None or file.filename == "":
        return jsonify({"error": "No image file provided."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Allowed: png, jpg, jpeg, gif, webp."}), 400

    ext = get_extension(file.filename)
    image_name = f"product_{product_id}_{session['user_id']}.{ext}"
    upload_folder = os.path.join(current_app.static_folder, "uploads", "product_images")
    save_upload(file, upload_folder, image_name)

    updated = _product_service.update_product_image(session["user_id"], product_id, image_name)
    return jsonify({
        "message": "Product image uploaded successfully.",
        "product": updated,
    }), 200
