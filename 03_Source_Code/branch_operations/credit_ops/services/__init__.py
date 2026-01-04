# credit_ops/services/__init__.py
# Marks the services folder as a Python package for imports
# Can be left empty or include shared package-level exports if needed

# Example: exposing api_client directly at package level
from .api_client import get_request, post_request, put_request, delete_request

__all__ = ["get_request", "post_request", "put_request", "delete_request"]
