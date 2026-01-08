# bancassurance/__init__.py

from .app import render_bancassurance_ui
from .policy_sales import render_policy_sales_ui
from .premium_collection import render_premium_collection_ui
from .claims_tracking import render_claims_tracking_ui
from .reports import render_reports_ui

__all__ = [
    "render_bancassurance_ui",
    "render_policy_sales_ui",
    "render_premium_collection_ui",
    "render_claims_tracking_ui",
    "render_reports_ui",
]
