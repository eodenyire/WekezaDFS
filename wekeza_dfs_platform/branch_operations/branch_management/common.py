# branch_management/common.py
import re
import streamlit as st

# -----------------------------
# Session & Manager Utilities
# -----------------------------
def get_branch_manager_info(manager_id: str, branch_code: str) -> dict:
    """
    Fetch branch manager session info.
    This is a stub function – in production, it can call backend APIs.

    Args:
        manager_id (str): Manager ID
        branch_code (str): Branch code

    Returns:
        dict: Manager info including name, role, branch_code
    """
    # Stubbed info – replace with real API call in production
    return {
        "manager_id": manager_id,
        "name": f"Manager {manager_id[-3:]}",
        "role": "BranchManager",
        "branch_code": branch_code
    }


# -----------------------------
# Format Utilities
# -----------------------------
def format_currency(amount: float) -> str:
    """
    Format number as KES currency string.

    Args:
        amount (float): Numeric amount

    Returns:
        str: Formatted currency string
    """
    try:
        return f"{amount:,.2f}"
    except Exception:
        return "0.00"


def format_date(date_str: str) -> str:
    """
    Format ISO date string to human-readable format (YYYY-MM-DD).

    Args:
        date_str (str): ISO date string

    Returns:
        str: Formatted date string
    """
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return date_str


# -----------------------------
# Validation Utilities
# -----------------------------
def validate_staff_id(staff_id: str) -> bool:
    """
    Validate staff ID format (e.g., TEL-001, LOAN-002).

    Args:
        staff_id (str): Staff ID

    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^[A-Z]+-\d{3}$"
    return bool(re.match(pattern, staff_id))


def validate_transaction_id(txn_id: str) -> bool:
    """
    Validate transaction ID format (e.g., BRN-DEP-123456).

    Args:
        txn_id (str): Transaction ID

    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^[A-Z]{3}-[A-Z]{3}-\d{6}$"
    return bool(re.match(pattern, txn_id))


# -----------------------------
# UI Utilities
# -----------------------------
def show_override_receipt(title: str, data: dict):
    """
    Display a digital receipt for manager overrides.

    Args:
        title (str): Receipt title
        data (dict): Receipt data
    """
    st.markdown(f"### 🧾 {title}")
    st.code(f"""
    Manager: {data.get('manager_name', 'N/A')}
    Branch: {data.get('branch_code', 'N/A')}
    Transaction ID: {data.get('transaction_id', 'N/A')}
    Override Type: {data.get('override_type', 'N/A')}
    Reason: {data.get('reason', 'N/A')}
    Timestamp: {data.get('timestamp', 'N/A')}
    """, language="text")
