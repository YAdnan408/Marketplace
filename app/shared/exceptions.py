class APIException(Exception):
    def __init__(self, message, status_code=400, code="ERROR"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class InvalidFileError(APIException):
    """Raised when an uploaded file is missing or has a disallowed type."""
    def __init__(self, message="Invalid file"):
        super().__init__(message, status_code=400, code="INVALID_FILE")


class UnauthorizedError(APIException):
    """Raised when a request is made without being logged in."""
    def __init__(self, message="Login required"):
        super().__init__(message, status_code=401, code="UNAUTHORIZED")


class ForbiddenError(APIException):
    """Raised when a logged-in user lacks the required role."""
    def __init__(self, message="Access forbidden"):
        super().__init__(message, status_code=403, code="FORBIDDEN")