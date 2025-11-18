"""
Custom exceptions for the application
"""
from typing import Optional, Dict, Any


class AdMasterException(Exception):
    """Base exception for all AdMaster exceptions"""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response"""
        return {
            "error": {
                "message": self.message,
                "code": self.error_code,
                "status_code": self.status_code,
                "details": self.details,
            }
        }


class ValidationError(AdMasterException):
    """Validation error (400)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details=details,
        )


class NotFoundError(AdMasterException):
    """Resource not found error (404)"""
    
    def __init__(self, resource: str, resource_id: Optional[str] = None):
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with ID '{resource_id}' not found"
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id},
        )


class UnauthorizedError(AdMasterException):
    """Unauthorized error (401)"""
    
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class ForbiddenError(AdMasterException):
    """Forbidden error (403)"""
    
    def __init__(self, message: str = "Forbidden"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class ConflictError(AdMasterException):
    """Conflict error (409)"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )


class InternalServerError(AdMasterException):
    """Internal server error (500)"""
    
    def __init__(self, message: str = "Internal server error", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            details=details,
        )


class ServiceUnavailableError(AdMasterException):
    """Service unavailable error (503)"""
    
    def __init__(self, message: str = "Service unavailable", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=503,
            error_code="SERVICE_UNAVAILABLE",
            details=details,
        )

