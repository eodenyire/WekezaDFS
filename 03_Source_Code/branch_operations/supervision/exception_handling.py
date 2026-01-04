# supervision/exception_handling.py
import streamlit as st
from .services.api_client import post_request, get_request
from .services.permissions import can_handle_exceptions
from .common import get_supervisor_info, validate_transaction_id, show_approval_receipt, format_currency, format_date

def render_exceptions_ui(supervisor: dict, api_url: str):
    """
    Render the Exception Handling UI for supervisors.

    Args:
        supervisor (dict): Supervisor info (id, name, role, branch_code)
        api_url (str): Base URL of the backend API
    """
    st.info("Handle exceptional or irregular transactions.")

    # --- Permission check ---
    if not can_handle_exceptions(supervisor['role']):
        st.error("You are not authorized to handle exceptions.")
        return

    # --- Fetch exceptions from backend ---
    try:
        response = get_request(
            f"{api_url}/supervision/exceptions",
            params={"branch_code": supervisor['branch_code']}
        )
        if response.status_code != 200:
            st.error(f"Error fetching exceptions: {response.json().get('detail', 'Unknown error')}")
            return
        exceptions = response.json().get("exceptions", [])
    except Exception as e:
        st.error(f"System Error: Could not fetch exceptions. {e}")
        return

    if not exceptions:
        st.success("No exceptional transactions at this time.")
        return

    # --- Display exceptions ---
    for ex in exceptions:
        with st.expander(f"Exception: {ex['type']} | Ref: {ex['reference']} | Amount: KES {format_currency(ex['amount'])}"):
            st.write(f"**Transaction ID:** {ex['transaction_id']}")
            st.write(f"**Customer ID:** {ex['customer_id']}")
            st.write(f"**Teller ID:** {ex.get('teller_id', '-')}")
            st.write(f"**Date:** {format_date(ex['date'])}")
            st.write(f"**Amount:** KES {format_currency(ex['amount'])}")
            st.write(f"**Remarks:** {ex.get('remarks', '-')}")
            st.write(f"**Issue:** {ex.get('issue', '-')}")
            st.write(f"**Status:** {ex['status']}")

            # --- Action Section ---
            resolution = st.text_area(f"Resolution for {ex['transaction_id']}", placeholder="Enter your resolution here")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Resolve {ex['transaction_id']}", key=f"resolve_{ex['transaction_id']}"):
                    if not resolution.strip():
                        st.error("Please enter a resolution.")
                    else:
                        payload = {
                            "supervisor_id": supervisor['supervisor_id'],
                            "branch_code": supervisor['branch_code'],
                            "transaction_id": ex['transaction_id'],
                            "resolution": resolution.strip()
                        }
                        try:
                            res = post_request(f"{api_url}/supervision/handle-exception", payload)
                            if res.status_code == 200:
                                st.success(f"Exception {ex['transaction_id']} resolved successfully.")
                                show_approval_receipt(f"Exception Resolution Receipt", res.json())
                            else:
                                st.error(f"Failed to resolve exception: {res.json().get('detail', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"System Error: Could not connect to backend. {e}")
            with col2:
                if st.button(f"❌ Mark as Pending {ex['transaction_id']}", key=f"pending_{ex['transaction_id']}"):
                    st.warning(f"Exception {ex['transaction_id']} marked as pending for further review.")
