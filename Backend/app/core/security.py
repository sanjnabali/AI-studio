"""
Security utilities and middleware for AI Studio Backend
"""

import secrets
import hashlib
import hmac
import time
import re
from typing import Optional, List, Dict, Any, Set
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, Security, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
from functools import wraps
import asyncio
from collections import defaultdict, deque

from .config import settings, security_config

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token handling
security_scheme = HTTPBearer()


class SecurityError(Exception):
    """Base security exception"""
    pass


class AuthenticationError(SecurityError):
    """Authentication failed"""
    pass


class AuthorizationError(SecurityError):
    """Authorization failed"""
    pass


class RateLimitError(SecurityError):
    """Rate limit exceeded"""
    pass


class CodeSecurityError(SecurityError):
    """Code execution security violation"""
    pass


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


# JWT token utilities
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise AuthenticationError("Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security_scheme)):
    """Get current user from JWT token"""
    try:
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid token payload")
        return {"user_id": user_id, "payload": payload}
    except SecurityError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Rate limiting
class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(deque)
        self.cleanup_interval = 300  # 5 minutes
        self.last_cleanup = time.time()
    
    def _cleanup_old_requests(self):
        """Remove old request records"""
        current_time = time.time()
        if current_time - self.last_cleanup < self.cleanup_interval:
            return
        
        cutoff_time = current_time - 3600  # 1 hour ago
        for key in list(self.requests.keys()):
            request_times = self.requests[key]
            while request_times and request_times[0] < cutoff_time:
                request_times.popleft()
            
            if not request_times:
                del self.requests[key]
        
        self.last_cleanup = current_time
    
    def is_allowed(self, key: str, limit: int, window_seconds: int = 60) -> bool:
        """Check if request is allowed under rate limit"""
        self._cleanup_old_requests()
        
        current_time = time.time()
        request_times = self.requests[key]
        
        # Remove requests outside the window
        cutoff_time = current_time - window_seconds
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Check if under limit
        if len(request_times) >= limit:
            return False
        
        # Record this request
        request_times.append(current_time)
        return True
    
    def get_reset_time(self, key: str, window_seconds: int = 60) -> float:
        """Get when rate limit resets for a key"""
        request_times = self.requests.get(key, deque())
        if not request_times:
            return time.time()
        return request_times[0] + window_seconds


# Global rate limiter instance
rate_limiter = RateLimiter()


def create_rate_limit_key(request: Request, endpoint: str) -> str:
    """Create rate limit key from request"""
    # Use IP address as primary identifier
    client_ip = request.client.host if request.client else "unknown"
    
    # Add user ID if authenticated
    auth_header = request.headers.get("authorization")
    user_id = "anonymous"
    
    if auth_header and auth_header.startswith("Bearer "):
        try:
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            user_id = payload.get("sub", "anonymous")
        except:
            pass
    
    return f"{endpoint}:{client_ip}:{user_id}"


async def check_rate_limit(request: Request, endpoint: str):
    """Rate limiting middleware"""
    if not settings.FEATURES.get("rate_limiting", False):
        return
    
    limit = security_config.RATE_LIMITS.get(endpoint, 60)
    key = create_rate_limit_key(request, endpoint)
    
    if not rate_limiter.is_allowed(key, limit):
        reset_time = rate_limiter.get_reset_time(key)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {int(reset_time - time.time())} seconds",
            headers={
                "X-RateLimit-Limit": str(limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_time))
            }
        )


