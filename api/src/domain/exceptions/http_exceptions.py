from .base import AppError


class NotFoundError(AppError):
    status_code = 404
    title = "Not Found"
    detail = "The requested resource was not found."


class ForbiddenError(AppError):
    status_code = 403
    title = "Forbidden"
    detail = "You do not have permission to perform this action."


class ConflictError(AppError):
    status_code = 409
    title = "Conflict"
    detail = "The request conflicts with the current state of the resource."


class ValidationError(AppError):
    status_code = 422
    title = "Unprocessable Entity"
    detail = "The request had semantic errors."


class UnauthorizedError(AppError):
    code = 401
    title = "Unauthorized"
    description = "Login is required."
