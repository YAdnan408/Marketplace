from ...extensions import db
from ...models.customer import Customer
from .interfaces import ICustomerRepository


class CustomerRepository(ICustomerRepository):

    def get_by_email(self, email: str):
        return Customer.query.filter_by(email=email).first()

    def get_by_id(self, id: int):
        return Customer.query.get_or_404(id)

    def create(self, data: dict):
        customer = Customer(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            phone_number=data.get("phone_number", ""),
            address=data.get("address", ""),
        )
        db.session.add(customer)
        db.session.commit()
        return customer

    def update(self, customer, data: dict):
        customer.name = data.get("name", customer.name)
        customer.phone_number = data.get("phone_number", customer.phone_number)
        customer.address = data.get("address", customer.address)
        db.session.commit()
        return customer

    def update_profile_image(self, customer, image_name: str):
        customer.profile_image = image_name
        db.session.commit()
        return customer
