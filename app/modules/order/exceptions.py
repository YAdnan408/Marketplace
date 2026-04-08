class OrderValidationError(Exception):
    """Raised when cart data or shipping details fail validation."""
    pass


class InsufficientStockError(Exception):
    """Raised when a requested quantity exceeds available stock."""
    pass


class OrderNotFoundError(Exception):
    """Raised when an order cannot be found by the given criteria."""
    pass


class OrderPlacementError(Exception):
    """Raised when the database transaction for placing an order fails."""
    pass