# bancassurance/claims_tracking.py

import streamlit as st
from bancassurance.common import validate_customer_id, format_currency, show_receipt
from bancassurance.services.api_client import get_request, post_request
from bancassurance.services.permissions import can_manage_claims

# --- CLAIMS TRACKING UI ---
def render_claims_tracking_ui(officer):
    """
    Render the Claims Tracking tab UI for Bancassurance Officers.

    Args:
        officer (dict): Officer session information (officer_id, name, role, branch_code)
    """

    st.info("Track and manage insurance claims for customers")

    # --- Customer Information ---
    st.subheader("Customer Information")
    customer_id = st.text_input("Customer National ID / CIF", placeholder="e.g., 12345678")

    if customer_id and st.button("Fetch Claims"):
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            return

        try:
            response = get_request(f"/bancassurance/claims?customer_id={customer_id}")

            if response.get("status") != "success" or not response.get("data"):
                st.warning("No claims found for this customer.")
                return

            st.session_state["claims"] = response["data"]
            st.success(f"Fetched {len(response['data'])} claims for customer {customer_id}.")

        except Exception as e:
            st.error(f"System Error: Could not fetch claims. {e}")
            return

    # --- Claims List & Status Update ---
    if "claims" in st.session_state:
        st.subheader("Customer Claims")
        for i, claim in enumerate(st.session_state["claims"]):
            st.markdown(f"**Claim #{claim['claim_number']} - {claim['policy_type']}**")
            st.write(f"Amount Claimed: {format_currency(claim['claim_amount'])}")
            st.write(f"Status: {claim['status']}")
            st.write(f"Submitted On: {claim['submitted_on']}")

            # Only allow updates if the officer has permissions
            if can_manage_claims(officer["role"]):
                new_status = st.selectbox(
                    f"Update Status for Claim #{claim['claim_number']}",
                    ["Pending", "Under Review", "Approved", "Rejected"],
                    index=["Pending", "Under Review", "Approved", "Rejected"].index(claim['status'])
                )
                remarks = st.text_input(f"Remarks for Claim #{claim['claim_number']}", value=claim.get("remarks", ""))

                if st.button(f"Update Claim #{claim['claim_number']}", key=f"update_{i}"):
                    payload = {
                        "officer_id": officer["officer_id"],
                        "branch_code": officer["branch_code"],
                        "claim_number": claim["claim_number"],
                        "new_status": new_status,
                        "remarks": remarks
                    }

                    try:
                        update_response = post_request("/bancassurance/claims-update", payload)

                        if update_response.get("status") == "success":
                            st.success(f"✅ Claim #{claim['claim_number']} updated successfully!")
                            show_receipt(f"Claim Update Receipt #{claim['claim_number']}", update_response["data"])
                        else:
                            st.error(f"❌ Failed to update claim: {update_response.get('message')}")
                    except Exception as e:
                        st.error(f"System Error: Could not connect to backend. {e}")
