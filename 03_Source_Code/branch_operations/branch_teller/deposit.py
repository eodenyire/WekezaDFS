import streamlit as st
from services.api_client import post_request
from app import get_logged_in_teller
from utils.validators import validate_amount, validate_account_number
from utils.formatting import format_currency
from datetime import datetime

# -----------------------------------------------------------------------------
# CASH DEPOSIT UI
# -----------------------------------------------------------------------------
def render_cash_deposit_ui(teller: dict):
    """
    Renders the Cash Deposit UI for the teller.
    All deposits are routed through backend for maker-checker approval.
    """

    st.subheader("💰 Cash Deposit")

    # -------------------------------
    # CUSTOMER & ACCOUNT DETAILS
    # -------------------------------
    account_no = st.text_input("Account Number")
    customer_id = st.text_input("Customer National ID")
    amount = st.number_input("Amount (KES)", min_value=50.0, step=100.0)
    source_of_funds = st.text_input("Source of Funds / Remarks", value="Cash Deposit")

    st.markdown("---")

    # -------------------------------
    # VALIDATION
    # -------------------------------
    if st.button("Submit Deposit", type="primary"):
        # Input validation
        if not validate_account_number(account_no):
            st.error("Invalid account number format.")
            return

        if not customer_id or len(customer_id.strip()) < 5:
            st.error("Please enter a valid Customer National ID.")
            return

        if not validate_amount(amount):
            st.error("Invalid amount. Must be greater than 0 and below teller limit.")
            return

        # -------------------------------
        # BUILD PAYLOAD
        # -------------------------------
        payload = {
            "teller_id": teller["teller_id"],
            "branch_code": teller["branch_code"],
            "account_no": account_no,
            "customer_id": customer_id,
            "amount": float(amount),
            "currency": "KES",
            "source_of_funds": source_of_funds,
            "transaction_date": datetime.now().isoformat()
        }

        # -------------------------------
        # CALL BACKEND API
        # -------------------------------
        with st.spinner("Processing deposit..."):
            try:
                response = post_request("/teller/cash-deposits", payload)
            except Exception as e:
                st.error(f"System error: {e}")
                return

            # -------------------------------
            # HANDLE RESPONSE
            # -------------------------------
            if response.get("status") == "SUCCESS":
                st.success("✅ Deposit submitted successfully.")
                st.markdown("### 🧾 Digital Receipt")
                st.code(f"""
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Ref: {response['reference_number']}
Customer: {customer_id}
Account: {account_no}
Amount: {format_currency(amount)}
Teller: {teller['teller_id']}
Branch: {teller['branch_code']}
Remarks: {source_of_funds}
Status: {response['status']}
""", language="text")

            else:
                st.error(response.get("message", "Deposit failed."))
