# bancassurance/services/__init__.py

from .api_client import get_request, post_request, put_request
from .permissions import can_sell_policy, can_collect_premium, can_manage_claims, can_view_reports

__all__ = [
    "get_request",
    "post_request",
    "put_request",
    "can_sell_policy",
    "can_collect_premium",
    "can_manage_claims",
    "can_view_reports"
]
