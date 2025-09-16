"""
Custom exception classes and error handlers for AI Studio Backend
"""

from typing import Dict, Any, Optional, List
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
import logging
import traceback
from datetime import datetime

logger = logging.getLogger(__name__)


# Base Exceptions
class AIStudioException(Exception):
    """Base exception class for AI Studio"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "GENERAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat()
        }


# Model & AI Related Exceptions
class ModelException(AIStudioException):
    """Base exception for model-related errors"""
    pass


class ModelNotLoadedException(ModelException):
    """Model is not loaded or available"""
    
    def __init__(self, model_name: str = "unknown", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Model '{model_name}' is not loaded or available",
            error_code="MODEL_NOT_LOADED",
            status_code=503,
            details=details or {"model_name": model_name}
        )


class ModelLoadingException(ModelException):
    """Error occurred while loading model"""
    
    def __init__(self, model_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to load model '{model_name}': {reason}",
            error_code="MODEL_LOADING_FAILED",
            status_code=503,
            details=details or {"model_name": model_name, "reason": reason}
        )


class ModelInferenceException(ModelException):
    """Error during model inference"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Model inference failed: {message}",
            error_code="MODEL_INFERENCE_FAILED",
            status_code=500,
            details=details
        )


# Code Execution Exceptions
class CodeExecutionException(AIStudioException):
    """Base exception for code execution errors"""
    pass


class CodeSecurityException(CodeExecutionException):
    """Code contains security violations"""
    
    def __init__(self, violations: List[str], details: Optional[Dict[str, Any]] = None):
        violation_text = "; ".join(violations)
        super().__init__(
            message=f"Code security violations detected: {violation_text}",
            error_code="CODE_SECURITY_VIOLATION",
            status_code=400,
            details=details or {"violations": violations}
        )


class CodeTimeoutException(CodeExecutionException):
    """Code execution timed out"""
    
    def __init__(self, timeout_seconds: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Code execution timed out after {timeout_seconds} seconds",
            error_code="CODE_EXECUTION_TIMEOUT",
            status_code=408,
            details=details or {"timeout_seconds": timeout_seconds}
        )


class UnsupportedLanguageException(CodeExecutionException):
    """Programming language not supported"""
    
    def __init__(self, language: str, supported_languages: List[str], details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Language '{language}' not supported. Supported languages: {', '.join(supported_languages)}",
            error_code="UNSUPPORTED_LANGUAGE",
            status_code=400,
            details=details or {"language": language, "supported": supported_languages}
        )


# File & Upload Exceptions
class FileException(AIStudioException):
    """Base exception for file-related errors"""
    pass


class FileSizeException(FileException):
    """File size exceeds limits"""
    
    def __init__(self, actual_size_mb: float, max_size_mb: int, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"File size ({actual_size_mb:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)",
            error_code="FILE_SIZE_EXCEEDED",
            status_code=413,
            details=details or {"actual_size_mb": actual_size_mb, "max_size_mb": max_size_mb}
        )


class UnsupportedFileTypeException(FileException):
    """File type not supported"""
    
    def __init__(self, file_type: str, supported_types: List[str], details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"File type '{file_type}' not supported. Supported types: {', '.join(supported_types)}",
            error_code="UNSUPPORTED_FILE_TYPE",
            status_code=400,
            details=details or {"file_type": file_type, "supported": supported_types}
        )


class FileProcessingException(FileException):
    """Error processing uploaded file"""
    
    def __init__(self, filename: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to process file '{filename}': {reason}",
            error_code="FILE_PROCESSING_FAILED",
            status_code=422,
            details=details or {"filename": filename, "reason": reason}
        )


# RAG & Document Exceptions
class RAGException(AIStudioException):
    """Base exception for RAG-related errors"""
    pass


class DocumentIndexingException(RAGException):
    """Error indexing document for RAG"""
    
    def __init__(self, document_id: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to index document '{document_id}': {reason}",
            error_code="DOCUMENT_INDEXING_FAILED",
            status_code=422,
            details=details or {"document_id": document_id, "reason": reason}
        )


