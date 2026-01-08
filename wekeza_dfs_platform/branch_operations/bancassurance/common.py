# bancassurance/common.py

import streamlit as st
from datetime import datetime

# --- SESSION / OFFICER HELPERS ---
def get_bancassurance_officer_info(officer_id, branch_code):
    """
    Retrieve officer session information.
    In production, this would be fetched from a secure session store or backend.
    
    Args:
        officer_id (str): Officer identifier
        branch_code (str): Branch code
    
    Returns:
        dict: Officer information (id, name, role, branch_code)
    """
    # Mock data for demonstration
    return {
        "officer_id": officer_id,
        "name": f"Officer {officer_id}",
        "role": "bancassurance_officer",  # Could be 'manager', 'supervisor', etc.
        "branch_code": branch_code
    }


# --- VALIDATORS ---
def validate_customer_id(customer_id):
    """
    Validate a customer ID / CIF.
    Args:
        customer_id (str)
    Returns:
        bool
    """
    return customer_id.isdigit() and len(customer_id) in (7, 8, 9)


def validate_policy_number(policy_number):
    """
    Validate policy number format.
    Args:
        policy_number (str)
    Returns:
        bool
    """
    return isinstance(policy_number, str) and policy_number.startswith("POL") and len(policy_number) >= 8


def validate_amount(amount):
    """
    Validate monetary amount.
    Args:
        amount (float)
    Returns:
        bool
    """
    return isinstance(amount, (int, float)) and amount > 0


# --- FORMATTERS ---
def format_currency(amount):
    """
    Format numeric value as KES currency.
    Args:
        amount (float)
    Returns:
        str
    """
    return f"KES {amount:,.2f}"


def format_date(date_obj):
    """
    Format datetime object to readable string.
    Args:
        date_obj (datetime or str)
    Returns:
        str
    """
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj)
        except ValueError:
            return date_obj
    return date_obj.strftime("%d-%b-%Y %H:%M:%S")


# --- PERMISSIONS ---
def check_permissions(role, operation):
    """
    Check if a role has permission for a specific operation.
    
    Args:
        role (str): User role
        operation (str): Operation to check
    
    Returns:
        bool: True if permission granted, False otherwise
    """
    # Define role permissions
    permissions = {
        "bancassurance_officer": ["policy_sales", "premium_collection", "claims_tracking"],
        "supervisor": ["policy_sales", "premium_collection", "claims_tracking", "reports"],
        "branch_manager": ["policy_sales", "premium_collection", "claims_tracking", "reports"],
        "admin": ["policy_sales", "premium_collection", "claims_tracking", "reports"]
    }
    
    return operation in permissions.get(role, [])


# --- UI HELPERS ---
def show_receipt(title, data):
    """
    Display a structured digital receipt in Streamlit.
    
    Args:
        title (str): Receipt title
        data (dict): Receipt content
    """
    st.markdown(f"### 🧾 {title}")
    receipt_lines = []
    
    for key, value in data.items():
        if isinstance(value, float):
            value = format_currency(value)
        receipt_lines.append(f"**{key.replace('_', ' ').title()}:** {value}")
    
    st.markdown("\n".join(receipt_lines))
    st.success("✅ Transaction / Operation recorded successfully!")
