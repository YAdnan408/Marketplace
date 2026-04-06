from abc import ABC, abstractmethod


# ── Repository interfaces ──────────────────────────────────────────────────────

class IProductRepository(ABC):

    @abstractmethod
    def get_all(self):
        ...

    @abstractmethod
    def get_all_by_seller(self, seller_id: int):
        ...

    @abstractmethod
    def get_by_id(self, product_id: int):
        ...

    @abstractmethod
    def get_by_id_or_none(self, product_id: int):
        ...

    @abstractmethod
    def get_by_id_and_seller(self, product_id: int, seller_id: int):
        ...

    @abstractmethod
    def create(self, data: dict):
        ...

    @abstractmethod
    def update(self, product, data: dict):
        ...

    @abstractmethod
    def update_image(self, product, image_name: str):
        ...

    @abstractmethod
    def delete(self, product) -> None:
        ...


class ICategoryRepository(ABC):

    @abstractmethod
    def get_all(self):
        ...

    @abstractmethod
    def get_by_id(self, category_id: int):
        ...


# ── Service interface ─────────────────────────────────────────────────────────

class IProductService(ABC):

    @abstractmethod
    def get_all_products(self) -> list:
        ...

    @abstractmethod
    def get_seller_products(self, seller_id: int) -> list:
        ...

    @abstractmethod
    def get_product_detail(self, product_id: int) -> dict:
        ...

    @abstractmethod
    def add_product(self, seller_id: int, data: dict) -> dict:
        ...

    @abstractmethod
    def update_product(self, seller_id: int, product_id: int, data: dict) -> dict:
        ...

    @abstractmethod
    def delete_product(self, seller_id: int, product_id: int) -> dict:
        ...

    @abstractmethod
    def update_product_image(self, seller_id: int, product_id: int, image_name: str) -> dict:
        ...

    @abstractmethod
    def get_categories(self) -> list:
        ...
