import streamlit as st
from .services.api_client import get_request
from .services.permissions import can_perform_action
from .common import validate_account_number, validate_customer_id

# -----------------------------------------------------------------------------
# Render Enquiries UI
# -----------------------------------------------------------------------------
def render_enquiries_ui(officer: dict):
    """
    Streamlit UI for checking balances, KYC status, and account details
    """
    st.subheader("🔍 Customer Enquiries")

    # Role-based access check
    if not can_perform_action(officer["role"], "enquiries"):
        st.error("Access Denied: You are not authorized to perform enquiries.")
        return

    # -----------------------------
    # Enquiry Form
    # -----------------------------
    with st.form(key="enquiry_form"):
        customer_id = st.text_input("Customer National ID / CIF")
        account_no = st.text_input("Account Number (Optional)")
        submit_btn = st.form_submit_button("Fetch Details")

    # -----------------------------
    # Handle Form Submission
    # -----------------------------
    if submit_btn:
        # Validate inputs
        if not validate_customer_id(customer_id):
            st.error("Invalid Customer ID")
            return
        if account_no and not validate_account_number(account_no):
            st.error("Invalid Account Number")
            return

        # Prepare query parameters
        params = {
            "customer_id": customer_id,
            "account_no": account_no.strip() if account_no else None,
            "branch_code": officer["branch_code"]
        }

        # -----------------------------
        # Call Backend API
        # -----------------------------
        with st.spinner("Fetching Customer Details..."):
            try:
                response = get_request("/customer/enquiry", params=params)

                # Display results
                st.success("✅ Customer Details Retrieved Successfully")
                st.markdown("### Customer Info")
                st.write({
                    "Customer ID": response.get("customer_id"),
                    "Full Name": response.get("full_name"),
                    "Date of Birth": response.get("dob"),
                    "Phone": response.get("phone"),
                    "Email": response.get("email"),
                    "Address": response.get("address"),
                    "Nationality": response.get("nationality"),
                    "KYC Status": response.get("kyc_status"),
                })

                # Display account info if available
                accounts = response.get("accounts", [])
                if accounts:
                    st.markdown("### Accounts")
                    for acc in accounts:
                        st.write({
                            "Account Number": acc.get("account_no"),
                            "Account Type": acc.get("account_type"),
                            "Balance": f"KES {acc.get('balance', 0):,.2f}",
                            "Status": acc.get("status")
                        })
                else:
                    st.info("No accounts found for this customer.")

            except Exception as e:
                st.error(f"❌ Failed to fetch customer details: {e}")
