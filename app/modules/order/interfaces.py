from abc import ABC, abstractmethod


# ── Repository interface ───────────────────────────────────────────────────────

class IOrderRepository(ABC):

    # ── Write / checkout ──────────────────────────────────────────────────────

    @abstractmethod
    def create_order(self, customer_id: int, total_price: float, shipping_address: str):
        """Create and flush a new Order (does not commit — atomic_commit does)."""
        ...

    @abstractmethod
    def create_order_items(self, order_id: int, validated_items: list) -> None:
        """Bulk-insert all order items in a single round-trip."""
        ...

    @abstractmethod
    def get_products_for_checkout(self, product_ids: list[int]) -> list:
        """Batch row-level lock all products in one query, ordered by id."""
        ...

    @abstractmethod
    def decrement_stock(self, product, quantity: int):
        """Subtract quantity from product.stock_quantity (in-memory only)."""
        ...

    # ── Customer reads ────────────────────────────────────────────────────────

    @abstractmethod
    def get_orders_by_customer(self, customer_id: int):
        """Return all orders for a customer, newest first."""
        ...

    @abstractmethod
    def get_order_by_id_and_customer(self, order_id: int, customer_id: int):
        """Return a single order owned by the customer, or 404."""
        ...

    # ── Seller reads + writes ─────────────────────────────────────────────────

    @abstractmethod
    def get_orders_by_seller(self, seller_id: int):
        """Return all orders that contain at least one item from this seller."""
        ...

    @abstractmethod
    def get_order_by_id_and_seller(self, order_id: int, seller_id: int):
        """Return a single order that contains items from this seller, or 404."""
        ...

    @abstractmethod
    def update_order_status(self, order, new_status: str):
        """Update order.status and commit."""
        ...

    # ── Transaction control ───────────────────────────────────────────────────

    @abstractmethod
    def atomic_commit(self) -> None:
        """Commit; rollback and re-raise on any DB error."""
        ...


# ── Service interface ──────────────────────────────────────────────────────────

class IOrderService(ABC):

    # ── Customer ──────────────────────────────────────────────────────────────

    @abstractmethod
    def place_order(
        self,
        customer_id: int,
        cart_items: list,
        shipping_address: str,
        shipping_cost: float,
    ) -> dict:
        """Validate, create, and persist a full order. Returns the order summary dict."""
        ...

    @abstractmethod
    def get_customer_orders(self, customer_id: int) -> list:
        """Return the full order history for a customer."""
        ...

    # ── Seller ────────────────────────────────────────────────────────────────

    @abstractmethod
    def get_seller_orders(self, seller_id: int) -> list:
        """Return all orders that contain items belonging to this seller."""
        ...

    @abstractmethod
    def approve_order(self, seller_id: int, order_id: int) -> dict:
        """Approve a pending order. Only the seller who owns items in it may approve."""
        ...