# Backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Any, Union, Optional
try:
    import jwt as pyjwt
    from jwt.exceptions import PyJWTError
except Exception:
    pyjwt = None
    class PyJWTError(Exception):
        """Fallback exception when PyJWT is not installed."""
        pass
from passlib.context import CryptContext
from fastapi import HTTPException, status
from config.settings import settings
import secrets
import bcrypt

# Configure password hashing with optimal settings
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,  # Industry standard for security/performance balance
    bcrypt__default_rounds=12
)

class SecurityManager:
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
        
        # Verify secret key strength
        if len(self.secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)

        to_encode.update({"exp": expire, "type": "access"})
        if pyjwt is None:
            raise RuntimeError("PyJWT is not installed. Install with `pip install PyJWT` to use token creation.")
        encoded_jwt = pyjwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        if pyjwt is None:
            raise RuntimeError("PyJWT is not installed. Install with `pip install PyJWT` to use token creation.")
        encoded_jwt = pyjwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> dict:
        try:
            if pyjwt is None:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="PyJWT is not installed on the server.")
            
            # Decode and verify token with additional checks
            payload = pyjwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                }
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check token expiration explicitly
            exp = payload.get("exp")
            if not exp or datetime.fromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired"
                )
            
            return payload
            
        except PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )
    
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_api_key(self) -> str:
        return secrets.token_urlsafe(32)

security_manager = SecurityManager()

# Backwards-compatible top-level function
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return security_manager.verify_password(plain_password, hashed_password)

# Password validation
def validate_password(password: str) -> bool:
    """
    Validate password strength
    Requirements: At least 8 characters, contains uppercase, lowercase, digit
    """
    if len(password) < 8:
        return False
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    return has_upper and has_lower and has_digit