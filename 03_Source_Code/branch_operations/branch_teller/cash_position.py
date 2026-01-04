import streamlit as st
from services.api_client import get_request
from app import get_logged_in_teller
from utils.formatting import format_currency
import pandas as pd

# -----------------------------------------------------------------------------
# CASH POSITION UI
# -----------------------------------------------------------------------------
def render_cash_position_ui(teller: dict):
    """
    Renders Cash Position UI for the teller.
    Shows current cash held and breakdown by denomination.
    """

    st.subheader("📊 Teller Cash Position")

    with st.spinner("Fetching cash position..."):
        try:
            params = {
                "teller_id": teller["teller_id"],
                "branch_code": teller["branch_code"]
            }
            response = get_request("/teller/cash-position", params=params)
        except Exception as e:
            st.error(f"System error: {e}")
            return

        # -------------------------------
        # HANDLE RESPONSE
        # -------------------------------
        if response.get("status") == "SUCCESS":
            cash_info = response.get("cash_info", {})
            total_cash = cash_info.get("total_cash", 0.0)
            denominations = cash_info.get("denominations", [])

            st.success(f"✅ Current Cash-in-Hand: {format_currency(total_cash)}")

            if denominations:
                st.markdown("### 💵 Denomination Breakdown")
                # Convert list of dicts to DataFrame for display
                df = pd.DataFrame(denominations)
                df["Amount"] = df["Amount"].apply(format_currency)
                st.dataframe(df)
            else:
                st.info("Denomination breakdown not available.")

        else:
            st.error(response.get("message", "Unable to fetch cash position."))
