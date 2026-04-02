from ...extensions import db
from ...models.product import Product
from ...models.category import Category


class ProductRepository:

    # ── Products ──────────────────────────────────────────────────

    @staticmethod
    def get_all():
        return Product.query.filter(Product.stock_quantity > 0).order_by(Product.created_at.desc()).all()

    @staticmethod
    def get_all_by_seller(seller_id):
        return Product.query.filter_by(seller_id=seller_id).order_by(Product.created_at.desc()).all()

    @staticmethod
    def get_by_id(product_id):
        return Product.query.get_or_404(product_id)

    @staticmethod
    def get_by_id_or_none(product_id):
        """Returns the product or None — used for detail page (no 404 abort)."""
        return Product.query.get(product_id)

    @staticmethod
    def get_by_id_and_seller(product_id, seller_id):
        """Ensures a seller can only access their own products."""
        return Product.query.filter_by(id=product_id, seller_id=seller_id).first_or_404()

    @staticmethod
    def create(data):
        product = Product(
            name=data.get("name"),
            description=data.get("description", ""),
            price=data.get("price"),
            stock_quantity=data.get("stock_quantity", 0),
            category_id=data.get("category_id"),
            seller_id=data.get("seller_id"),
            image_name=data.get("image_name", "")
        )
        db.session.add(product)
        db.session.commit()
        return product

    @staticmethod
    def update(product, data):
        product.name = data.get("name", product.name)
        product.description = data.get("description", product.description)
        product.price = data.get("price", product.price)
        product.stock_quantity = data.get("stock_quantity", product.stock_quantity)
        product.category_id = data.get("category_id", product.category_id)
        db.session.commit()
        return product

    @staticmethod
    def update_image(product, image_name):
        product.image_name = image_name
        db.session.commit()
        return product

    @staticmethod
    def delete(product):
        db.session.delete(product)
        db.session.commit()

    # ── Categories ────────────────────────────────────────────────

    @staticmethod
    def get_all_categories():
        return Category.query.order_by(Category.name).all()

    @staticmethod
    def get_category_by_id(category_id):
        return Category.query.get(category_id)