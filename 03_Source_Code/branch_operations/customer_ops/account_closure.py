import streamlit as st
from datetime import datetime
from .services.api_client import post_request
from .services.permissions import can_perform_action
from .common import validate_account_number, validate_customer_id, show_receipt

# -----------------------------------------------------------------------------
# Render Account Closure UI
# -----------------------------------------------------------------------------
def render_account_closure_ui(officer: dict):
    """
    Streamlit UI for closing customer accounts safely
    """
    st.subheader("❌ Account Closure")

    # Role-based access check
    if not can_perform_action(officer["role"], "account_closure"):
        st.error("Access Denied: You are not authorized to close accounts.")
        return

    # -----------------------------
    # Account Closure Form
    # -----------------------------
    with st.form(key="account_closure_form"):
        customer_id = st.text_input("Customer National ID / CIF")
        account_no = st.text_input("Account Number")
        reason = st.text_area("Reason for Closure")
        submit_btn = st.form_submit_button("Close Account")

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
        if not reason.strip():
            st.error("Closure reason is required")
            return

        # Prepare payload
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "customer_id": customer_id,
            "account_no": account_no,
            "reason": reason.strip(),
            "closed_at": datetime.now().isoformat()
        }

        # -----------------------------
        # Call Backend API
        # -----------------------------
        with st.spinner("Closing Account..."):
            try:
                response = post_request("/customer/account-close", payload)
                # Show success receipt
                show_receipt(
                    "✅ Account Closure Successful",
                    {
                        "Customer ID": customer_id,
                        "Account Number": account_no,
                        "Branch": officer["branch_code"],
                        "Closed By": officer["officer_id"],
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            except Exception as e:
                st.error(f"❌ Failed to close account: {e}")