class DocumentRetrievalException(RAGException):
    """Error retrieving documents"""
    
    def __init__(self, query: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Failed to retrieve documents for query '{query[:50]}...': {reason}",
            error_code="DOCUMENT_RETRIEVAL_FAILED",
            status_code=500,
            details=details or {"query": query, "reason": reason}
        )


# Voice Processing Exceptions
class VoiceProcessingException(AIStudioException):
    """Base exception for voice processing errors"""
    pass


class AudioTranscriptionException(VoiceProcessingException):
    """Error during audio transcription"""
    
    def __init__(self, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Audio transcription failed: {reason}",
            error_code="AUDIO_TRANSCRIPTION_FAILED",
            status_code=422,
            details=details or {"reason": reason}
        )


class UnsupportedAudioFormatException(VoiceProcessingException):
    """Audio format not supported"""
    
    def __init__(self, format_type: str, supported_formats: List[str], details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Audio format '{format_type}' not supported. Supported formats: {', '.join(supported_formats)}",
            error_code="UNSUPPORTED_AUDIO_FORMAT",
            status_code=400,
            details=details or {"format": format_type, "supported": supported_formats}
        )


# Image Processing Exceptions
class ImageProcessingException(AIStudioException):
    """Base exception for image processing errors"""
    pass


class ImageGenerationException(ImageProcessingException):
    """Error during image generation"""
    
    def __init__(self, prompt: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Image generation failed for prompt '{prompt[:50]}...': {reason}",
            error_code="IMAGE_GENERATION_FAILED",
            status_code=500,
            details=details or {"prompt": prompt, "reason": reason}
        )


# Rate Limiting & Security Exceptions
class RateLimitException(AIStudioException):
    """Rate limit exceeded"""
    
    def __init__(self, limit: int, window_seconds: int, reset_time: float, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Rate limit exceeded ({limit} requests per {window_seconds}s). Reset in {int(reset_time)} seconds",
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details or {
                "limit": limit,
                "window_seconds": window_seconds,
                "reset_time": reset_time
            }
        )


class AuthenticationException(AIStudioException):
    """Authentication failed"""
    
    def __init__(self, reason: str = "Invalid credentials", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Authentication failed: {reason}",
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details or {"reason": reason}
        )


class AuthorizationException(AIStudioException):
    """Authorization failed"""
    
    def __init__(self, resource: str = "resource", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Access denied to {resource}",
            error_code="ACCESS_DENIED",
            status_code=403,
            details=details or {"resource": resource}
        )


# Validation Exceptions
class ValidationException(AIStudioException):
    """Input validation failed"""
    
    def __init__(self, field: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Validation failed for '{field}': {reason}",
            error_code="VALIDATION_FAILED",
            status_code=400,
            details=details or {"field": field, "reason": reason}
        )


class ConfigurationException(AIStudioException):
    """Configuration error"""
    
    def __init__(self, setting: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Configuration error for '{setting}': {reason}",
            error_code="CONFIGURATION_ERROR",
            status_code=500,
            details=details or {"setting": setting, "reason": reason}
        )


# Service Unavailable Exceptions
class ServiceUnavailableException(AIStudioException):
    """Service temporarily unavailable"""
    
    def __init__(self, service_name: str, reason: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"Service '{service_name}' is temporarily unavailable: {reason}",
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details or {"service": service_name, "reason": reason}
        )


