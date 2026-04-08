from app.shared import APIException


class ProductValidationError(APIException):
    """Raised when product input fails validation (missing name, bad price, etc.)."""
    def __init__(self, message="Invalid product data"):
        super().__init__(
            message=message,
            status_code=400,
            code="PRODUCT_VALIDATION_ERROR"
        )


class ProductNotFoundError(APIException):
    """Raised when a product cannot be found by the given criteria."""
    def __init__(self, message="Product not found"):
        super().__init__(
            message=message,
            status_code=404,
            code="PRODUCT_NOT_FOUND"
        )


class DuplicateCategoryError(APIException):
    """Raised when trying to create a category that already exists."""
    def __init__(self, message="Category already exists"):
        super().__init__(
            message=message,
            status_code=409,
            code="DUPLICATE_CATEGORY"
        )