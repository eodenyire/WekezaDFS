# bancassurance/premium_collection.py

import streamlit as st
from bancassurance.common import validate_customer_id, format_currency, show_receipt
from bancassurance.services.api_client import post_request, get_request
from bancassurance.services.permissions import can_collect_premium

# --- PREMIUM COLLECTION UI ---
def render_premium_collection_ui(officer):
    """
    Render the Premium Collection tab UI for Bancassurance Officers.

    Args:
        officer (dict): Officer session information (officer_id, name, role, branch_code)
    """

    st.info("Collect and record insurance premiums from customers")

    # --- Customer and Policy Details ---
    st.subheader("Customer Information")
    customer_id = st.text_input("Customer National ID / CIF", placeholder="e.g., 12345678")

    if customer_id and st.button("Fetch Active Policies"):
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            return

        try:
            # Fetch customer policies from backend
            policies = get_request(f"/bancassurance/customer-policies?customer_id={customer_id}")

            if not policies.get("data"):
                st.warning("No active policies found for this customer.")
                return

            st.session_state["policies"] = policies["data"]
            st.success(f"Fetched {len(policies['data'])} active policies.")

        except Exception as e:
            st.error(f"System Error: Could not fetch policies. {e}")
            return

    # --- Policy Selection ---
    if "policies" in st.session_state:
        st.subheader("Select Policy for Premium Payment")
        policy_options = [
            f"{p['policy_number']} - {p['policy_type']} - {format_currency(p['premium_due'])}"
            for p in st.session_state["policies"]
        ]
        selected_policy_index = st.selectbox("Select Policy", range(len(policy_options)), format_func=lambda i: policy_options[i])
        selected_policy = st.session_state["policies"][selected_policy_index]

        st.write(f"Premium Due: **{format_currency(selected_policy['premium_due'])}**")

        # --- Payment Amount ---
        payment_amount = st.number_input(
            "Payment Amount (KES)",
            min_value=50.0,
            step=50.0,
            value=selected_policy["premium_due"],
            format="%.2f"
        )

        payment_method = st.selectbox(
            "Payment Method",
            ["Cash", "Bank Transfer", "Mobile Payment"]
        )

        # --- Submission ---
        if st.button("Submit Premium Payment", type="primary"):
            # Permission check
            if not can_collect_premium(officer["role"], payment_amount):
                st.error("You are not authorized to collect this premium amount.")
                return

            payload = {
                "officer_id": officer["officer_id"],
                "branch_code": officer["branch_code"],
                "customer_id": customer_id,
                "policy_number": selected_policy["policy_number"],
                "payment_amount": payment_amount,
                "payment_method": payment_method
            }

            st.info("Processing premium payment...")

            try:
                response = post_request("/bancassurance/premium-collection", payload)

                if response.get("status") == "success":
                    st.success("✅ Premium payment recorded successfully!")
                    show_receipt("Premium Payment Receipt", response["data"])
                else:
                    st.error(f"❌ Payment failed: {response.get('message')}")
            except Exception as e:
                st.error(f"System Error: Could not connect to backend. {e}")
