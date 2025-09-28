"""
Custom exception handlers for OpenVoice API
"""

import logging
from typing import Union
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class OpenVoiceAPIException(Exception):
    """Base exception for OpenVoice API"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class AudioProcessingError(OpenVoiceAPIException):
    """Audio processing related errors"""
    def __init__(self, message: str):
        super().__init__(message, 422)


class FileValidationError(OpenVoiceAPIException):
    """File validation related errors"""
    def __init__(self, message: str):
        super().__init__(message, 400)


class ConversionError(OpenVoiceAPIException):
    """Voice conversion related errors"""
    def __init__(self, message: str):
        super().__init__(message, 500)


def setup_exception_handlers(app: FastAPI):
    """Setup global exception handlers"""
    
    @app.exception_handler(OpenVoiceAPIException)
    async def openvoice_exception_handler(request: Request, exc: OpenVoiceAPIException):
        logger.error(f"OpenVoice API Exception: {exc.message}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "OpenVoice API Error",
                "message": exc.message,
                "type": exc.__class__.__name__
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        logger.warning(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTP Error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def starlette_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(f"Starlette Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "Request Error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": exc.errors()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred",
                "type": "InternalError"
            }
        )
