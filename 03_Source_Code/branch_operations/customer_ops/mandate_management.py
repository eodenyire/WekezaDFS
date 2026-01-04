import streamlit as st
from datetime import datetime
from .services.api_client import post_request, put_request
from .services.permissions import can_perform_action
from .common import validate_account_number, validate_customer_id, show_receipt

# -----------------------------------------------------------------------------
# Render Mandate Management UI
# -----------------------------------------------------------------------------
def render_mandate_ui(officer: dict):
    """
    Streamlit UI for managing account mandates and authorized signatories
    """
    st.subheader("✍️ Mandate Management")

    # Role-based access check
    if not can_perform_action(officer["role"], "mandate_management"):
        st.error("Access Denied: You are not authorized to manage mandates.")
        return

    # -----------------------------
    # Action Selection
    # -----------------------------
    action = st.radio("Select Action", ["Add Signatory", "Remove Signatory", "Update Signatory"])

    with st.form(key="mandate_form"):
        customer_id = st.text_input("Customer National ID / CIF")
        account_no = st.text_input("Account Number")
        signatory_name = st.text_input("Signatory Full Name")
        signatory_id = st.text_input("Signatory ID Number")
        submit_btn = st.form_submit_button(f"{action}")

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
        if not signatory_name.strip():
            st.error("Signatory name is required")
            return
        if not signatory_id.strip():
            st.error("Signatory ID is required")
            return

        # Prepare payload
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "customer_id": customer_id,
            "account_no": account_no,
            "signatory_name": signatory_name.strip(),
            "signatory_id": signatory_id.strip(),
            "action": action,
            "updated_at": datetime.now().isoformat()
        }

        # -----------------------------
        # Call Backend API
        # -----------------------------
        with st.spinner(f"{action} in progress..."):
            try:
                if action == "Add Signatory":
                    response = post_request("/customer/mandate", payload)
                else:
                    response = put_request("/customer/mandate", payload)

                # Show success receipt
                show_receipt(
                    f"✅ {action} Successful",
                    {
                        "Customer ID": customer_id,
                        "Account Number": account_no,
                        "Signatory": signatory_name,
                        "Signatory ID": signatory_id,
                        "Branch": officer["branch_code"],
                        "Performed By": officer["officer_id"],
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            except Exception as e:
                st.error(f"❌ Failed to {action.lower()}: {e}")
