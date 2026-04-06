from .interfaces import ISellerService, ISellerRepository
from .base_user_service import BaseUserService


class SellerService(BaseUserService, ISellerService):

    def __init__(self, repo: ISellerRepository) -> None:
        super().__init__(repo)

    @property
    def user_type(self) -> str:
        return "seller"

    def _map_profile(self, seller) -> dict:
        return {
            "id": seller.id,
            "user_type": self.user_type,
            "name": seller.name,
            "email": seller.email,
            "phone_number": seller.phone_number or "",
            "address": seller.business_address or "",  # seller uses business_address
            "profile_image": seller.profile_image or "",
        }

