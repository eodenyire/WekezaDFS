# customer_ops/__init__.py

from .app import render_customer_ops_ui
from .cif_create import render_cif_ui
from .account_opening import render_account_opening_ui
from .account_maintenance import render_account_maintenance_ui
from .account_closure import render_account_closure_ui
from .mandate_management import render_mandate_ui
from .enquiries import render_enquiries_ui

__all__ = [
    "render_customer_ops_ui",
    "render_cif_ui",
    "render_account_opening_ui",
    "render_account_maintenance_ui",
    "render_account_closure_ui",
    "render_mandate_ui",
    "render_enquiries_ui"
]
