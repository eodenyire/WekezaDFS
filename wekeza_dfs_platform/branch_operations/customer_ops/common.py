import streamlit as st
import re

# -----------------------------------------------------------------------------
# Validators
# -----------------------------------------------------------------------------
def validate_customer_id(customer_id: str) -> bool:
    """
    Validate a Kenyan National ID (or CIF)
    - Must be numeric, typically 7-8 digits
    """
    if not customer_id:
        return False
    return bool(re.fullmatch(r"\d{7,8}", customer_id.strip()))

def validate_account_number(account_no: str) -> bool:
    """
    Validate an account number
    - Must be numeric, typically 10-12 digits
    """
    if not account_no:
        return False
    return bool(re.fullmatch(r"\d{10,12}", account_no.strip()))

def validate_amount(amount) -> bool:
    """
    Validate numeric amount (positive)
    """
    try:
        return float(amount) > 0
    except:
        return False

# -----------------------------------------------------------------------------
# UI Helpers
# -----------------------------------------------------------------------------
def show_receipt(title: str, data: dict):
    """
    Display a digital receipt in a structured code block
    """
    st.markdown(f"### 🧾 {title}")
    receipt_text = "\n".join([f"{k}: {v}" for k, v in data.items()])
    st.code(receipt_text, language="text")

def format_currency(amount: float, currency: str = "KES") -> str:
    """
    Format a numeric amount as currency
    """
    return f"{currency} {amount:,.2f}"

def format_date(dt):
    """
    Format datetime object as YYYY-MM-DD
    """
    return dt.strftime("%Y-%m-%d") if dt else ""
