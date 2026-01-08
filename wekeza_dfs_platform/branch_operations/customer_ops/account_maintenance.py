import streamlit as st
from datetime import datetime
from .services.api_client import put_request
from .services.permissions import can_perform_action
from .common import validate_account_number, validate_customer_id, show_receipt

# -----------------------------------------------------------------------------
# Render Account Maintenance UI
# -----------------------------------------------------------------------------
def render_account_maintenance_ui(officer: dict):
    """
    Streamlit UI for updating customer or account details
    """
    st.subheader("🔧 Account Maintenance")

    # Role-based access check
    if not can_perform_action(officer["role"], "account_maintenance"):
        st.error("Access Denied: You are not authorized to maintain accounts.")
        return

    # -----------------------------
    # Account Update Form
    # -----------------------------
    with st.form(key="account_maintenance_form"):
        customer_id = st.text_input("Customer National ID / CIF")
        account_no = st.text_input("Account Number")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        address = st.text_area("Residential Address")
        submit_btn = st.form_submit_button("Update Account")

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
        if not (phone.strip() or email.strip() or address.strip()):
            st.error("At least one field (Phone, Email, Address) must be updated")
            return

        # Prepare payload
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "customer_id": customer_id,
            "account_no": account_no,
            "phone": phone.strip(),
            "email": email.strip(),
            "address": address.strip(),
            "updated_at": datetime.now().isoformat()
        }

        # -----------------------------
        # Call Backend API
        # -----------------------------
        with st.spinner("Updating Account..."):
            try:
                response = put_request("/customer/account-update", payload)
                # Show success receipt
                show_receipt(
                    "✅ Account Update Successful",
                    {
                        "Customer ID": customer_id,
                        "Account Number": account_no,
                        "Updated By": officer["officer_id"],
                        "Branch": officer["branch_code"],
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            except Exception as e:
                st.error(f"❌ Failed to update account: {e}")
