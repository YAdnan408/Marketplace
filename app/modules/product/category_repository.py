from ...models.category import Category
from .interfaces import ICategoryRepository


class CategoryRepository(ICategoryRepository):

    def get_all(self):
        return Category.query.order_by(Category.name).all()

    def get_by_id(self, category_id: int):
        return Category.query.get(category_id)