# Exception Handlers
async def ai_studio_exception_handler(request: Request, exc: AIStudioException) -> JSONResponse:
    """Handler for AI Studio custom exceptions"""
    
    # Log the exception
    logger.error(
        f"AIStudioException: {exc.error_code} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for general exceptions"""
    
    # Log the full traceback
    logger.error(
        f"Unhandled exception: {type(exc).__name__}: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown",
            "traceback": traceback.format_exc()
        }
    )
    
    # Return generic error response
    error_response = {
        "error": True,
        "error_code": "INTERNAL_SERVER_ERROR",
        "message": "An internal server error occurred",
        "status_code": 500,
        "details": {"type": type(exc).__name__} if not isinstance(exc, HTTPException) else {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return JSONResponse(
        status_code=500,
        content=error_response
    )


async def http_exception_handler_custom(request: Request, exc: HTTPException) -> JSONResponse:
    """Custom handler for HTTP exceptions"""
    
    # Use the default FastAPI handler but add consistent format
    response = await http_exception_handler(request, exc)
    
    # Convert to our standard format
    error_response = {
        "error": True,
        "error_code": f"HTTP_{exc.status_code}",
        "message": exc.detail,
        "status_code": exc.status_code,
        "details": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for Pydantic validation exceptions"""
    
    logger.warning(
        f"Validation error: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": type(exc).__name__
        }
    )
    
    error_response = {
        "error": True,
        "error_code": "VALIDATION_ERROR",
        "message": "Request validation failed",
        "status_code": 422,
        "details": {"validation_errors": str(exc)},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return JSONResponse(
        status_code=422,
        content=error_response
    )


# Utility functions for raising exceptions
def raise_model_not_loaded(model_name: str = "unknown"):
    """Convenience function to raise ModelNotLoadedException"""
    raise ModelNotLoadedException(model_name)


def raise_file_too_large(actual_size_mb: float, max_size_mb: int):
    """Convenience function to raise FileSizeException"""
    raise FileSizeException(actual_size_mb, max_size_mb)


def raise_unsupported_language(language: str, supported: List[str]):
    """Convenience function to raise UnsupportedLanguageException"""
    raise UnsupportedLanguageException(language, supported)


def raise_rate_limit_exceeded(limit: int, window_seconds: int, reset_time: float):
    """Convenience function to raise RateLimitException"""
    raise RateLimitException(limit, window_seconds, reset_time)


# Error response builders
def build_error_response(
    message: str,
    error_code: str = "ERROR",
    status_code: int = 500,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build standardized error response"""
    return {
        "error": True,
        "error_code": error_code,
        "message": message,
        "status_code": status_code,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat()
    }


def build_success_response(
    data: Any,
    message: str = "Success",
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Build standardized success response"""
    response = {
        "error": False,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if metadata:
        response["metadata"] = metadata
    
    return response


# Export all exceptions and handlers
__all__ = [
    # Base exceptions
    "AIStudioException",
    
    # Model exceptions
    "ModelException",
    "ModelNotLoadedException",
    "ModelLoadingException", 
    "ModelInferenceException",
    
    # Code execution exceptions
    "CodeExecutionException",
    "CodeSecurityException",
    "CodeTimeoutException",
    "UnsupportedLanguageException",
    
    # File exceptions
    "FileException",
    "FileSizeException",
    "UnsupportedFileTypeException",
    "FileProcessingException",
    
    # RAG exceptions
    "RAGException",
    "DocumentIndexingException",
    "DocumentRetrievalException",
    
    # Voice processing exceptions
    "VoiceProcessingException",
    "AudioTranscriptionException",
    "UnsupportedAudioFormatException",
    
    # Image processing exceptions
    "ImageProcessingException",
    "ImageGenerationException",
    
    # Security exceptions
    "RateLimitException",
    "AuthenticationException",
    "AuthorizationException",
    
    # Validation exceptions
    "ValidationException",
    "ConfigurationException",
    "ServiceUnavailableException",
    
    # Exception handlers
    "ai_studio_exception_handler",
    "general_exception_handler",
    "http_exception_handler_custom",
    "validation_exception_handler",
    
    # Utility functions
    "raise_model_not_loaded",
    "raise_file_too_large",
    "raise_unsupported_language", 
    "raise_rate_limit_exceeded",
    "build_error_response",
    "build_success_response"
]