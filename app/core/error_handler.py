"""
Global error handler for FastAPI
"""
import logging
from typing import Union
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError as PydanticValidationError

from app.core.exceptions import AdMasterException

logger = logging.getLogger(__name__)


async def admaster_exception_handler(
    request: Request,
    exc: AdMasterException,
) -> JSONResponse:
    """Handle custom AdMaster exceptions"""
    logger.error(
        f"AdMasterException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
        },
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


async def validation_exception_handler(
    request: Request,
    exc: Union[RequestValidationError, PydanticValidationError],
) -> JSONResponse:
    """Handle Pydantic validation errors"""
    errors = []
    if isinstance(exc, RequestValidationError):
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            errors.append({
                "field": field,
                "message": error.get("msg"),
                "type": error.get("type"),
            })
    else:
        # Pydantic ValidationError
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", []))
            errors.append({
                "field": field,
                "message": error.get("msg"),
                "type": error.get("type"),
            })
    
    logger.warning(
        f"Validation error: {len(errors)} errors",
        extra={
            "errors": errors,
            "path": request.url.path,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "message": "Validation failed",
                "code": "VALIDATION_ERROR",
                "status_code": 422,
                "details": {
                    "errors": errors,
                },
            }
        },
    )


async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Handle all other exceptions"""
    logger.exception(
        f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
        extra={
            "exception_type": type(exc).__name__,
            "path": request.url.path,
        },
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "code": "INTERNAL_SERVER_ERROR",
                "status_code": 500,
                "details": {},
            }
        },
    )

