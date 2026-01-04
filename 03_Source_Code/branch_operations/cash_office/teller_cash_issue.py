import streamlit as st
from datetime import datetime
from common import validate_amount, validate_teller_id, show_cash_receipt, get_cash_officer_info
from services.api_client import post_request
from services.permissions import requires_supervisor_approval

# --- Issue Cash to Teller UI ---
def issue_cash_ui(officer_info):
    st.subheader("💵 Teller Cash Issue")

    # Input: Teller ID
    teller_id = st.text_input("Enter Teller ID", placeholder="e.g., TEL-001")
    if teller_id and not validate_teller_id(teller_id):
        st.error("Invalid Teller ID format.")
        return

    # Input: Cash amount to issue
    amount = st.number_input(
        "Enter Cash Amount (KES)",
        min_value=50.0,
        step=100.0,
        format="%.2f"
    )

    # Input: Denomination breakdown
    denominations = st.text_area(
        "Enter Denomination Breakdown (e.g., 1000x50, 500x100)",
        placeholder="Format: 1000x50, 500x100"
    )

    if st.button("Issue Cash"):
        # Validate inputs
        if not teller_id:
            st.error("Teller ID is required.")
            return
        if amount <= 0:
            st.error("Amount must be greater than 0.")
            return
        if not denominations:
            st.error("Denomination breakdown is required.")
            return

        # Check if supervisor approval is needed
        if requires_supervisor_approval(officer_info["officer_id"], amount):
            st.warning("Supervisor approval required for this cash issuance.")

        # Prepare payload for backend
        payload = {
            "officer_id": officer_info["officer_id"],
            "branch_code": officer_info["branch_code"],
            "teller_id": teller_id,
            "amount": amount,
            "denominations": denominations,
            "timestamp": datetime.now().isoformat()
        }

        # Call backend API
        try:
            response = post_request("/cash-office/teller-issue", payload)
            if response.get("status") == "success":
                show_cash_receipt("Teller Cash Issue Receipt", {
                    "Teller ID": teller_id,
                    "Issued Amount": amount,
                    "Denominations": denominations,
                    "Issued By": officer_info["officer_id"],
                    "Branch": officer_info["branch_code"],
                    "Timestamp": payload["timestamp"]
                })
                st.success(f"✅ Successfully issued KES {amount:,.2f} to Teller {teller_id}.")
            else:
                st.error(f"Failed to issue cash: {response.get('detail')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to Core Banking. {e}")
