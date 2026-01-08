# bancassurance/policy_sales.py

import streamlit as st
from bancassurance.common import validate_customer_id, format_currency, show_receipt
from bancassurance.services.api_client import post_request
from bancassurance.services.permissions import can_sell_policy

# --- POLICY SALES UI ---
def render_policy_sales_ui(officer):
    """
    Render the Policy Sales tab UI for Bancassurance Officers.

    Args:
        officer (dict): Officer session information (officer_id, name, role, branch_code)
    """

    st.info("Sell new insurance policies to customers")

    # --- Customer Details ---
    st.subheader("Customer Information")
    customer_id = st.text_input("Customer National ID / CIF", placeholder="e.g., 12345678")
    customer_name = st.text_input("Customer Name", placeholder="e.g., John Doe")

    # --- Policy Selection ---
    st.subheader("Policy Details")
    policy_type = st.selectbox(
        "Policy Type",
        ["Life Insurance", "Health Insurance", "Education Plan", "Pension Plan", "Investment Linked"]
    )
    coverage_amount = st.number_input(
        "Coverage Amount (KES)",
        min_value=1000,
        step=1000,
        format="%.2f"
    )

    # --- Premium Calculation ---
    st.subheader("Premium Calculation")
    # Simple example formula: premium = coverage * factor
    premium_factor = {
        "Life Insurance": 0.05,
        "Health Insurance": 0.03,
        "Education Plan": 0.04,
        "Pension Plan": 0.06,
        "Investment Linked": 0.07
    }
    premium_amount = coverage_amount * premium_factor[policy_type]
    st.write(f"Calculated Premium: **{format_currency(premium_amount)}**")

    # --- Validation & Submission ---
    if st.button("Submit Policy Sale", type="primary"):
        # Permission check
        if not can_sell_policy(officer["role"]):
            st.error("You are not authorized to sell insurance policies.")
            return

        # Customer ID validation
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID. Please check and try again.")
            return

        # Prepare payload
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "customer_id": customer_id,
            "customer_name": customer_name,
            "policy_type": policy_type,
            "coverage_amount": coverage_amount,
            "premium_amount": premium_amount
        }

        st.info("Processing policy sale...")

        try:
            # Call backend API
            response = post_request("/bancassurance/policy-sale", payload)

            if response.get("status") == "success":
                st.success("✅ Policy sale successful!")
                show_receipt("Insurance Policy Sale Receipt", response["data"])
            else:
                st.error(f"❌ Policy sale failed: {response.get('message')}")
        except Exception as e:
            st.error(f"System Error: Could not connect to backend. {e}")
