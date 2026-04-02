from .repository import ProductRepository


class ProductService:

    @staticmethod
    def _serialize(product):
        """Converts a Product model to a dict for JSON responses."""
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description or "",
            "price": float(product.price),
            "stock_quantity": product.stock_quantity,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else "Uncategorized",
            "seller_id": product.seller_id,
            "image_name": product.image_name or "",
            "created_at": product.created_at.strftime("%Y-%m-%d") if product.created_at else ""
        }

    @staticmethod
    def _serialize_detail(product):
        """Extended serialization including seller info for the detail page."""
        seller = product.seller
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description or "",
            "price": float(product.price),
            "stock_quantity": product.stock_quantity,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else "Uncategorized",
            "seller_id": product.seller_id,
            "seller_name": seller.name if seller else "Unknown Seller",
            "seller_email": seller.email if seller else "",
            "seller_image": seller.profile_image if seller else "",
            "image_name": product.image_name or "",
            "created_at": product.created_at.strftime("%Y-%m-%d") if product.created_at else ""
        }

    # ── Customer ──────────────────────────────────────────────────

    @staticmethod
    def get_all_products():
        products = ProductRepository.get_all()
        return [ProductService._serialize(p) for p in products]

    @staticmethod
    def get_product_detail(product_id):
        """Returns full product detail including seller info. Returns None if not found."""
        product = ProductRepository.get_by_id_or_none(product_id)
        if product is None:
            return None
        return ProductService._serialize_detail(product)

    # ── Seller ────────────────────────────────────────────────────

    @staticmethod
    def get_seller_products(seller_id):
        products = ProductRepository.get_all_by_seller(seller_id)
        return [ProductService._serialize(p) for p in products]

    @staticmethod
    def add_product(seller_id, data):
        name = data.get("name", "").strip()
        price = data.get("price")
        stock_quantity = data.get("stock_quantity", 0)

        if not name:
            return None, "Product name is required."

        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except (TypeError, ValueError):
            return None, "Price must be a valid positive number."

        try:
            stock_quantity = int(stock_quantity)
            if stock_quantity < 0:
                raise ValueError
        except (TypeError, ValueError):
            return None, "Stock quantity must be a valid non-negative number."

        category_id = data.get("category_id")
        if category_id:
            try:
                category_id = int(category_id)
            except (TypeError, ValueError):
                category_id = None

        product = ProductRepository.create({
            "name": name,
            "description": data.get("description", "").strip(),
            "price": price,
            "stock_quantity": stock_quantity,
            "category_id": category_id,
            "seller_id": seller_id,
            "image_name": ""
        })

        return ProductService._serialize(product), None

    @staticmethod
    def update_product(seller_id, product_id, data):
        product = ProductRepository.get_by_id_and_seller(product_id, seller_id)

        name = data.get("name", "").strip()
        if not name:
            return None, "Product name is required."

        try:
            price = float(data.get("price"))
            if price < 0:
                raise ValueError
        except (TypeError, ValueError):
            return None, "Price must be a valid positive number."

        try:
            stock_quantity = int(data.get("stock_quantity", 0))
            if stock_quantity < 0:
                raise ValueError
        except (TypeError, ValueError):
            return None, "Stock quantity must be a valid non-negative number."

        category_id = data.get("category_id")
        if category_id:
            try:
                category_id = int(category_id)
            except (TypeError, ValueError):
                category_id = None

        updated = ProductRepository.update(product, {
            "name": name,
            "description": data.get("description", "").strip(),
            "price": price,
            "stock_quantity": stock_quantity,
            "category_id": category_id
        })

        return ProductService._serialize(updated), None

    @staticmethod
    def delete_product(seller_id, product_id):
        product = ProductRepository.get_by_id_and_seller(product_id, seller_id)
        ProductRepository.delete(product)
        return {"message": "Product deleted successfully."}

    @staticmethod
    def update_product_image(seller_id, product_id, image_name):
        product = ProductRepository.get_by_id_and_seller(product_id, seller_id)
        updated = ProductRepository.update_image(product, image_name)
        return ProductService._serialize(updated)

    # ── Categories ────────────────────────────────────────────────

    @staticmethod
    def get_categories():
        categories = ProductRepository.get_all_categories()
        return [{"id": c.id, "name": c.name} for c in categories]