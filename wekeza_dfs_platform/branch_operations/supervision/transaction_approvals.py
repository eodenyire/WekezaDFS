# supervision/transaction_approvals.py
import streamlit as st
from .services.api_client import post_request
from .services.permissions import can_approve_transaction
from .common import get_supervisor_info, validate_transaction_id, show_approval_receipt

def render_approvals_ui(supervisor: dict, api_url: str):
    """
    Render the Transaction Approvals UI for the supervisor.

    Args:
        supervisor (dict): Supervisor info (id, name, role, branch_code)
        api_url (str): Base URL of the backend API
    """
    st.info("Approve or reject transactions pending authorization.")

    # --- Input Section ---
    transaction_id = st.text_input("Enter Transaction ID to Approve/Reject")
    action = st.radio("Action", ["Approve", "Reject"])

    if st.button("Submit"):
        if not transaction_id:
            st.error("Transaction ID is required.")
            return
        if not validate_transaction_id(transaction_id):
            st.error("Invalid Transaction ID format.")
            return
        if not can_approve_transaction(supervisor['role']):
            st.error("You are not authorized to approve/reject this transaction.")
            return

        # --- Prepare payload ---
        payload = {
            "supervisor_id": supervisor["supervisor_id"],
            "branch_code": supervisor["branch_code"],
            "transaction_id": transaction_id,
            "action": action.lower()
        }

        # --- Call Backend API ---
        try:
            response = post_request(f"{api_url}/supervision/approve-transaction", payload)
            if response.status_code == 200:
                st.success(f"✅ Transaction {transaction_id} successfully {action.lower()}d.")
                # Display receipt
                show_approval_receipt(f"Transaction {action} Receipt", response.json())
            else:
                st.error(f"❌ Failed to {action.lower()} transaction: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to backend. {e}")
