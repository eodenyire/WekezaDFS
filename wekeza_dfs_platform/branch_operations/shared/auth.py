# shared/auth.py

import os
import jwt
from datetime import datetime, timedelta

# --- CONFIGURATION ---
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "supersecretkey")  # In production, use env variable
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 60  # 1 hour token validity


# --- AUTH HELPERS ---
def generate_token(user_id, role, branch_code):
    """
    Generate a JWT token for a user session.
    
    Args:
        user_id (str): Unique user identifier
        role (str): User role (e.g., teller, officer, manager)
        branch_code (str): Branch code
    Returns:
        str: JWT token
    """
    payload = {
        "user_id": user_id,
        "role": role,
        "branch_code": branch_code,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token):
    """
    Decode and validate a JWT token.
    
    Args:
        token (str): JWT token
    Returns:
        dict: Payload containing user_id, role, branch_code, etc.
    Raises:
        jwt.ExpiredSignatureError: Token expired
        jwt.InvalidTokenError: Token invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")


def login(user_id, role, branch_code):
    """
    Simulate login and return a session token.
    
    Args:
        user_id (str)
        role (str)
        branch_code (str)
    Returns:
        str: JWT token
    """
    # In production, verify credentials against database or auth service
    token = generate_token(user_id, role, branch_code)
    return token


def validate_session(token, required_roles=None):
    """
    Validate user session and optionally check role permissions.
    
    Args:
        token (str): JWT token
        required_roles (list, optional): List of allowed roles
    Returns:
        dict: Payload if valid
    Raises:
        ValueError: Invalid or expired token, or unauthorized role
    """
    payload = decode_token(token)
    if required_roles and payload["role"] not in required_roles:
        raise ValueError("Unauthorized role for this operation")
    return payload
