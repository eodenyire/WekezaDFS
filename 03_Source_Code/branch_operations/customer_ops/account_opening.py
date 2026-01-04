import streamlit as st
from datetime import datetime
from .services.api_client import post_request
from .services.permissions import can_perform_action
from .common import validate_account_number, validate_customer_id, validate_amount, show_receipt

# -----------------------------------------------------------------------------
# Render Account Opening UI
# -----------------------------------------------------------------------------
def render_account_opening_ui(officer: dict):
    """
    Streamlit UI for opening new bank accounts linked to a CIF
    """
    st.subheader("🏦 Account Opening")

    # Role-based access check
    if not can_perform_action(officer["role"], "account_opening"):
        st.error("Access Denied: You are not authorized to open accounts.")
        return

    # -----------------------------
    # Account Opening Form
    # -----------------------------
    with st.form(key="account_open_form"):
        customer_id = st.text_input("Customer National ID / CIF")
        account_no = st.text_input("Proposed Account Number")
        account_type = st.selectbox("Account Type", ["Savings", "Current", "Fixed Deposit"])
        initial_deposit = st.number_input("Initial Deposit (KES)", min_value=0.0, step=100.0, format="%.2f")
        submit_btn = st.form_submit_button("Open Account")

    # -----------------------------
    # Handle Form Submission
    # -----------------------------
    if submit_btn:
        # Validate inputs
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            return
        if not validate_account_number(account_no):
            st.error("Invalid Account Number")
            return
        if not validate_amount(initial_deposit):
            st.error("Initial Deposit must be positive")
            return

        # Prepare payload
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "customer_id": customer_id,
            "account_no": account_no,
            "account_type": account_type,
            "initial_deposit": initial_deposit,
            "created_at": datetime.now().isoformat()
        }

        # -----------------------------
        # Call Backend API
        # -----------------------------
        with st.spinner("Creating Account..."):
            try:
                response = post_request("/customer/account-open", payload)
                # Show success receipt
                show_receipt(
                    "✅ Account Opening Successful",
                    {
                        "Customer ID": customer_id,
                        "Account Number": account_no,
                        "Account Type": account_type,
                        "Branch": officer["branch_code"],
                        "Opened By": officer["officer_id"],
                        "Initial Deposit": f"KES {initial_deposit:,.2f}",
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            except Exception as e:
                st.error(f"❌ Failed to open account: {e}")
