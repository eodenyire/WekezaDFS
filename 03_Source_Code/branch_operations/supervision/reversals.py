# supervision/reversals.py
import streamlit as st
from .services.api_client import post_request
from .services.permissions import can_reverse_transaction
from .common import get_supervisor_info, validate_transaction_id, show_approval_receipt

def render_reversals_ui(supervisor: dict, api_url: str):
    """
    Render the Reversals UI for supervisors.

    Args:
        supervisor (dict): Supervisor info (id, name, role, branch_code)
        api_url (str): Base URL of the backend API
    """
    st.info("Reverse erroneous or failed transactions.")

    # --- Input Section ---
    transaction_id = st.text_input("Enter Transaction ID to Reverse")
    reason = st.text_area("Reason for Reversal", placeholder="Describe why this transaction should be reversed")

    if st.button("Submit Reversal"):
        # --- Validations ---
        if not transaction_id:
            st.error("Transaction ID is required.")
            return
        if not validate_transaction_id(transaction_id):
            st.error("Invalid Transaction ID format.")
            return
        if not reason.strip():
            st.error("A reason for reversal is required.")
            return
        if not can_reverse_transaction(supervisor['role']):
            st.error("You are not authorized to reverse transactions.")
            return

        # --- Prepare payload ---
        payload = {
            "supervisor_id": supervisor["supervisor_id"],
            "branch_code": supervisor["branch_code"],
            "transaction_id": transaction_id,
            "reason": reason.strip()
        }

        # --- Call Backend API ---
        try:
            response = post_request(f"{api_url}/supervision/reverse-transaction", payload)
            if response.status_code == 200:
                st.success(f"✅ Transaction {transaction_id} successfully reversed.")
                # Display reversal receipt
                show_approval_receipt("Reversal Receipt", response.json())
            else:
                st.error(f"❌ Failed to reverse transaction: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to backend. {e}")
