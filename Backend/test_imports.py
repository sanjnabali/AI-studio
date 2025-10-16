#!/usr/bin/env python3

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.models.user import User
    print("User model import successful")
except ImportError as e:
    print(f"User model import failed: {e}")

try:
    from app.core.security import verify_password
    print("Security module import successful")
except ImportError as e:
    print(f"Security module import failed: {e}")

try:
    from app.core.config import settings
    print("Config module import successful")
except ImportError as e:
    print(f"Config module import failed: {e}")

try:
    from app.api.endpoints.auth import router
    print("Auth router import successful")
except ImportError as e:
    print(f"Auth router import failed: {e}")

try:
    # The package exports "api_router" from app.api.__init__.py
    from app.api import api_router
    print("API router import successful")
except ImportError as e:
    print(f"API router import failed: {e}")

try:
    from app.main import app
    print("Main app import successful")
except ImportError as e:
    print(f"Main app import failed: {e}")
