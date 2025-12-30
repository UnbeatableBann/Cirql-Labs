class AppError(Exception):
    """
    Base application exception.
    """
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DatabaseError(AppError):
    def __init__(self, message: str = "Database error"):
        super().__init__(message, status_code=500)


class DuplicateDataError(AppError):
    def __init__(self, message: str = "Duplicate data"):
        super().__init__(message, status_code=409)


class ExternalServiceError(AppError):
    def __init__(self, message: str = "External service failed"):
        super().__init__(message, status_code=502)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)
