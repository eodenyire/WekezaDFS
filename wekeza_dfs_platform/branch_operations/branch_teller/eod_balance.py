import streamlit as st
from services.api_client import get_request, post_request
from app import get_logged_in_teller
from utils.formatting import format_currency
from datetime import datetime

# -----------------------------------------------------------------------------
# END-OF-DAY BALANCE UI
# -----------------------------------------------------------------------------
def render_eod_balance_ui(teller: dict):
    """
    Renders End-of-Day Balance UI for the teller.
    Allows teller to reconcile cash and submit end-of-day report.
    """

    st.subheader("📦 End-of-Day Balance & Reconciliation")

    # -------------------------------
    # FETCH CURRENT EOD DATA
    # -------------------------------
    with st.spinner("Fetching end-of-day summary..."):
        try:
            params = {
                "teller_id": teller["teller_id"],
                "branch_code": teller["branch_code"]
            }
            response = get_request("/teller/eod-summary", params=params)
        except Exception as e:
            st.error(f"System error: {e}")
            return

        if response.get("status") != "SUCCESS":
            st.error(response.get("message", "Unable to fetch EOD summary."))
            return

        summary = response.get("summary", {})
        opening_balance = summary.get("opening_balance", 0.0)
        total_deposits = summary.get("total_deposits", 0.0)
        total_withdrawals = summary.get("total_withdrawals", 0.0)

        expected_closing = opening_balance + total_deposits - total_withdrawals

        st.markdown(f"**Opening Balance:** {format_currency(opening_balance)}")
        st.markdown(f"**Total Deposits:** {format_currency(total_deposits)}")
        st.markdown(f"**Total Withdrawals:** {format_currency(total_withdrawals)}")
        st.markdown(f"**Expected Closing Balance:** {format_currency(expected_closing)}")

    # -------------------------------
    # ACTUAL CASH COUNT
    # -------------------------------
    st.markdown("---")
    st.subheader("Enter Actual Cash Count")
    actual_cash = st.number_input("Actual Cash in Drawer (KES)", min_value=0.0, step=100.0)

    if st.button("Submit EOD Report"):

        discrepancy = actual_cash - expected_closing
        status = "BALANCED" if discrepancy == 0 else "DISCREPANCY"

        payload = {
            "teller_id": teller["teller_id"],
            "branch_code": teller["branch_code"],
            "actual_cash": float(actual_cash),
            "expected_closing": float(expected_closing),
            "discrepancy": float(discrepancy),
            "status": status,
            "eod_date": datetime.now().isoformat()
        }

        # -------------------------------
        # CALL BACKEND API
        # -------------------------------
        with st.spinner("Submitting end-of-day report..."):
            try:
                res = post_request("/teller/eod-submit", payload)
            except Exception as e:
                st.error(f"System error: {e}")
                return

            if res.get("status") == "SUCCESS":
                st.success(f"✅ EOD Report submitted successfully. Status: {status}")
                if discrepancy != 0:
                    st.warning(f"⚠ Discrepancy detected: {format_currency(discrepancy)}")
                st.markdown("### 🧾 EOD Summary Receipt")
                st.code(f"""
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Teller: {teller['teller_id']}
Branch: {teller['branch_code']}
Opening Balance: {format_currency(opening_balance)}
Total Deposits: {format_currency(total_deposits)}
Total Withdrawals: {format_currency(total_withdrawals)}
Expected Closing Balance: {format_currency(expected_closing)}
Actual Cash Counted: {format_currency(actual_cash)}
Discrepancy: {format_currency(discrepancy)}
Status: {status}
""", language="text")
            else:
                st.error(res.get("message", "Failed to submit EOD report."))
