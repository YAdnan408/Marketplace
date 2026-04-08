from app.shared import APIException


class UserValidationError(APIException):
    """Raised when required fields are missing or have invalid values."""
    def __init__(self, message="Invalid user data"):
        super().__init__(
            message=message,
            status_code=400,
            code="USER_VALIDATION_ERROR"
        )

class InvalidUserTypeError(APIException):
    """Raised when an invalid user type is provided during signup or login."""
    def __init__(self, message="Invalid account type. Choose customer or seller."):
        super().__init__(
            message=message,
            status_code=400,
            code="INVALID_USER_TYPE"
        )


class UserAlreadyExistsError(APIException):
    """Raised when attempting to register with an already-registered email."""
    def __init__(self, message="User already exists"):
        super().__init__(
            message=message,
            status_code=409,
            code="USER_ALREADY_EXISTS"
        )


class UserNotFoundError(APIException):
    """Raised when a user cannot be found by the given criteria."""
    def __init__(self, message="User not found"):
        super().__init__(
            message=message,
            status_code=404,
            code="USER_NOT_FOUND"
        )


class InvalidCredentialsError(APIException):
    """Raised when login credentials do not match any stored record."""
    def __init__(self, message="Invalid email or password"):
        super().__init__(
            message=message,
            status_code=401,
            code="INVALID_CREDENTIALS"
        )