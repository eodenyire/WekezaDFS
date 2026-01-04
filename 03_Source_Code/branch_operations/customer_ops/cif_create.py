import streamlit as st
from datetime import datetime
from .services.api_client import post_request
from .services.permissions import can_perform_action
from .common import validate_customer_id, validate_amount, show_receipt

# -----------------------------------------------------------------------------
# Render CIF Creation UI
# -----------------------------------------------------------------------------
def render_cif_ui(officer: dict):
    """
    Streamlit UI for creating a Customer Information File (CIF)
    """
    st.subheader("🆔 CIF Creation (KYC Onboarding)")

    # Role-based access check
    if not can_perform_action(officer["role"], "cif_create"):
        st.error("Access Denied: You are not authorized to create CIFs.")
        return

    # -----------------------------
    # Customer Details Form
    # -----------------------------
    with st.form(key="cif_form"):
        customer_id = st.text_input("Customer National ID", placeholder="e.g., 12345678")
        full_name = st.text_input("Full Name")
        dob = st.date_input("Date of Birth")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email Address")
        address = st.text_area("Residential Address")
        nationality = st.selectbox("Nationality", ["Kenyan", "Other"])
        id_type = st.selectbox("ID Type", ["National ID", "Passport", "Other"])
        submit_btn = st.form_submit_button("Create CIF")

    # -----------------------------
    # Handle Form Submission
    # -----------------------------
    if submit_btn:
        # Validate inputs
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            return
        if not full_name.strip():
            st.error("Full Name is required")
            return
        if not phone.strip():
            st.error("Phone Number is required")
            return
        if not address.strip():
            st.error("Residential Address is required")
            return

        # Prepare payload
        payload = {
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "customer_id": customer_id,
            "full_name": full_name.strip(),
            "dob": dob.strftime("%Y-%m-%d"),
            "phone": phone.strip(),
            "email": email.strip(),
            "address": address.strip(),
            "nationality": nationality,
            "id_type": id_type,
            "created_at": datetime.now().isoformat()
        }

        # -----------------------------
        # Call Backend API
        # -----------------------------
        with st.spinner("Submitting CIF..."):
            try:
                response = post_request("/customer/cif", payload)
                # Show success receipt
                show_receipt(
                    "✅ CIF Creation Successful",
                    {
                        "Customer ID": customer_id,
                        "Full Name": full_name,
                        "Branch": officer["branch_code"],
                        "Created By": officer["officer_id"],
                        "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )
            except Exception as e:
                st.error(f"❌ Failed to create CIF: {e}")
