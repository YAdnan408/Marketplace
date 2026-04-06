from .interfaces import ICustomerService, ICustomerRepository
from .base_user_service import BaseUserService


class CustomerService(BaseUserService, ICustomerService):

    def __init__(self, repo: ICustomerRepository) -> None:
        super().__init__(repo)

    @property
    def user_type(self) -> str:
        return "customer"

    def _map_profile(self, customer) -> dict:
        return {
            "id": customer.id,
            "user_type": self.user_type,
            "name": customer.name,
            "email": customer.email,
            "phone_number": customer.phone_number or "",
            "address": customer.address or "",
            "profile_image": customer.profile_image or "",
        }

