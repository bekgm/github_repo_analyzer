class AppError(Exception):
    """Base application error."""

    def __init__(self, message: str = "An unexpected error occurred", code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(AppError):
    def __init__(self, entity: str = "Resource", identifier: str = ""):
        super().__init__(
            message=f"{entity} not found: {identifier}",
            code="NOT_FOUND",
        )


class AlreadyExistsError(AppError):
    def __init__(self, entity: str = "Resource", identifier: str = ""):
        super().__init__(
            message=f"{entity} already exists: {identifier}",
            code="ALREADY_EXISTS",
        )


class ExternalServiceError(AppError):
    def __init__(self, service: str, detail: str = ""):
        super().__init__(
            message=f"External service error [{service}]: {detail}",
            code="EXTERNAL_SERVICE_ERROR",
        )


class RateLimitExceededError(AppError):
    def __init__(self):
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            code="RATE_LIMIT_EXCEEDED",
        )


class ValidationError(AppError):
    def __init__(self, detail: str = ""):
        super().__init__(
            message=f"Validation error: {detail}",
            code="VALIDATION_ERROR",
        )
