from ...extensions import db
from ...models.seller import Seller
from .interfaces import ISellerRepository


class SellerRepository(ISellerRepository):

    def get_by_email(self, email: str):
        return Seller.query.filter_by(email=email).first()

    def get_by_id(self, id: int):
        return Seller.query.get_or_404(id)

    def create(self, data: dict):
        seller = Seller(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            phone_number=data.get("phone_number", ""),
            business_address=data.get("address", ""),
            role="seller",
        )
        db.session.add(seller)
        db.session.commit()
        return seller

    def update(self, seller, data: dict):
        seller.name = data.get("name", seller.name)
        seller.phone_number = data.get("phone_number", seller.phone_number)
        seller.business_address = data.get("address", seller.business_address)
        db.session.commit()
        return seller

    def update_profile_image(self, seller, image_name: str):
        seller.profile_image = image_name
        db.session.commit()
        return seller
