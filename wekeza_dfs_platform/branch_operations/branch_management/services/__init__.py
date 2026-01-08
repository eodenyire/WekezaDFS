# branch_management/services/__init__.py
"""
branch_management.services
--------------------------

This package contains shared services for the branch_management module,
including backend API clients and role-based permissions.

Modules:
- api_client.py      : Centralized backend API call functions (GET, POST, etc.)
- permissions.py     : Role-based access control and branch-level authorization
"""

# Optional: Explicitly expose submodules
from . import api_client
from . import permissions

__all__ = [
    "api_client",
    "permissions"
]
