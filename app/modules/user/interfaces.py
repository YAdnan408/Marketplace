from abc import ABC, abstractmethod


# ── Repository interfaces ──────────────────────────────────────────────────────

class ICustomerRepository(ABC):


    @abstractmethod
    def get_by_email(self, email: str):
        ...

    @abstractmethod
    def get_by_id(self, id: int):
        ...

    @abstractmethod
    def create(self, data: dict):
        ...

    @abstractmethod
    def update(self, customer, data: dict):
        ...

    @abstractmethod
    def update_profile_image(self, customer, image_name: str):
        ...


class ISellerRepository(ABC):

    @abstractmethod
    def get_by_email(self, email: str):
        ...

    @abstractmethod
    def get_by_id(self, id: int):
        ...

    @abstractmethod
    def create(self, data: dict):
        ...

    @abstractmethod
    def update(self, seller, data: dict):
        ...

    @abstractmethod
    def update_profile_image(self, seller, image_name: str):
        ...


# ── Service interfaces ─────────────────────────────────────────────────────────

class IUserService(ABC):
    """Shared contract for all user-type services."""

    @abstractmethod
    def signup(self, data: dict) -> dict:
        ...

    @abstractmethod
    def login(self, data: dict) -> dict:
        ...

    @abstractmethod
    def get_profile(self, user_id: int) -> dict:
        ...

    @abstractmethod
    def update_profile(self, user_id: int, data: dict) -> dict:
        ...

    @abstractmethod
    def update_profile_image(self, user_id: int, image_name: str) -> dict:
        ...


class ICustomerService(IUserService):
    """Marker interface — reserved for customer-specific extensions."""


class ISellerService(IUserService):
    """Marker interface — reserved for seller-specific extensions."""
