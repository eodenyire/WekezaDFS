import streamlit as st

# -----------------------------------------------------------------------------
# VALIDATORS
# -----------------------------------------------------------------------------
def validate_customer_id(customer_id: str) -> bool:
    """
    Validate that a customer ID is numeric and has 5-12 digits.
    """
    if not customer_id:
        return False
    customer_id = str(customer_id).strip()
    return customer_id.isdigit() and 5 <= len(customer_id) <= 12

def validate_account_number(account_no: str) -> bool:
    """
    Validate that an account number is numeric and 8-12 digits.
    """
    if not account_no:
        return False
    account_no = str(account_no).strip()
    return account_no.isdigit() and 8 <= len(account_no) <= 12

def validate_amount(amount: float) -> bool:
    """
    Validate that a numeric amount is greater than zero.
    """
    try:
        return float(amount) > 0
    except (ValueError, TypeError):
        return False

# -----------------------------------------------------------------------------
# FORMATTERS
# -----------------------------------------------------------------------------
def format_currency(amount: float) -> str:
    """
    Format a number as KES currency.
    """
    try:
        return f"KES {amount:,.2f}"
    except Exception:
        return str(amount)

def format_date(dt) -> str:
    """
    Format a datetime object as YYYY-MM-DD HH:MM
    """
    try:
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(dt)

# -----------------------------------------------------------------------------
# RECEIPT / DISPLAY
# -----------------------------------------------------------------------------
def show_receipt(title: str, data: dict):
    """
    Display a digital receipt in Streamlit.
    """
    st.markdown(f"### 🧾 {title}")
    receipt_text = "\n".join([f"{key}: {value}" for key, value in data.items()])
    st.code(receipt_text, language="text")
