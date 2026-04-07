from ...models.category import Category
from .interfaces import ICategoryRepository
from ...extensions import db


class CategoryRepository(ICategoryRepository):

    def get_all(self):
        return Category.query.order_by(Category.name).all()

    def get_by_id(self, category_id: int):
        return Category.query.get(category_id)
    
    def get_by_name(self, name: str):
        return Category.query.filter_by(name=name).first()

    def create(self, name: str, description: str = ""):
        category = Category(name=name, description=description)
        db.session.add(category)
        db.session.commit()
        return category