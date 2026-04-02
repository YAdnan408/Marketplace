from werkzeug.security import generate_password_hash, check_password_hash
from .repository import CustomerRepository, SellerRepository


class CustomerService:

    # ── Auth ──────────────────────────────────────────────────────

    @staticmethod
    def signup(data):
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            return None, "Name, email, and password are required."

        if CustomerRepository.get_by_email(email):
            return None, "A customer account with this email already exists."

        hashed_password = generate_password_hash(password)

        customer = CustomerRepository.create({
            "name": name,
            "email": email,
            "password": hashed_password,
            "phone_number": data.get("phone_number", ""),
            "address": data.get("address", "")
        })

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "user_type": "customer"
        }, None

    @staticmethod
    def login(data):
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return None, "Email and password are required."

        customer = CustomerRepository.get_by_email(email)

        if not customer:
            return None, "No customer account found with this email."

        if not check_password_hash(customer.password, password):
            return None, "Incorrect password."

        return {
            "id": customer.id,
            "name": customer.name,
            "email": customer.email,
            "user_type": "customer"
        }, None

    # ── Profile ───────────────────────────────────────────────────

    @staticmethod
    def get_profile(customer_id):
        customer = CustomerRepository.get_by_id(customer_id)
        return {
            "id": customer.id,
            "user_type": "customer",
            "name": customer.name,
            "email": customer.email,
            "phone_number": customer.phone_number or "",
            "address": customer.address or "",
            "profile_image": customer.profile_image or ""
        }

    @staticmethod
    def update_profile(customer_id, data):
        customer = CustomerRepository.get_by_id(customer_id)
        updated = CustomerRepository.update(customer, data)
        return {
            "id": updated.id,
            "name": updated.name,
            "email": updated.email,
            "phone_number": updated.phone_number or "",
            "address": updated.address or "",
            "profile_image": updated.profile_image or ""
        }

    @staticmethod
    def update_profile_image(customer_id, image_name):
        customer = CustomerRepository.get_by_id(customer_id)
        updated = CustomerRepository.update_profile_image(customer, image_name)
        return {"profile_image": updated.profile_image}


class SellerService:

    # ── Auth ──────────────────────────────────────────────────────

    @staticmethod
    def signup(data):
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            return None, "Name, email, and password are required."

        if SellerRepository.get_by_email(email):
            return None, "A seller account with this email already exists."

        hashed_password = generate_password_hash(password)

        seller = SellerRepository.create({
            "name": name,
            "email": email,
            "password": hashed_password,
            "phone_number": data.get("phone_number", ""),
            "address": data.get("address", "")
        })

        return {
            "id": seller.id,
            "name": seller.name,
            "email": seller.email,
            "user_type": "seller"
        }, None

    @staticmethod
    def login(data):
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return None, "Email and password are required."

        seller = SellerRepository.get_by_email(email)

        if not seller:
            return None, "No seller account found with this email."

        if not check_password_hash(seller.password, password):
            return None, "Incorrect password."

        return {
            "id": seller.id,
            "name": seller.name,
            "email": seller.email,
            "user_type": "seller"
        }, None

    # ── Profile ───────────────────────────────────────────────────

    @staticmethod
    def get_profile(seller_id):
        seller = SellerRepository.get_by_id(seller_id)
        return {
            "id": seller.id,
            "user_type": "seller",
            "name": seller.name,
            "email": seller.email,
            "phone_number": seller.phone_number or "",
            "address": seller.business_address or "",
            "profile_image": seller.profile_image or ""
        }

    @staticmethod
    def update_profile(seller_id, data):
        seller = SellerRepository.get_by_id(seller_id)
        updated = SellerRepository.update(seller, data)
        return {
            "id": updated.id,
            "name": updated.name,
            "email": updated.email,
            "phone_number": updated.phone_number or "",
            "address": updated.business_address or "",
            "profile_image": updated.profile_image or ""
        }

    @staticmethod
    def update_profile_image(seller_id, image_name):
        seller = SellerRepository.get_by_id(seller_id)
        updated = SellerRepository.update_profile_image(seller, image_name)
        return {"profile_image": updated.profile_image}
