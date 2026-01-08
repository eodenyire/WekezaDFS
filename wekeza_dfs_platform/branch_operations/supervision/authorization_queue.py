# supervision/authorization_queue.py
import streamlit as st
from .services.api_client import get_request
from .services.permissions import can_view_authorization_queue
from .common import format_currency, format_date

def render_queue_ui(supervisor: dict, api_url: str):
    """
    Render the Authorization Queue UI for the supervisor.
    
    Args:
        supervisor (dict): Supervisor info (id, name, role, branch_code)
        api_url (str): Base URL of the backend API
    """
    # Check if supervisor has permission to view the queue
    if not can_view_authorization_queue(supervisor['role']):
        st.error("You do not have permission to view the authorization queue.")
        return

    st.info("Displaying all transactions pending your approval.")

    # --- Fetch pending transactions from backend ---
    try:
        # Example endpoint: GET /supervision/authorization-queue?branch_code=XXX
        response = get_request(
            f"{api_url}/supervision/authorization-queue",
            params={"branch_code": supervisor['branch_code']}
        )
        if response.status_code != 200:
            st.error(f"Error fetching transactions: {response.json().get('detail', 'Unknown error')}")
            return

        transactions = response.json().get("transactions", [])
    except Exception as e:
        st.error(f"System Error: Could not fetch transactions. {e}")
        return

    # --- Display queue ---
    if not transactions:
        st.success("No transactions pending approval.")
        return

    # --- Search / Filter Section ---
    st.subheader("Filter Transactions")
    filter_type = st.selectbox("Transaction Type", ["All"] + list(set(tx['type'] for tx in transactions)))
    filter_teller = st.text_input("Teller ID (optional)")
    filter_amount = st.number_input("Min Amount (optional)", min_value=0.0, step=100.0, format="%.2f")

    # Apply filters
    filtered_transactions = []
    for tx in transactions:
        if filter_type != "All" and tx['type'] != filter_type:
            continue
        if filter_teller and filter_teller not in tx['teller_id']:
            continue
        if filter_amount > 0 and tx['amount'] < filter_amount:
            continue
        filtered_transactions.append(tx)

    # --- Display Table ---
    st.subheader(f"Pending Transactions ({len(filtered_transactions)})")
    for tx in filtered_transactions:
        with st.expander(f"{tx['type']} | Ref: {tx['reference']} | Amount: KES {format_currency(tx['amount'])}"):
            st.write(f"**Transaction ID:** {tx['id']}")
            st.write(f"**Teller ID:** {tx['teller_id']}")
            st.write(f"**Customer ID:** {tx['customer_id']}")
            st.write(f"**Date:** {format_date(tx['date'])}")
            st.write(f"**Amount:** KES {format_currency(tx['amount'])}")
            st.write(f"**Remarks:** {tx.get('remarks', '-')}")
            st.write(f"**Status:** {tx['status']}")

            # Show Approve / Reject buttons only if status is pending
            if tx['status'].lower() == "pending":
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"✅ Approve {tx['id']}", key=f"approve_{tx['id']}"):
                        st.info(f"Approval action triggered for transaction {tx['id']}.")
                        # Call approval API in transaction_approvals.py (handled elsewhere)
                with col2:
                    if st.button(f"❌ Reject {tx['id']}", key=f"reject_{tx['id']}"):
                        st.info(f"Rejection action triggered for transaction {tx['id']}.")
                        # Call rejection API in transaction_approvals.py (handled elsewhere)
