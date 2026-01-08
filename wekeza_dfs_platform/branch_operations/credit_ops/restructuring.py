import streamlit as st
from datetime import datetime

from .common import validate_customer_id, validate_amount, format_currency, show_receipt
from .services.api_client import post_request
from .services.permissions import requires_supervisor_approval, can_perform_action

# -----------------------------------------------------------------------------
# UI RENDER FUNCTION
# -----------------------------------------------------------------------------
def render_restructuring_ui(officer: dict):
    """
    Render the Loan Restructuring UI tab.
    """

    st.subheader("🔄 Loan Restructuring / Top-Up")

    # --- CHECK PERMISSIONS ---
    if not can_perform_action(officer["role"], "restructuring"):
        st.error("You are not authorized to restructure loans")
        st.stop()

    # --- LOAN DETAILS ---
    st.markdown("**Existing Loan Details**")
    application_ref = st.text_input("Loan Application Reference", placeholder="e.g., LOAN-REF-001")
    customer_id = st.text_input("Customer National ID", placeholder="e.g., 12345678")
    current_outstanding = st.number_input("Current Outstanding Amount (KES)", min_value=0.0, step=100.0, format="%.2f")

    # --- RESTRUCTURING OPTIONS ---
    st.markdown("**Restructuring Options**")
    new_tenure = st.number_input("New Tenure (Months)", min_value=1, step=1)
    top_up_amount = st.number_input("Top-Up Amount (KES)", min_value=0.0, step=100.0, format="%.2f")
    new_interest_rate = st.number_input("New Interest Rate (%)", min_value=0.0, step=0.1, format="%.2f")
    notes = st.text_area("Notes / Reason for Restructuring", value="Optional")

    # --- SUBMIT BUTTON ---
    if st.button("Submit Restructuring Request"):
        # --- VALIDATIONS ---
        if not application_ref.strip():
            st.error("Loan Application Reference is required")
            st.stop()
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            st.stop()
        if current_outstanding <= 0:
            st.error("Current outstanding amount must be greater than zero")
            st.stop()
        if new_tenure <= 0:
            st.error("New tenure must be at least 1 month")
            st.stop()
        if new_interest_rate <= 0:
            st.error("New interest rate must be greater than 0")
            st.stop()
        if top_up_amount < 0:
            st.error("Top-up amount cannot be negative")
            st.stop()

        # --- MAKER-CHECKER / SUPERVISOR APPROVAL ---
        total_amount = current_outstanding + top_up_amount
        if requires_supervisor_approval(officer["officer_id"], total_amount):
            st.warning("⚠ This restructuring requires supervisor approval before processing")

        # --- PREPARE PAYLOAD ---
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "application_ref": application_ref.strip(),
            "customer_id": customer_id.strip(),
            "current_outstanding": current_outstanding,
            "new_tenure": new_tenure,
            "top_up_amount": top_up_amount,
            "new_interest_rate": new_interest_rate,
            "notes": notes.strip(),
            "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # --- CALL BACKEND API ---
        try:
            with st.spinner("Submitting restructuring request..."):
                response = post_request("/credit/restructuring", payload)
                st.success("✅ Loan Restructuring Submitted Successfully!")

                # --- SHOW RECEIPT ---
                receipt_data = {
                    "Date": payload["request_date"],
                    "Officer": officer["officer_id"],
                    "Branch": officer["branch_code"],
                    "Customer": customer_id,
                    "Application Ref": application_ref,
                    "Current Outstanding": format_currency(current_outstanding),
                    "New Tenure": f"{new_tenure} months",
                    "Top-Up Amount": format_currency(top_up_amount),
                    "New Interest Rate": f"{new_interest_rate:.2f}%",
                    "Notes": notes,
                    "Restructuring Ref": response.get("restructuring_ref", "N/A")
                }
                show_receipt("Loan Restructuring Receipt", receipt_data)

        except Exception as e:
            st.error(f"Failed to submit restructuring request: {e}")
