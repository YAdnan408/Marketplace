class ProductValidationError(Exception):
    """Raised when product input fails validation (missing name, bad price, etc.)."""
    pass


class ProductNotFoundError(Exception):
    """Raised when a product cannot be found by the given criteria."""
    pass
