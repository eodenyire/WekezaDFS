# supervision/__init__.py

"""
Supervision Module Package
-------------------------
This package contains all branch supervision operations including:
- Authorization queue management
- Transaction approvals
- Reversals
- Exception handling

Modules:
- app
- authorization_queue
- transaction_approvals
- reversals
- exception_handling
- common
- services.api_client
- services.permissions
"""

# Import the main render function
from .app import render_supervision_ui

# Optional: expose commonly used functions or classes
from .common import get_supervisor_info, validate_transaction_id, show_approval_receipt
from .authorization_queue import render_queue_ui
from .transaction_approvals import render_approvals_ui
from .reversals import render_reversals_ui
from .exception_handling import render_exceptions_ui
