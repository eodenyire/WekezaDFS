"""
Cash Office Services Package

This package contains helper services for the Cash Office module, including:
- Centralized API client for backend communication (`api_client.py`)
- Role-based permissions and cash limits (`permissions.py`)
"""

# Optional: Expose main service utilities at package level
from .api_client import get_request, post_request
from .permissions import requires_supervisor_approval, teller_limit_check

__all__ = [
    "get_request",
    "post_request",
    "requires_supervisor_approval",
    "teller_limit_check"
]
