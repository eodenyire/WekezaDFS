import streamlit as st
from datetime import datetime
from common import validate_amount, show_cash_receipt, get_cash_officer_info
from services.api_client import post_request
from services.permissions import requires_supervisor_approval

# --- Vault Opening UI ---
def open_vault_ui(officer_info):
    st.subheader("🟢 Vault Opening")

    # Input: Opening balance
    opening_balance = st.number_input(
        "Enter Vault Opening Balance (KES)",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )

    # Input: Cash denominations breakdown
    denominations = st.text_area(
        "Enter Denomination Breakdown (e.g., 1000x50, 500x100)",
        placeholder="Format: 1000x50, 500x100"
    )

    if st.button("Open Vault"):
        if opening_balance <= 0:
            st.error("Opening balance must be greater than 0.")
            return
        if not denominations:
            st.error("Please enter denomination breakdown.")
            return

        # Check if supervisor approval is required for large amounts
        if requires_supervisor_approval(officer_info["officer_id"], opening_balance):
            st.warning("Supervisor approval required for opening this vault amount.")
        
        payload = {
            "officer_id": officer_info["officer_id"],
            "branch_code": officer_info["branch_code"],
            "opening_balance": opening_balance,
            "denominations": denominations,
            "timestamp": datetime.now().isoformat()
        }

        try:
            response = post_request("/cash-office/vault/open", payload)
            if response.get("status") == "success":
                show_cash_receipt("Vault Opening Receipt", {
                    "Vault Status": "Opened",
                    "Opening Balance": opening_balance,
                    "Denominations": denominations,
                    "Officer": officer_info["officer_id"],
                    "Timestamp": payload["timestamp"]
                })
                st.success("Vault opened successfully!")
            else:
                st.error(f"Failed to open vault: {response.get('detail')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to Core Banking. {e}")

# --- Vault Closing UI ---
def close_vault_ui(officer_info):
    st.subheader("🔴 Vault Closing")

    # Input: Closing balance
    closing_balance = st.number_input(
        "Enter Vault Closing Balance (KES)",
        min_value=0.0,
        step=100.0,
        format="%.2f"
    )

    # Input: Cash denominations breakdown
    denominations = st.text_area(
        "Enter Denomination Breakdown (e.g., 1000x50, 500x100)",
        placeholder="Format: 1000x50, 500x100"
    )

    if st.button("Close Vault"):
        if closing_balance < 0:
            st.error("Closing balance cannot be negative.")
            return
        if not denominations:
            st.error("Please enter denomination breakdown.")
            return

        # Check if supervisor approval is required for discrepancies
        if requires_supervisor_approval(officer_info["officer_id"], closing_balance):
            st.warning("Supervisor approval required for closing this vault amount.")

        payload = {
            "officer_id": officer_info["officer_id"],
            "branch_code": officer_info["branch_code"],
            "closing_balance": closing_balance,
            "denominations": denominations,
            "timestamp": datetime.now().isoformat()
        }

        try:
            response = post_request("/cash-office/vault/close", payload)
            if response.get("status") == "success":
                show_cash_receipt("Vault Closing Receipt", {
                    "Vault Status": "Closed",
                    "Closing Balance": closing_balance,
                    "Denominations": denominations,
                    "Officer": officer_info["officer_id"],
                    "Timestamp": payload["timestamp"]
                })
                st.success("Vault closed successfully!")
            else:
                st.error(f"Failed to close vault: {response.get('detail')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to Core Banking. {e}")
