import streamlit as st
from services.api_client import get_request
from app import get_logged_in_teller
from utils.validators import validate_account_number
from utils.formatting import format_currency

# -----------------------------------------------------------------------------
# BALANCE ENQUIRY UI
# -----------------------------------------------------------------------------
def render_balance_enquiry_ui(teller: dict):
    """
    Renders the Balance Enquiry UI for teller.
    Read-only operation, no transaction is performed.
    """

    st.subheader("🔍 Balance Enquiry")

    # -------------------------------
    # INPUT FIELDS
    # -------------------------------
    account_no = st.text_input("Account Number")
    customer_id = st.text_input("Customer National ID")

    if st.button("Check Balance"):

        # -------------------------------
        # VALIDATION
        # -------------------------------
        if not validate_account_number(account_no):
            st.error("Invalid account number.")
            return

        if not customer_id or len(customer_id.strip()) < 5:
            st.error("Invalid Customer National ID.")
            return

        # -------------------------------
        # CALL BACKEND API
        # -------------------------------
        with st.spinner("Fetching account balance..."):
            try:
                params = {
                    "teller_id": teller["teller_id"],
                    "branch_code": teller["branch_code"],
                    "account_no": account_no,
                    "customer_id": customer_id
                }
                response = get_request("/teller/balance-enquiry", params=params)
            except Exception as e:
                st.error(f"System error: {e}")
                return

            # -------------------------------
            # HANDLE RESPONSE
            # -------------------------------
            if response.get("status") == "SUCCESS":
                balance_info = response.get("balance", {})
                ledger_balance = balance_info.get("ledger_balance", 0.0)
                available_balance = balance_info.get("available_balance", 0.0)

                st.success(f"✅ Balance fetched successfully for account {account_no}")
                st.markdown("### Account Balance")
                st.write(f"**Ledger Balance:** {format_currency(ledger_balance)}")
                st.write(f"**Available Balance:** {format_currency(available_balance)}")

            else:
                st.error(response.get("message", "Unable to fetch balance."))
