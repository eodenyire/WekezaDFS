# supervision/common.py
import streamlit as st
from datetime import datetime
import re

# -----------------------------
# Supervisor Session Utilities
# -----------------------------
def get_supervisor_info(supervisor_id: str, branch_code: str) -> dict:
    """
    Simulate fetching supervisor information from backend.
    In production, this would call a GET /supervisors API.

    Args:
        supervisor_id (str): Supervisor ID
        branch_code (str): Branch code

    Returns:
        dict: Supervisor info
    """
    # For MVP, return dummy data
    return {
        "supervisor_id": supervisor_id,
        "name": f"Supervisor {supervisor_id[-3:]}",
        "role": "BranchSupervisor",  # Could also be 'BranchManager'
        "branch_code": branch_code
    }

# -----------------------------
# Validators
# -----------------------------
def validate_transaction_id(tx_id: str) -> bool:
    """
    Validate transaction ID format.
    Example format: TXN-123456

    Args:
        tx_id (str): Transaction ID

    Returns:
        bool: True if valid, False otherwise
    """
    if not tx_id:
        return False
    pattern = r"^TXN-\d{6,}$"
    return re.match(pattern, tx_id) is not None

def validate_amount(amount: float) -> bool:
    """
    Validate transaction amount.

    Args:
        amount (float): Transaction amount

    Returns:
        bool: True if valid (positive), False otherwise
    """
    return amount > 0

# -----------------------------
# Formatting Helpers
# -----------------------------
def format_currency(amount: float) -> str:
    """
    Format amount as Kenyan Shillings currency.

    Args:
        amount (float): Amount

    Returns:
        str: Formatted string
    """
    return f"{amount:,.2f}"

def format_date(date_str: str) -> str:
    """
    Format date string to readable format.
    Expects ISO format 'YYYY-MM-DDTHH:MM:SS'

    Args:
        date_str (str): Date string

    Returns:
        str: Formatted date
    """
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d-%b-%Y %H:%M:%S")
    except Exception:
        return date_str

# -----------------------------
# UI Helpers
# -----------------------------
def show_approval_receipt(title: str, data: dict):
    """
    Display a digital receipt for approvals, reversals, or exception resolutions.

    Args:
        title (str): Receipt title
        data (dict): Data to display (transaction_id, supervisor_id, timestamp, etc.)
    """
    st.markdown(f"### 🧾 {title}")
    st.code(
        f"""
Transaction ID: {data.get('transaction_id', '-')}

Supervisor ID: {data.get('supervisor_id', '-')}
Branch: {data.get('branch_code', '-')}

Action: {data.get('action', data.get('resolution', '-'))}
Amount: KES {format_currency(data.get('amount', 0))}
Customer ID: {data.get('customer_id', '-')}

Timestamp: {format_date(data.get('timestamp', datetime.now().isoformat()))}
Remarks: {data.get('remarks', '-')}
        """,
        language="text"
    )

# -----------------------------
# Session / Misc Helpers
# -----------------------------
def display_error(message: str):
    """
    Standardized error display in Streamlit
    """
    st.error(f"❌ {message}")

def display_success(message: str):
    """
    Standardized success display in Streamlit
    """
    st.success(f"✅ {message}")
