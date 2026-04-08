from app.shared.exceptions import APIException


class OrderValidationError(APIException):
    def __init__(self, message="Invalid order data"):
        super().__init__(message, 400, "ORDER_VALIDATION_ERROR")


class InsufficientStockError(APIException):
    def __init__(self, message="Insufficient stock"):
        super().__init__(message, 400, "INSUFFICIENT_STOCK")


class OrderNotFoundError(APIException):
    def __init__(self, message="Order not found"):
        super().__init__(message, 404, "ORDER_NOT_FOUND")


class OrderPlacementError(APIException):
    def __init__(self, message="Failed to place order"):
        super().__init__(message, 500, "ORDER_PLACEMENT_FAILED")