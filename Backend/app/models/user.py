from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime
import uuid

class User(BaseModel):
    """User model for authentication"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @validator('email')
    def email_must_be_valid(cls, v):
        if not v or '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "name": "John Doe",
                "is_active": True,
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z"
            }
        }

class UserCreate(BaseModel):
    """User creation request model"""
    email: EmailStr
    name: str
    password: str = Field(..., min_length=6)
    confirmPassword: str

    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @validator('confirmPassword')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

class UserLogin(BaseModel):
    """User login request model"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[str] = None
    email: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    """Refresh token request model"""
    refresh_token: str

# In-memory user storage (replace with database in production)
users_db: dict[str, User] = {}
email_to_id: dict[str, str] = {}
