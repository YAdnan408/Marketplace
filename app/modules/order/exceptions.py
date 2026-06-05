from app.shared import APIException


class OrderValidationError(APIException):
    """Raised when cart data or shipping details fail validation."""
    def __init__(self, message="Invalid order data"):
        super().__init__(
            message=message,
            status_code=400,
            code="ORDER_VALIDATION_ERROR"
        )


class InsufficientStockError(APIException):
    """Raised when a requested quantity exceeds available stock."""
    def __init__(self, message="Insufficient stock"):
        super().__init__(
            message=message,
            status_code=400,
            code="INSUFFICIENT_STOCK"
        )


class OrderNotFoundError(APIException):
    """Raised when an order cannot be found by the given criteria."""
    def __init__(self, message="Order not found"):
        super().__init__(
            message=message,
            status_code=404,
            code="ORDER_NOT_FOUND"
        )


class OrderPlacementError(APIException):
    """Raised when the database transaction for placing an order fails."""
    def __init__(self, message="Failed to place order"):
        super().__init__(
            message=message,
            status_code=500,
            code="ORDER_PLACEMENT_FAILED"
        )


class OrderStatusError(APIException):
    """Raised when a status transition is not permitted."""
    def __init__(self, message="Invalid order status transition"):
        super().__init__(
            message=message,
            status_code=400,
            code="ORDER_STATUS_ERROR"
        )