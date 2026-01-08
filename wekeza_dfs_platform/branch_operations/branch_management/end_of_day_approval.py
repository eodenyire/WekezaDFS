# branch_management/end_of_day_approval.py
import streamlit as st
from services.api_client import get_request, post_request
from branch_management.common import format_currency, validate_transaction_id

def render_eod_approval_ui(manager: dict, api_url: str):
    """
    Render the End-of-Day (EOD) approval UI for branch managers.

    Args:
        manager (dict): Manager session info (manager_id, name, branch_code, role)
        api_url (str): Base URL of backend API
    """
    st.info("Review and approve branch end-of-day balances and reconciliations.")

    # --- Fetch EOD Summary ---
    try:
        response = get_request(f"{api_url}/branch/eod-summary", params={"branch_code": manager["branch_code"]})
        if response.status_code != 200:
            st.error(f"Error fetching EOD summary: {response.json().get('detail', 'Unknown error')}")
            return

        eod_data = response.json().get("eod_summary", {})
        if not eod_data:
            st.warning("No EOD data available for approval.")
            return
    except Exception as e:
        st.error(f"System Error: Could not fetch EOD summary. {e}")
        return

    # --- Display EOD Summary ---
    st.subheader("📊 End-of-Day Summary")
    st.markdown(f"**Branch:** {manager['branch_code']} | **Manager:** {manager['name']}")
    st.markdown(f"- Total Cash In Vault: KES {format_currency(eod_data.get('vault_cash', 0))}")
    st.markdown(f"- Total Cash with Tellers: KES {format_currency(sum(eod_data.get('teller_cash', {}).values()))}")
    st.markdown(f"- Total ATM Cash: KES {format_currency(eod_data.get('atm_cash', 0))}")
    st.markdown(f"- Total Deposits Today: KES {format_currency(eod_data.get('total_deposits', 0))}")
    st.markdown(f"- Total Withdrawals Today: KES {format_currency(eod_data.get('total_withdrawals', 0))}")
    st.markdown(f"- Reconciliation Status: {eod_data.get('reconciliation_status', 'Pending')}")

    # --- Approve or Reject EOD ---
    st.subheader("✅ Approve End-of-Day")
    approval_action = st.radio("Select Action", ["Approve", "Reject"], index=0)
    reason = st.text_area("Reason (required if rejecting)", placeholder="Provide reason if rejecting")

    if st.button("Submit EOD Approval"):
        # Validations
        if approval_action == "Reject" and not reason.strip():
            st.error("You must provide a reason when rejecting EOD.")
            return

        payload = {
            "manager_id": manager["manager_id"],
            "branch_code": manager["branch_code"],
            "approval_action": approval_action,
            "reason": reason.strip()
        }

        # --- Send Approval to Backend ---
        try:
            res = post_request(f"{api_url}/branch/eod-approval", payload)
            if res.status_code == 200:
                st.success(f"✅ EOD successfully {approval_action.lower()}ed.")
            else:
                st.error(f"❌ Failed to submit EOD approval: {res.json().get('detail', 'Unknown error')}")
        except Exception as e:
            st.error(f"System Error: Could not submit EOD approval. {e}")
