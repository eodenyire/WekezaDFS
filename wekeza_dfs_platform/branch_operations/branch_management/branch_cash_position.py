# branch_management/branch_cash_position.py
import streamlit as st
from services.api_client import get_request
from branch_management.common import format_currency

def render_branch_cash_position_ui(manager: dict, api_url: str):
    """
    Render the branch cash position dashboard.

    Args:
        manager (dict): Manager session info (manager_id, name, branch_code, role)
        api_url (str): Base URL of backend API
    """
    st.info("View total cash positions for the branch including vault, ATMs, and tellers.")

    # --- Fetch branch cash data from backend ---
    try:
        response = get_request(f"{api_url}/branch/cash-position", params={"branch_code": manager["branch_code"]})
        if response.status_code != 200:
            st.error(f"Error fetching cash positions: {response.json().get('detail', 'Unknown error')}")
            return

        cash_data = response.json().get("cash_positions", {})
        if not cash_data:
            st.warning("No cash position data available.")
            return
    except Exception as e:
        st.error(f"System Error: Could not fetch cash positions. {e}")
        return

    # --- Display cash positions ---
    st.subheader("💰 Branch Cash Summary")
    st.markdown(f"**Branch:** {manager['branch_code']} | **Manager:** {manager['name']}")

    vault_cash = cash_data.get("vault", 0)
    atm_cash = cash_data.get("atm", 0)
    teller_cash = cash_data.get("tellers", {})

    st.markdown(f"**Vault Cash:** KES {format_currency(vault_cash)}")
    st.markdown(f"**ATM Cash:** KES {format_currency(atm_cash)}")

    st.markdown("**Teller Cash Balances:**")
    if teller_cash:
        for teller_id, amount in teller_cash.items():
            st.markdown(f"- {teller_id}: KES {format_currency(amount)}")
    else:
        st.markdown("No teller cash data available.")

    total_cash = vault_cash + atm_cash + sum(teller_cash.values())
    st.markdown(f"### **Total Branch Cash:** KES {format_currency(total_cash)}")
