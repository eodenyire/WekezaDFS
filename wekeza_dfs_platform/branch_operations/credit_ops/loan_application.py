import streamlit as st
from datetime import datetime

from .common import validate_customer_id, validate_amount, format_currency, show_receipt
from .services.api_client import post_request
from .services.permissions import requires_supervisor_approval, can_perform_action

# -----------------------------------------------------------------------------
# UI RENDER FUNCTION
# -----------------------------------------------------------------------------
def render_loan_application_ui(officer: dict):
    """
    Render the Loan Application UI tab.
    """

    st.subheader("📝 New Loan Application")

    # --- CUSTOMER DETAILS ---
    st.markdown("**Customer Details**")
    customer_id = st.text_input("Customer National ID", placeholder="e.g., 12345678")
    account_no = st.text_input("Customer Account Number", placeholder="e.g., 00123456789")
    
    # --- LOAN DETAILS ---
    st.markdown("**Loan Details**")
    loan_amount = st.number_input("Loan Amount (KES)", min_value=1000.0, step=1000.0, format="%.2f")
    tenure = st.number_input("Tenure (Months)", min_value=1, step=1)
    purpose = st.text_input("Loan Purpose / Notes", value="General Business")

    # SUBMIT BUTTON
    if st.button("Submit Loan Application"):
        # --- VALIDATIONS ---
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            st.stop()

        if not validate_amount(loan_amount):
            st.error("Loan amount must be greater than zero")
            st.stop()

        if tenure <= 0:
            st.error("Tenure must be at least 1 month")
            st.stop()

        # --- CHECK PERMISSIONS ---
        if not can_perform_action(officer["role"], "loan_application"):
            st.error("You are not authorized to submit loan applications")
            st.stop()

        # --- MAKER-CHECKER / SUPERVISOR APPROVAL ---
        if requires_supervisor_approval(officer["officer_id"], loan_amount):
            st.warning("⚠ This loan requires supervisor approval before processing")

        # --- PREPARE PAYLOAD ---
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "customer_id": customer_id,
            "account_no": account_no,
            "loan_amount": loan_amount,
            "tenure_months": tenure,
            "purpose": purpose,
            "application_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # --- CALL BACKEND API ---
        try:
            with st.spinner("Submitting loan application..."):
                response = post_request("/credit/loan-application", payload)
                st.success("✅ Loan Application Submitted Successfully!")

                # --- SHOW RECEIPT ---
                receipt_data = {
                    "Date": payload["application_date"],
                    "Officer": officer["officer_id"],
                    "Branch": officer["branch_code"],
                    "Customer": customer_id,
                    "Account": account_no,
                    "Loan Amount": format_currency(loan_amount),
                    "Tenure (Months)": tenure,
                    "Purpose": purpose,
                    "Application Ref": response.get("application_ref", "N/A")
                }
                show_receipt("Loan Application Receipt", receipt_data)

        except Exception as e:
            st.error(f"Failed to submit loan application: {e}")
