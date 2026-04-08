from .interfaces import IProductService, IProductRepository, ICategoryRepository
from .exceptions import DuplicateCategoryError, ProductValidationError, ProductNotFoundError


class ProductService(IProductService):

    def __init__(
        self,
        product_repo: IProductRepository,
        category_repo: ICategoryRepository,
    ) -> None:
        self._products = product_repo
        self._categories = category_repo

    # ── Serializers ───────────────────────────────────────────────────────────

    @staticmethod
    def _serialize(product) -> dict:
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
            "created_at": product.created_at.strftime("%Y-%m-%d") if product.created_at else "",
        }

    @staticmethod
    def _serialize_detail(product) -> dict:
        seller = product.seller
        return {
            **ProductService._serialize(product),
            "seller_name": seller.name if seller else "Unknown Seller",
            "seller_email": seller.email if seller else "",
            "seller_image": seller.profile_image if seller else "",
        }

    # ── Validation helpers ────────────────────────────────────────────────────

    @staticmethod
    def _parse_price(value) -> float:
        try:
            price = float(value)
        except (TypeError, ValueError):
            raise ProductValidationError("Price must be a valid positive number.")
        if price < 0:
            raise ProductValidationError("Price must be a valid positive number.")
        return price

    @staticmethod
    def _parse_stock(value) -> int:
        try:
            qty = int(value)
        except (TypeError, ValueError):
            raise ProductValidationError("Stock quantity must be a valid non-negative number.")
        if qty < 0:
            raise ProductValidationError("Stock quantity must be a valid non-negative number.")
        return qty

    @staticmethod
    def _parse_category_id(value):
        if not value:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ProductValidationError("Category ID must be a valid integer.")

    # ── Customer ──────────────────────────────────────────────────────────────

    def get_all_products(self) -> list:
        return [self._serialize(p) for p in self._products.get_all()]

    def get_product_detail(self, product_id: int) -> dict:
        product = self._products.get_by_id_or_none(product_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found.")
        return self._serialize_detail(product)

    # ── Seller ────────────────────────────────────────────────────────────────

    def get_seller_products(self, seller_id: int) -> list:
        return [self._serialize(p) for p in self._products.get_all_by_seller(seller_id)]

    def add_product(self, seller_id: int, data: dict) -> dict:
        name = data.get("name", "").strip()
        if not name:
            raise ProductValidationError("Product name is required.")

        price = self._parse_price(data.get("price"))
        stock_quantity = self._parse_stock(data.get("stock_quantity", 0))
        category_id = self._parse_category_id(data.get("category_id"))

        product = self._products.create(
            {
                "name": name,
                "description": data.get("description", "").strip(),
                "price": price,
                "stock_quantity": stock_quantity,
                "category_id": category_id,
                "seller_id": seller_id,
                "image_name": "",
            }
        )
        return self._serialize(product)

    def update_product(self, seller_id: int, product_id: int, data: dict) -> dict:
        product = self._products.get_by_id_and_seller(product_id, seller_id)

        name = data.get("name", "").strip()
        if not name:
            raise ProductValidationError("Product name is required.")

        price = self._parse_price(data.get("price"))
        stock_quantity = self._parse_stock(data.get("stock_quantity", 0))
        category_id = self._parse_category_id(data.get("category_id"))

        updated = self._products.update(
            product,
            {
                "name": name,
                "description": data.get("description", "").strip(),
                "price": price,
                "stock_quantity": stock_quantity,
                "category_id": category_id,
            },
        )
        return self._serialize(updated)

    def delete_product(self, seller_id: int, product_id: int) -> dict:
        product = self._products.get_by_id_and_seller(product_id, seller_id)
        if product is None:
            raise ProductNotFoundError(f"Product {product_id} not found or not owned by you.")
        self._products.delete(product)
        return {"message": "Product deleted successfully."}

    def update_product_image(self, seller_id: int, product_id: int, image_name: str) -> dict:
        product = self._products.get_by_id_and_seller(product_id, seller_id)
        updated = self._products.update_image(product, image_name)
        return self._serialize(updated)

    # ── Categories ────────────────────────────────────────────────────────────

    def get_categories(self) -> list:
        return [{"id": c.id, "name": c.name} for c in self._categories.get_all()]
    
    def add_category(self, name: str, description: str = "") -> dict:
        existing = self._categories.get_by_name(name)
        if existing:
            raise DuplicateCategoryError(f"Category '{name}' already exists.")
        category = self._categories.create(name, description)
        return {"id": category.id, "name": category.name, "description": category.description}
