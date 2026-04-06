class UserValidationError(Exception):
    """Raised when required fields are missing or have invalid values."""
    pass


class UserAlreadyExistsError(Exception):
    """Raised when attempting to register with an already-registered email."""
    pass


class UserNotFoundError(Exception):
    """Raised when a user cannot be found by the given criteria."""
    pass


class InvalidCredentialsError(Exception):
    """Raised when login credentials do not match any stored record."""
    pass
