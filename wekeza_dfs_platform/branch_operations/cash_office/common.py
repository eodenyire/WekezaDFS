import streamlit as st
from datetime import datetime

# --- Officer Info Retrieval ---
def get_cash_officer_info(officer_id, branch_code):
    """
    Returns a dictionary with officer information.
    In production, this could query a backend or session store.
    """
    return {
        "officer_id": officer_id,
        "branch_code": branch_code,
        "login_time": datetime.now().isoformat()
    }


# --- Amount Validation ---
def validate_amount(amount):
    """
    Ensures the cash amount is positive and properly formatted.
    """
    if amount is None or amount <= 0:
        return False
    return True


# --- Teller ID Validation ---
def validate_teller_id(teller_id):
    """
    Basic validation for teller ID format: e.g., TEL-001
    """
    if not teller_id or not teller_id.startswith("TEL-"):
        return False
    return True


# --- Cash Receipt Generator ---
def show_cash_receipt(title, data_dict):
    """
    Displays a formatted digital cash receipt.
    `data_dict` is a dictionary of key-value pairs to display.
    """
    st.markdown(f"### 🧾 {title}")
    receipt_text = "\n".join([f"{key}: {value}" for key, value in data_dict.items()])
    st.code(receipt_text, language="text")
