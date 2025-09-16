#!/usr/bin/env python3
"""Test script for security utilities"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Backend'))

from app.core.security import create_access_token, verify_token, get_current_user
from app.core.config import settings

def test_jwt_functions():
    """Test JWT token creation and verification"""
    print("Testing JWT functions...")

    # Test data
    test_data = {"user_id": "test_user", "sub": "test_user"}

    # Create token
    try:
        token = create_access_token(test_data)
        print(f"✓ Token created: {token[:50]}...")
    except Exception as e:
        print(f"✗ Token creation failed: {e}")
        return False

    # Verify token
    try:
        payload = verify_token(token)
        print(f"✓ Token verified: {payload}")
        if payload.get("sub") != "test_user":
            print("✗ Token payload incorrect")
            return False
    except Exception as e:
        print(f"✗ Token verification failed: {e}")
        return False

    print("✓ JWT functions working correctly")
    return True

def test_authentication():
    """Test authentication flow"""
    print("\nTesting authentication...")

    # This would require a mock request, but for now just test the functions exist
    try:
        from app.core.security import AuthenticationError
        print("✓ AuthenticationError class available")
    except ImportError:
        print("✗ AuthenticationError not available")
        return False

    print("✓ Authentication utilities available")
    return True

if __name__ == "__main__":
    print("Running critical-path tests for security.py...")

    success = True
    success &= test_jwt_functions()
    success &= test_authentication()

    if success:
        print("\n✓ All critical-path tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
