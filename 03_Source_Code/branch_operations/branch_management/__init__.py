# branch_management/__init__.py

"""
Branch Management Package
-------------------------
This package contains modules and utilities for branch-level operations 
and management within the Wekeza Bank DFS system.

Modules (examples):
- app.py                  : Main Streamlit UI entry point for branch managers
- branch_overview.py      : Dashboard and KPIs for branch operations
- staff_management.py     : Manage branch staff, roles, and assignments
- reporting.py            : Branch-level reports and analytics

Usage:
    from branch_management import app
    from branch_management import branch_overview

Version:
    1.0.0
"""

__version__ = "1.0.0"

# Optional: import key modules at package level
# from . import app
# from . import branch_overview
# from . import staff_management
# from . import reporting

# Optional: define __all__ for explicit exports
__all__ = ["app"]  # can expand as more modules are added
