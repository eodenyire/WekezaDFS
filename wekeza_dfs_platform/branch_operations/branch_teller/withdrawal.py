import streamlit as st
from services.api_client import post_request
from app import get_logged_in_teller
from utils.validators import validate_amount, validate_account_number
from utils.formatting import format_currency
from datetime import datetime

# -----------------------------------------------------------------------------
# CASH WITHDRAWAL UI
# -----------------------------------------------------------------------------
def render_cash_withdrawal_ui(teller: dict):
    """
    Renders Cash Withdrawal UI for teller.
    Includes maker-checker workflow for high-value withdrawals.
    """

    st.subheader("💸 Cash Withdrawal")

    # -------------------------------
    # INPUT FIELDS
    # -------------------------------
    account_no = st.text_input("Account Number")
    customer_id = st.text_input("Customer National ID")
    amount = st.number_input("Amount (KES)", min_value=50.0, step=100.0)
    remarks = st.text_input("Remarks", value="Cash Withdrawal")

    st.markdown("---")

    # -------------------------------
    # SUBMIT BUTTON
    # -------------------------------
    if st.button("Submit Withdrawal", type="primary"):

        # -------------------------------
        # VALIDATION
        # -------------------------------
        if not validate_account_number(account_no):
            st.error("Invalid account number format.")
            return

        if not customer_id or len(customer_id.strip()) < 5:
            st.error("Please enter a valid Customer National ID.")
            return

        if not validate_amount(amount):
            st.error("Invalid amount. Must be greater than 0.")
            return

        # -------------------------------
        # CHECK CASH LIMIT
        # -------------------------------
        teller_limit = teller.get("cash_limit", 0)
        requires_supervisor = False
        if amount > teller_limit:
            requires_supervisor = True
            st.warning(
                f"⚠ Amount exceeds teller limit ({format_currency(teller_limit)}). "
                "This withdrawal will require supervisor approval."
            )

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
            "remarks": remarks,
            "requires_approval": requires_supervisor,
            "transaction_date": datetime.now().isoformat()
        }

        # -------------------------------
        # CALL BACKEND API
        # -------------------------------
        with st.spinner("Processing withdrawal..."):
            try:
                response = post_request("/teller/cash-withdrawals", payload)
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
                    f"Withdrawal requires supervisor approval.\nReference No: {ref_no}"
                )
            elif status == "SUCCESS":
                st.success("✅ Withdrawal successful.")
            else:
                st.error(response.get("message", "Withdrawal failed."))

            # -------------------------------
            # DISPLAY RECEIPT
            # -------------------------------
            st.markdown("### 🧾 Digital Receipt")
            st.code(f"""
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Reference: {ref_no}
Customer: {customer_id}
Account: {account_no}
Amount: {format_currency(amount)}
Teller: {teller['teller_id']}
Branch: {teller['branch_code']}
Remarks: {remarks}
Status: {status}
""", language="text")
