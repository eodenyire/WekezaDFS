# cash_office/__init__.py

"""
Cash Office Module

This package handles all branch cash operations, including:
- Vault management
- Teller cash issue and receipt
- ATM cash loading/offloading
- Cash reconciliation

Modules included:
- app.py
- vault_open_close.py
- teller_cash_issue.py
- teller_cash_receive.py
- atm_cash_loading.py
- atm_cash_offloading.py
- cash_reconciliation.py
- common.py
- services/
"""

# Optional: Expose main UI functions at package level for easy imports
from .vault_open_close import open_vault_ui, close_vault_ui
from .teller_cash_issue import issue_cash_ui
from .teller_cash_receive import receive_cash_ui
from .atm_cash_loading import load_atm_ui
from .atm_cash_offloading import offload_atm_ui
from .cash_reconciliation import reconcile_cash_ui

__all__ = [
    "open_vault_ui",
    "close_vault_ui",
    "issue_cash_ui",
    "receive_cash_ui",
    "load_atm_ui",
    "offload_atm_ui",
    "reconcile_cash_ui"
]
