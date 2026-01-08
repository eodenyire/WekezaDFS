import streamlit as st
from datetime import datetime
from common import validate_amount, show_cash_receipt, get_cash_officer_info
from services.api_client import post_request
from services.permissions import requires_supervisor_approval

# --- ATM Cash Loading UI ---
def load_atm_ui(officer_info):
    st.subheader("🏧 ATM Cash Loading")

    # Input: ATM ID
    atm_id = st.text_input("Enter ATM ID", placeholder="e.g., ATM-NBO-01")
    if not atm_id:
        st.error("ATM ID is required.")
        return

    # Input: Cash amount to load
    amount = st.number_input(
        "Enter Cash Amount to Load (KES)",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )

    # Input: Denomination breakdown
    denominations = st.text_area(
        "Enter Denomination Breakdown (e.g., 1000x50, 500x100)",
        placeholder="Format: 1000x50, 500x100"
    )

    if st.button("Load Cash into ATM"):
        # Validate inputs
        if amount <= 0:
            st.error("Amount must be greater than 0.")
            return
        if not denominations:
            st.error("Denomination breakdown is required.")
            return

        # Check supervisor approval for large amounts
        if requires_supervisor_approval(officer_info["officer_id"], amount):
            st.warning("Supervisor approval required for loading this ATM amount.")

        # Prepare payload
        payload = {
            "officer_id": officer_info["officer_id"],
            "branch_code": officer_info["branch_code"],
            "atm_id": atm_id,
            "amount": amount,
            "denominations": denominations,
            "timestamp": datetime.now().isoformat()
        }

        # Call backend API
        try:
            response = post_request("/cash-office/atm-load", payload)
            if response.get("status") == "success":
                show_cash_receipt("ATM Cash Loading Receipt", {
                    "ATM ID": atm_id,
                    "Loaded Amount": amount,
                    "Denominations": denominations,
                    "Loaded By": officer_info["officer_id"],
                    "Branch": officer_info["branch_code"],
                    "Timestamp": payload["timestamp"]
                })
                st.success(f"✅ Successfully loaded KES {amount:,.2f} into ATM {atm_id}.")
            else:
                st.error(f"Failed to load ATM: {response.get('detail')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to Core Banking. {e}")
