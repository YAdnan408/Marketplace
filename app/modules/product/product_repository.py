from ...extensions import db
from ...models.product import Product
from .interfaces import IProductRepository


class ProductRepository(IProductRepository):

    def get_all(self):
        return (
            Product.query
            .filter(Product.stock_quantity > 0)
            .order_by(Product.created_at.desc())
            .all()
        )

    def get_all_by_seller(self, seller_id: int):
        return (
            Product.query
            .filter_by(seller_id=seller_id)
            .order_by(Product.created_at.desc())
            .all()
        )

    def get_by_id(self, product_id: int):
        return Product.query.get_or_404(product_id)

    def get_by_id_or_none(self, product_id: int):
        return Product.query.get(product_id)

    def get_by_id_and_seller(self, product_id: int, seller_id: int):
        return Product.query.filter_by(id=product_id, seller_id=seller_id).first()

    def create(self, data: dict):
        product = Product(
            name=data["name"],
            description=data.get("description", ""),
            price=data["price"],
            stock_quantity=data.get("stock_quantity", 0),
            category_id=data.get("category_id"),
            seller_id=data["seller_id"],
            image_name=data.get("image_name", ""),
        )
        db.session.add(product)
        db.session.commit()
        return product

    def update(self, product, data: dict):
        product.name = data.get("name", product.name)
        product.description = data.get("description", product.description)
        product.price = data.get("price", product.price)
        product.stock_quantity = data.get("stock_quantity", product.stock_quantity)
        product.category_id = data.get("category_id", product.category_id)
        db.session.commit()
        return product

    def update_image(self, product, image_name: str):
        product.image_name = image_name
        db.session.commit()
        return product

    def delete(self, product) -> None:
        db.session.delete(product)
        db.session.commit()
