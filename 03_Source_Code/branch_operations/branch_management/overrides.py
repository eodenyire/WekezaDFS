# branch_management/overrides.py
import streamlit as st
from services.api_client import post_request
from services.permissions import has_permission
from branch_management.common import get_branch_manager_info, validate_transaction_id, show_override_receipt

def render_overrides_ui(manager: dict, api_url: str):
    """
    Render the UI for branch manager-level overrides.
    
    Args:
        manager (dict): Manager session info (id, name, branch_code, role)
        api_url (str): Base URL of the backend API
    """
    st.info("Manager Overrides: Approve transactions or handle exceptions beyond normal limits.")

    # --- Input Section ---
    transaction_id = st.text_input("Transaction ID to Override")
    override_type = st.selectbox("Override Type", ["Approval", "Reversal", "Exception"])
    reason = st.text_area("Reason for Override", placeholder="Explain why this override is necessary")

    if st.button("Submit Override"):
        # --- Validations ---
        if not transaction_id:
            st.error("Transaction ID is required.")
            return
        if not validate_transaction_id(transaction_id):
            st.error("Invalid Transaction ID format.")
            return
        if not reason.strip():
            st.error("Please provide a reason for the override.")
            return
        if not has_permission(manager['role'], "approve"):
            st.error("You are not authorized to perform overrides.")
            return

        # --- Payload for Backend ---
        payload = {
            "manager_id": manager["manager_id"],
            "branch_code": manager["branch_code"],
            "transaction_id": transaction_id,
            "override_type": override_type,
            "reason": reason.strip()
        }

        # --- Call Backend API ---
        try:
            response = post_request(f"{api_url}/branch_manager/override", payload)
            if response.status_code == 200:
                st.success(f"✅ Override successful for transaction {transaction_id}")
                # Show override receipt
                show_override_receipt("Manager Override Receipt", response.json())
            else:
                st.error(f"❌ Override failed: {response.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to backend. {e}")
