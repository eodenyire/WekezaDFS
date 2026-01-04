import streamlit as st
from services.api_client import post_request
from app import get_logged_in_teller
from utils.validators import validate_account_number, validate_amount
from utils.formatting import format_currency
from datetime import datetime

# -----------------------------------------------------------------------------
# CHEQUE DEPOSIT UI
# -----------------------------------------------------------------------------
def render_cheque_deposit_ui(teller: dict):
    """
    Renders the Cheque Deposit UI for the teller.
    All cheque deposits are routed through backend for maker-checker approval.
    """

    st.subheader("🧾 Cheque Deposit")

    # -------------------------------
    # INPUT FIELDS
    # -------------------------------
    account_no = st.text_input("Account Number")
    customer_id = st.text_input("Customer National ID")
    cheque_number = st.text_input("Cheque Number")
    bank_name = st.text_input("Bank Name")
    amount = st.number_input("Amount (KES)", min_value=1.0, step=100.0)
    remarks = st.text_input("Remarks", value="Cheque Deposit")

    st.markdown("---")

    # -------------------------------
    # VALIDATION
    # -------------------------------
    if st.button("Submit Cheque", type="primary"):

        if not validate_account_number(account_no):
            st.error("Invalid account number.")
            return

        if not customer_id or len(customer_id.strip()) < 5:
            st.error("Invalid Customer National ID.")
            return

        if not cheque_number or len(cheque_number.strip()) < 3:
            st.error("Invalid Cheque Number.")
            return

        if not bank_name:
            st.error("Bank Name is required.")
            return

        if not validate_amount(amount):
            st.error("Invalid amount. Must be greater than 0.")
            return

        # -------------------------------
        # BUILD PAYLOAD
        # -------------------------------
        payload = {
            "teller_id": teller["teller_id"],
            "branch_code": teller["branch_code"],
            "account_no": account_no,
            "customer_id": customer_id,
            "cheque_number": cheque_number,
            "bank_name": bank_name,
            "amount": float(amount),
            "currency": "KES",
            "remarks": remarks,
            "transaction_date": datetime.now().isoformat()
        }

        # -------------------------------
        # CALL BACKEND API
        # -------------------------------
        with st.spinner("Submitting cheque..."):
            try:
                response = post_request("/teller/cheque-deposits", payload)
            except Exception as e:
                st.error(f"System error: {e}")
                return

            # -------------------------------
            # HANDLE RESPONSE
            # -------------------------------
            status = response.get("status")
            ref_no = response.get("reference_number", "N/A")

            if status == "PENDING_APPROVAL":
                st.info(
                    f"Cheque deposit submitted successfully.\n"
                    f"Reference No: {ref_no}\n"
                    f"Status: Pending Supervisor Approval"
                )
            elif status == "SUCCESS":
                st.success("✅ Cheque deposit successful.")
            else:
                st.error(response.get("message", "Cheque deposit failed."))

            # -------------------------------
            # DIGITAL RECEIPT
            # -------------------------------
            st.markdown("### 🧾 Digital Receipt")
            st.code(f"""
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Reference: {ref_no}
Customer: {customer_id}
Account: {account_no}
Cheque Number: {cheque_number}
Bank: {bank_name}
Amount: {format_currency(amount)}
Teller: {teller['teller_id']}
Branch: {teller['branch_code']}
Remarks: {remarks}
Status: {status}
""", language="text")