# Code security
class CodeSecurityValidator:
    """Validate code for security issues"""
    
    def __init__(self):
        self.dangerous_patterns = security_config.DANGEROUS_PATTERNS
        self.allowed_imports = security_config.ALLOWED_IMPORTS
    
    def validate_python_code(self, code: str) -> Dict[str, Any]:
        """Validate Python code for security issues"""
        issues = []
        warnings = []
        
        code_lower = code.lower()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if pattern in code_lower:
                issues.append(f"Dangerous pattern detected: {pattern}")
        
        # Check imports
        import_lines = [line.strip() for line in code.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
        
        for line in import_lines:
            # Extract module name
            if line.startswith('import '):
                module = line.split()[1].split('.')[0]
            elif line.startswith('from '):
                module = line.split()[1].split('.')[0]
            else:
                continue
            
            if module not in self.allowed_imports.get("python", []):
                warnings.append(f"Import may be restricted: {module}")
        
        # Check for eval/exec usage
        if re.search(r'\b(eval|exec)\s*\(', code):
            issues.append("Dynamic code execution detected (eval/exec)")
        
        # Check for file operations
        if re.search(r'\bopen\s*\(', code):
            warnings.append("File operation detected - ensure it's necessary")
        
        # Check for network operations
        network_patterns = ['urllib', 'requests', 'socket', 'http.client']
        for pattern in network_patterns:
            if pattern in code_lower:
                warnings.append(f"Network operation detected: {pattern}")
        
        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, 100 - len(issues) * 50 - len(warnings) * 10)
        }
    
    def validate_javascript_code(self, code: str) -> Dict[str, Any]:
        """Validate JavaScript code for security issues"""
        issues = []
        warnings = []
        
        code_lower = code.lower()
        
        # Check for dangerous functions
        dangerous_js = [
            'eval(', 'function(', 'settimeout', 'setinterval',
            'xmlhttprequest', 'fetch(', 'require(', 'import(',
            'document.', 'window.', 'global.', 'process.'
        ]
        
        for pattern in dangerous_js:
            if pattern in code_lower:
                if pattern in ['eval(', 'function(']:
                    issues.append(f"Dangerous JavaScript detected: {pattern}")
                else:
                    warnings.append(f"Potentially restricted operation: {pattern}")
        
        return {
            "safe": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "score": max(0, 100 - len(issues) * 50 - len(warnings) * 10)
        }
    
    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code based on language"""
        if language.lower() == "python":
            return self.validate_python_code(code)
        elif language.lower() == "javascript":
            return self.validate_javascript_code(code)
        else:
            return {
                "safe": True,
                "issues": [],
                "warnings": [f"Security validation not implemented for {language}"],
                "score": 80
            }


# Global code validator
code_validator = CodeSecurityValidator()


# Input sanitization
def sanitize_input(text: str, max_length: int = 10000) -> str:
    """Sanitize user input"""
    if not isinstance(text, str):
        raise ValueError("Input must be a string")
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def validate_file_upload(filename: str, content: bytes, allowed_extensions: List[str], max_size_mb: int = 50) -> Dict[str, Any]:
    """Validate file upload"""
    issues = []
    
    # Check filename
    if not filename:
        issues.append("Filename is required")
    elif '..' in filename or '/' in filename or '\\' in filename:
        issues.append("Invalid characters in filename")
    
    # Check extension
    if filename and not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        issues.append(f"File extension not allowed. Allowed: {allowed_extensions}")
    
    # Check size
    size_mb = len(content) / (1024 * 1024)
    if size_mb > max_size_mb:
        issues.append(f"File too large ({size_mb:.1f}MB). Max: {max_size_mb}MB")
    
    # Check for executable content (basic check)
    if content.startswith(b'MZ') or content.startswith(b'\x7fELF'):
        issues.append("Executable files not allowed")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "size_mb": size_mb
    }


# Security headers middleware
async def add_security_headers(request: Request, call_next):
    """Add security headers to responses"""
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    
    if settings.is_production():
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# Authentication decorators
def require_auth(func):
    """Decorator to require authentication"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This is a placeholder - implement actual auth check
        # For now, just pass through if authentication is disabled
        if not settings.FEATURES.get("authentication", False):
            return await func(*args, **kwargs)
        
        # Add actual authentication logic here
        return await func(*args, **kwargs)
    return wrapper


def require_rate_limit(endpoint: str):
    """Decorator for rate limiting"""
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request = None, *args, **kwargs):
            if request:
                await check_rate_limit(request, endpoint)
            return await func(*args, **kwargs)
        return wrapper
    return decorator


# Security utilities
def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify CSRF token"""
    return hmac.compare_digest(token, expected)


def hash_sensitive_data(data: str) -> str:
    """Hash sensitive data for logging"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def is_safe_redirect_url(url: str, allowed_hosts: List[str]) -> bool:
    """Check if redirect URL is safe"""
    if not url:
        return False
    
    # Reject absolute URLs to different hosts
    if url.startswith(('http://', 'https://')):
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc in allowed_hosts
    
    # Allow relative URLs
    return url.startswith('/')


# Logging security events
def log_security_event(event_type: str, details: Dict[str, Any], request: Request = None):
    """Log security events"""
    log_data = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "details": details
    }
    
    if request:
        log_data.update({
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "endpoint": request.url.path
        })
    
    logger.warning(f"Security event: {event_type}", extra=log_data)


# Export commonly used functions
__all__ = [
    "SecurityError",
    "AuthenticationError", 
    "AuthorizationError",
    "RateLimitError",
    "CodeSecurityError",
    "verify_password",
    "get_password_hash",
    "generate_secure_token",
    "create_access_token",
    "verify_token",
    "get_current_user",
    "check_rate_limit",
    "code_validator",
    "sanitize_input",
    "validate_file_upload",
    "add_security_headers",
    "require_auth",
    "require_rate_limit",
    "log_security_event",
    "rate_limiter"
]