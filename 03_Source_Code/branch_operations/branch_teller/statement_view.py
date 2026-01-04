import streamlit as st
import pandas as pd
from services.api_client import get_request
from app import get_logged_in_teller
from utils.validators import validate_account_number
from utils.formatting import format_currency

# -----------------------------------------------------------------------------
# STATEMENT VIEW UI
# -----------------------------------------------------------------------------
def render_statement_view_ui(teller: dict):
    """
    Renders Statement View UI for teller.
    Allows mini-statements and full statements.
    """

    st.subheader("📄 Account Statement")

    # -------------------------------
    # INPUT FIELDS
    # -------------------------------
    account_no = st.text_input("Account Number")
    customer_id = st.text_input("Customer National ID")
    
    st.markdown("**Date Range (optional, leave empty for mini-statement)**")
    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("View Statement"):

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
        # BUILD PARAMETERS
        # -------------------------------
        params = {
            "teller_id": teller["teller_id"],
            "branch_code": teller["branch_code"],
            "account_no": account_no,
            "customer_id": customer_id,
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }

        # -------------------------------
        # CALL BACKEND API
        # -------------------------------
        with st.spinner("Fetching statement..."):
            try:
                response = get_request("/teller/statement-view", params=params)
            except Exception as e:
                st.error(f"System error: {e}")
                return

            # -------------------------------
            # HANDLE RESPONSE
            # -------------------------------
            if response.get("status") == "SUCCESS":
                transactions = response.get("transactions", [])

                if not transactions:
                    st.info("No transactions found for this account.")
                    return

                # -------------------------------
                # DISPLAY STATEMENT
                # -------------------------------
                df = pd.DataFrame(transactions)
                df["Amount"] = df["Amount"].apply(format_currency)
                df["Balance"] = df["Balance"].apply(format_currency)

                st.success(f"✅ Statement fetched successfully for account {account_no}")
                st.dataframe(df)

            else:
                st.error(response.get("message", "Unable to fetch statement."))
