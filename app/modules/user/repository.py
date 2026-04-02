from ...extensions import db
from ...models.customer import Customer
from ...models.seller import Seller


class CustomerRepository:

    @staticmethod
    def get_by_email(email):
        return Customer.query.filter_by(email=email).first()

    @staticmethod
    def get_by_id(id):
        return Customer.query.get_or_404(id)

    @staticmethod
    def create(data):
        customer = Customer(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password"),
            phone_number=data.get("phone_number"),
            address=data.get("address")
        )
        db.session.add(customer)
        db.session.commit()
        return customer

    @staticmethod
    def update(customer, data):
        customer.name = data.get("name", customer.name)
        customer.phone_number = data.get("phone_number", customer.phone_number)
        customer.address = data.get("address", customer.address)
        db.session.commit()
        return customer

    @staticmethod
    def update_profile_image(customer, image_name):
        customer.profile_image = image_name
        db.session.commit()
        return customer


class SellerRepository:

    @staticmethod
    def get_by_email(email):
        return Seller.query.filter_by(email=email).first()

    @staticmethod
    def get_by_id(id):
        return Seller.query.get_or_404(id)

    @staticmethod
    def create(data):
        seller = Seller(
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password"),
            phone_number=data.get("phone_number"),
            business_address=data.get("address"),
            role="seller"
        )
        db.session.add(seller)
        db.session.commit()
        return seller

    @staticmethod
    def update(seller, data):
        seller.name = data.get("name", seller.name)
        seller.phone_number = data.get("phone_number", seller.phone_number)
        seller.business_address = data.get("address", seller.business_address)
        db.session.commit()
        return seller

    @staticmethod
    def update_profile_image(seller, image_name):
        seller.profile_image = image_name
        db.session.commit()
        return seller
