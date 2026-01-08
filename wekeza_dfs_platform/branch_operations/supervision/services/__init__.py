# services/__init__.py

"""
Services Package
----------------
This package contains modules that provide backend integration and
role-based permission utilities for the banking DFS system.

Modules:
- api_client: Centralized API client for GET, POST, PUT, DELETE requests
- permissions: Role-based access control and permission checks

Usage:
    # Direct imports from services package
    from services import api_client, permissions
    response = api_client.get_request("http://127.0.0.1:8000/some-endpoint")
    if permissions.can_approve_transaction("BranchSupervisor"):
        print("Authorized!")

Version:
    1.0.0
"""

# Mark version
__version__ = "1.0.0"

# Optional: expose modules at package level
from . import api_client
from . import permissions

# Optional: define __all__ for explicit exports
__all__ = ["api_client", "permissions"]
