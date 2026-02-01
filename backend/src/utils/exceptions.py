"""Custom exceptions for the MgmtSays application."""

from typing import Any


class MgmtSaysError(Exception):
    """Base exception for all MgmtSays errors."""

    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(MgmtSaysError):
    """Resource not found error."""

    def __init__(
        self,
        resource: str,
        identifier: str | int,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier, **(details or {})},
        )


class ValidationError(MgmtSaysError):
    """Validation error for invalid input."""

    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field, **(details or {})} if field else details,
        )


class AuthenticationError(MgmtSaysError):
    """Authentication failed error."""

    def __init__(
        self,
        message: str = "Authentication required",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            details=details,
        )


class AuthorizationError(MgmtSaysError):
    """Authorization/permission denied error."""

    def __init__(
        self,
        message: str = "Permission denied",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            details=details,
        )


class ExternalServiceError(MgmtSaysError):
    """Error communicating with external service."""

    def __init__(
        self,
        service: str,
        message: str,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=f"External service error ({service}): {message}",
            code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **(details or {})},
        )


class RateLimitError(MgmtSaysError):
    """Rate limit exceeded error."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: int | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_ERROR",
            details={"retry_after": retry_after, **(details or {})},
        )


class DocumentProcessingError(MgmtSaysError):
    """Error processing a document."""

    def __init__(
        self,
        message: str,
        document_id: str | None = None,
        stage: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="DOCUMENT_PROCESSING_ERROR",
            details={
                "document_id": document_id,
                "stage": stage,
                **(details or {}),
            },
        )


class NLPError(MgmtSaysError):
    """Error in NLP processing."""

    def __init__(
        self,
        message: str,
        component: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            code="NLP_ERROR",
            details={"component": component, **(details or {})},
        )
