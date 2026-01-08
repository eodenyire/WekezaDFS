import streamlit as st
from datetime import datetime

from .common import format_currency, show_receipt
from .services.api_client import post_request
from .services.permissions import can_perform_action

# -----------------------------------------------------------------------------
# UI RENDER FUNCTION
# -----------------------------------------------------------------------------
def render_loan_setup_ui(officer: dict):
    """
    Render the Loan Setup UI tab.
    """

    st.subheader("⚙ Loan Product Setup")

    # --- CHECK PERMISSIONS ---
    if not can_perform_action(officer["role"], "loan_setup"):
        st.error("You are not authorized to setup loan products")
        st.stop()

    # --- LOAN PRODUCT DETAILS ---
    product_name = st.text_input("Loan Product Name", placeholder="e.g., Business Loan")
    max_amount = st.number_input("Maximum Loan Amount (KES)", min_value=1000.0, step=1000.0, format="%.2f")
    min_amount = st.number_input("Minimum Loan Amount (KES)", min_value=1000.0, step=100.0, format="%.2f")
    interest_rate = st.number_input("Interest Rate (%)", min_value=0.1, step=0.1, format="%.2f")
    max_tenure = st.number_input("Maximum Tenure (Months)", min_value=1, step=1)
    min_tenure = st.number_input("Minimum Tenure (Months)", min_value=1, step=1)
    notes = st.text_area("Notes / Description", value="Optional")

    # --- SUBMIT BUTTON ---
    if st.button("Create / Update Loan Product"):
        # VALIDATIONS
        if not product_name.strip():
            st.error("Loan Product Name is required")
            st.stop()
        if min_amount > max_amount:
            st.error("Minimum amount cannot be greater than maximum amount")
            st.stop()
        if min_tenure > max_tenure:
            st.error("Minimum tenure cannot be greater than maximum tenure")
            st.stop()
        if interest_rate <= 0:
            st.error("Interest rate must be greater than 0")
            st.stop()

        # PREPARE PAYLOAD
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "product_name": product_name.strip(),
            "max_amount": max_amount,
            "min_amount": min_amount,
            "interest_rate": interest_rate,
            "max_tenure": max_tenure,
            "min_tenure": min_tenure,
            "notes": notes.strip(),
            "setup_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # CALL BACKEND API
        try:
            with st.spinner("Saving loan product..."):
                response = post_request("/credit/loan-setup", payload)
                st.success("✅ Loan Product Setup Successfully!")

                # SHOW RECEIPT
                receipt_data = {
                    "Date": payload["setup_date"],
                    "Officer": officer["officer_id"],
                    "Branch": officer["branch_code"],
                    "Loan Product": product_name,
                    "Max Amount": format_currency(max_amount),
                    "Min Amount": format_currency(min_amount),
                    "Interest Rate": f"{interest_rate:.2f}%",
                    "Max Tenure": f"{max_tenure} months",
                    "Min Tenure": f"{min_tenure} months",
                    "Notes": notes,
                    "Product Ref": response.get("product_ref", "N/A")
                }
                show_receipt("Loan Product Setup Receipt", receipt_data)

        except Exception as e:
            st.error(f"Failed to setup loan product: {e}")
