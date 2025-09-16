"""
API router configuration
"""

from fastapi import APIRouter
from .endpoints import auth_new as auth

# Create main API router
api_router = APIRouter()

# Include auth endpoints
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

# Export the main router
__all__ = ["api_router"]
