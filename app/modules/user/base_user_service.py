from abc import ABC, abstractmethod

from werkzeug.security import generate_password_hash, check_password_hash

from .exceptions import (
    UserValidationError,
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
)


class BaseUserService(ABC):
    """
    Template Method base for all user-type services.

    Subclasses must implement:
      - user_type  (str property)  — the domain label, e.g. "customer" / "seller"
      - _map_profile(user) -> dict — maps model fields to the profile response dict
                                     (handles field-name differences per user type)

    All shared auth and profile logic lives here once.
    """

    def __init__(self, repo) -> None:
        self._repo = repo

    # ── Abstract hooks ────────────────────────────────────────────────────────

    @property
    @abstractmethod
    def user_type(self) -> str:
        """Domain label used in error messages and response payloads."""
        ...

    @abstractmethod
    def _map_profile(self, user) -> dict:
        """Full profile dict — subclass owns field-name differences."""
        ...

    # ── Shared auth ───────────────────────────────────────────────────────────

    def signup(self, data: dict) -> dict:
        name = data.get("name", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not name or not email or not password:
            raise UserValidationError("Name, email, and password are required.")

        if self._repo.get_by_email(email):
            raise UserAlreadyExistsError(
                f"A {self.user_type} account with this email already exists."
            )

        user = self._repo.create(
            {
                "name": name,
                "email": email,
                "password": generate_password_hash(password),
                "phone_number": data.get("phone_number", ""),
                "address": data.get("address", ""),
            }
        )
        return self._serialize(user)

    def login(self, data: dict) -> dict:
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            raise UserValidationError("Email and password are required.")

        user = self._repo.get_by_email(email)
        if not user:
            raise UserNotFoundError(
                f"No {self.user_type} account found with this email."
            )

        if not check_password_hash(user.password, password):
            raise InvalidCredentialsError("Incorrect password.")

        return self._serialize(user)

    # ── Shared profile ────────────────────────────────────────────────────────

    def get_profile(self, user_id: int) -> dict:
        return self._map_profile(self._repo.get_by_id(user_id))

    def update_profile(self, user_id: int, data: dict) -> dict:
        user = self._repo.get_by_id(user_id)
        updated = self._repo.update(user, data)
        return self._map_profile(updated)

    def update_profile_image(self, user_id: int, image_name: str) -> dict:
        user = self._repo.get_by_id(user_id)
        updated = self._repo.update_profile_image(user, image_name)
        return {"profile_image": updated.profile_image}

    # ── Shared serializer ─────────────────────────────────────────────────────

    def _serialize(self, user) -> dict:
        """Minimal auth payload — used after signup / login."""
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "user_type": self.user_type,
        }
