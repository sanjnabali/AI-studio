from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import logging

from ...models.user import (
    User, UserCreate, UserLogin, Token, TokenData, RefreshTokenRequest,
    users_db, email_to_id
)
from ...core.security import (
    verify_password, get_password_hash, create_access_token,
    verify_token, generate_secure_token
)
from ...core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Helper functions
def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email"""
    user_id = email_to_id.get(email.lower())
    if user_id:
        return users_db.get(user_id)
    return None

def get_user_by_id(user_id: str) -> Optional[User]:
    """Get user by ID"""
    return users_db.get(user_id)

def create_user(user_data: UserCreate) -> User:
    """Create a new user"""
    # Check if email already exists
    if get_user_by_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        hashed_password=get_password_hash(user_data.password)
    )

    # Store user
    users_db[user.id] = user
    email_to_id[user.email] = user.id

    logger.info(f"User created: {user.email}")
    return user

def authenticate_user(email: str, password: str) -> Optional[User]:
    """Authenticate user credentials"""
    user = get_user_by_email(email)
    if not user:
        logger.warning(f"Authentication failed: user not found for email {email}")
        return None
    if not verify_password(password, user.hashed_password):
        logger.warning(f"Authentication failed: incorrect password for user {email}")
        return None
    return user

def create_token_response(user: User) -> Token:
    """Create access and refresh tokens for user"""
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_data = {
        "sub": user.id,
        "email": user.email,
        "type": "access"
    }
    access_token = create_access_token(
        data=access_token_data,
        expires_delta=access_token_expires
    )

    # Create refresh token (longer expiry)
    refresh_token_expires = timedelta(days=7)  # 7 days
    refresh_token_data = {
        "sub": user.id,
        "email": user.email,
        "type": "refresh"
    }
    refresh_token = create_access_token(
        data=refresh_token_data,
        expires_delta=refresh_token_expires
    )

    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(credentials.credentials)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise credentials_exception

        user = get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise credentials_exception

        return user
    except Exception:
        raise credentials_exception

# Auth endpoints
@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        user = create_user(user_data)
        token_response = create_token_response(user)

        return {
            "access_token": token_response.access_token,
            "refresh_token": token_response.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Authenticate user and return tokens"""
    try:
        user = authenticate_user(user_data.email, user_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_response = create_token_response(user)

        return {
            "access_token": token_response.access_token,
            "refresh_token": token_response.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = verify_token(request.refresh_token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = get_user_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Create new tokens
        token_response = create_token_response(user)

        return {
            "access_token": token_response.access_token,
            "refresh_token": token_response.refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    # In a stateless JWT system, logout is handled client-side
    # In production, you might want to implement token blacklisting
    return {"message": "Successfully logged out"}

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return {
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "is_active": current_user.is_active,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
    }
