# ---------------------------------------------------------------------------
# customer_ops/services/__init__.py
# ---------------------------------------------------------------------------
# This file marks the "services" folder as a Python package for customer_ops.
# It also exposes key functions for easy import in modules.
# ---------------------------------------------------------------------------

from .api_client import get_request, post_request, put_request
from .permissions import can_perform_action

__all__ = [
    "get_request",
    "post_request",
    "put_request",
    "can_perform_action"
]

# Optional: you can add package-level constants or config here if needed
