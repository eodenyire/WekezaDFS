import streamlit as st
from datetime import datetime

from .common import validate_customer_id, validate_account_number, format_currency, show_receipt
from .services.api_client import post_request
from .services.permissions import requires_supervisor_approval, can_perform_action

# -----------------------------------------------------------------------------
# UI RENDER FUNCTION
# -----------------------------------------------------------------------------
def render_disbursement_ui(officer: dict):
    """
    Render the Disbursement UI tab.
    """

    st.subheader("💸 Loan Disbursement")

    # --- CHECK PERMISSIONS ---
    if not can_perform_action(officer["role"], "disbursement"):
        st.error("You are not authorized to disburse loans")
        st.stop()

    # --- SELECT LOAN TO DISBURSE ---
    st.markdown("**Loan Details**")
    application_ref = st.text_input("Loan Application Reference", placeholder="e.g., LOAN-REF-001")
    customer_id = st.text_input("Customer National ID", placeholder="e.g., 12345678")
    account_no = st.text_input("Customer Account Number", placeholder="e.g., 00123456789")
    loan_amount = st.number_input("Loan Amount (KES)", min_value=0.0, step=100.0, format="%.2f")
    disbursement_date = st.date_input("Disbursement Date", value=datetime.today())

    # --- SUBMIT BUTTON ---
    if st.button("Disburse Loan"):
        # --- VALIDATIONS ---
        if not application_ref.strip():
            st.error("Loan Application Reference is required")
            st.stop()
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            st.stop()
        if not validate_account_number(account_no):
            st.error("Invalid Account Number")
            st.stop()
        if loan_amount <= 0:
            st.error("Loan amount must be greater than zero")
            st.stop()

        # --- MAKER-CHECKER / SUPERVISOR APPROVAL ---
        if requires_supervisor_approval(officer["officer_id"], loan_amount):
            st.warning("⚠ This disbursement requires supervisor approval before processing")

        # --- PREPARE PAYLOAD ---
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "application_ref": application_ref.strip(),
            "customer_id": customer_id.strip(),
            "account_no": account_no.strip(),
            "loan_amount": loan_amount,
            "disbursement_date": disbursement_date.strftime("%Y-%m-%d %H:%M:%S")
        }

        # --- CALL BACKEND API ---
        try:
            with st.spinner("Processing disbursement..."):
                response = post_request("/credit/disbursement", payload)
                st.success("✅ Loan Disbursed Successfully!")

                # --- SHOW RECEIPT ---
                receipt_data = {
                    "Date": payload["disbursement_date"],
                    "Officer": officer["officer_id"],
                    "Branch": officer["branch_code"],
                    "Customer": customer_id,
                    "Account": account_no,
                    "Loan Amount": format_currency(loan_amount),
                    "Application Ref": application_ref,
                    "Disbursement Ref": response.get("disbursement_ref", "N/A")
                }
                show_receipt("Loan Disbursement Receipt", receipt_data)

        except Exception as e:
            st.error(f"Failed to disburse loan: {e}")
