import streamlit as st
from datetime import datetime
from .services.api_client import post_request
from .services.permissions import can_perform_action
from .common import validate_customer_id, validate_amount, show_receipt
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from authorization_helper import submit_to_authorization_queue, check_authorization_thresholds

# -----------------------------------------------------------------------------
# Render CIF Creation UI
# -----------------------------------------------------------------------------
def render_cif_ui(officer: dict):
    """
    Streamlit UI for creating a Customer Information File (CIF)
    All CIF creations require supervisor approval (maker-checker)
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
        customer_type = st.selectbox("Customer Type", ["Individual", "Business"])
        submit_btn = st.form_submit_button("Submit CIF for Approval")

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

        # Prepare operation data
        operation_data = {
            "customer_id": customer_id,
            "full_name": full_name.strip(),
            "dob": dob.strftime("%Y-%m-%d"),
            "phone": phone.strip(),
            "email": email.strip(),
            "address": address.strip(),
            "nationality": nationality,
            "id_type": id_type,
            "customer_type": customer_type.lower(),
            "officer_id": officer["officer_id"],
            "branch_code": officer["branch_code"],
            "created_at": datetime.now().isoformat()
        }

        # -----------------------------
        # Submit to Authorization Queue
        # -----------------------------
        with st.spinner("Submitting CIF for approval..."):
            try:
                result = submit_to_authorization_queue(
                    operation_type='CIF_CREATE',
                    operation_data=operation_data,
                    maker_info=officer,
                    priority='HIGH'  # CIF creation always requires approval
                )
                
                if result['success']:
                    st.success("✅ CIF creation submitted for supervisor approval!")
                    
                    # Display authorization receipt
                    st.markdown("### 🧾 CIF Authorization Receipt")
                    st.code(f"""
WEKEZA BANK - CIF CREATION AUTHORIZATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Queue ID: {result['queue_id']}
Officer: {officer['full_name']} ({officer['officer_id']})
Branch: {officer['branch_code']}

Customer Details:
National ID: {customer_id}
Full Name: {full_name}
Phone: {phone}
Email: {email}
Customer Type: {customer_type}

Status: {result['status']}
Priority: HIGH (Always requires supervisor approval)

IMPORTANT: CIF creation requires supervisor approval for compliance.
                    """)
                    
                    # Show next steps
                    st.markdown("### 📋 Next Steps")
                    st.info("1. CIF is queued for supervisor approval")
                    st.info("2. Supervisor will review customer details and KYC documents")
                    st.info("3. Upon approval, CIF number will be generated")
                    st.info("4. Customer can then proceed with account opening")
                    
                    st.warning("⚠️ **Compliance Note:** All CIF creations require supervisor approval to ensure proper KYC compliance and risk management.")
                        
                else:
                    st.error(f"❌ CIF submission failed: {result['error']}")
                    
            except Exception as e:
                st.error(f"System error: {e}")
                return
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
