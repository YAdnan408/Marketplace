from abc import ABC, abstractmethod


# ── Repository interface ───────────────────────────────────────────────────────

class IOrderRepository(ABC):

    @abstractmethod
    def create_order(self, customer_id: int, total_price: float, shipping_address: str):
        ...

    @abstractmethod
    def create_order_items(self, order_id: int, validated_items: list) -> None:
        ...

    @abstractmethod
    def get_products_for_checkout(self, product_ids: list[int]) -> list:
        ...

    @abstractmethod
    def decrement_stock(self, product, quantity: int):
        ...

    @abstractmethod
    def get_orders_by_customer(self, customer_id: int):
        ...

    @abstractmethod
    def get_order_by_id_and_customer(self, order_id: int, customer_id: int):
        ...

    @abstractmethod
    def commit(self) -> None:
        ...

    @abstractmethod
    def rollback(self) -> None:
        ...


# ── Service interface ──────────────────────────────────────────────────────────

class IOrderService(ABC):

    @abstractmethod
    def place_order(
        self,
        customer_id: int,
        cart_items: list,
        shipping_address: str,
        shipping_cost: float,
    ) -> dict:
        ...

    @abstractmethod
    def get_customer_orders(self, customer_id: int) -> list:
        ...