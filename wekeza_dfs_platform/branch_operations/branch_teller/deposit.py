import streamlit as st
from services.api_client import post_request
from app import get_logged_in_teller
from utils.validators import validate_amount, validate_account_number
from utils.formatting import format_currency
from datetime import datetime
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from authorization_helper import submit_to_authorization_queue, check_authorization_thresholds

# -----------------------------------------------------------------------------
# CASH DEPOSIT UI
# -----------------------------------------------------------------------------
def render_cash_deposit_ui(teller: dict):
    """
    Renders the Cash Deposit UI for the teller.
    All deposits are routed through authorization queue for maker-checker approval.
    """

    st.subheader("💰 Cash Deposit")

    # -------------------------------
    # CUSTOMER & ACCOUNT DETAILS
    # -------------------------------
    account_no = st.text_input("Account Number")
    customer_id = st.text_input("Customer National ID")
    amount = st.number_input("Amount (KES)", min_value=50.0, step=100.0)
    source_of_funds = st.text_input("Source of Funds / Remarks", value="Cash Deposit")

    st.markdown("---")

    # -------------------------------
    # VALIDATION
    # -------------------------------
    if st.button("Submit Deposit", type="primary"):
        # Input validation
        if not validate_account_number(account_no):
            st.error("Invalid account number format.")
            return

        if not customer_id or len(customer_id.strip()) < 5:
            st.error("Please enter a valid Customer National ID.")
            return

        if not validate_amount(amount):
            st.error("Invalid amount. Must be greater than 0 and below teller limit.")
            return

        # -------------------------------
        # CHECK AUTHORIZATION REQUIREMENTS
        # -------------------------------
        auth_check = check_authorization_thresholds('CASH_DEPOSIT', amount, teller.get('role', 'teller'))
        
        # -------------------------------
        # BUILD OPERATION DATA
        # -------------------------------
        operation_data = {
            "account_no": account_no,
            "customer_id": customer_id,
            "amount": float(amount),
            "currency": "KES",
            "source_of_funds": source_of_funds,
            "transaction_date": datetime.now().isoformat(),
            "teller_id": teller["teller_id"],
            "branch_code": teller["branch_code"]
        }

        # -------------------------------
        # SUBMIT TO AUTHORIZATION QUEUE
        # -------------------------------
        with st.spinner("Processing deposit..."):
            try:
                result = submit_to_authorization_queue(
                    operation_type='CASH_DEPOSIT',
                    operation_data=operation_data,
                    maker_info=teller,
                    priority=auth_check.get('priority', 'MEDIUM')
                )
                
                if result['success']:
                    st.success("✅ Cash deposit submitted for approval!")
                    
                    # Show authorization info
                    if auth_check['requires_approval']:
                        st.warning(f"⚠️ **Supervisor Approval Required**")
                        st.info(f"**Reason:** {auth_check['reason']}")
                        st.info(f"**Priority:** {auth_check['priority']}")
                    else:
                        st.info("✅ **Auto-Approved** - Amount within your authorization limit")
                    
                    # Display receipt
                    st.markdown("### 🧾 Authorization Receipt")
                    st.code(f"""
WEKEZA BANK - CASH DEPOSIT AUTHORIZATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Queue ID: {result['queue_id']}
Teller: {teller['full_name']} ({teller['teller_id']})
Branch: {teller['branch_code']}

Customer ID: {customer_id}
Account: {account_no}
Amount: KES {amount:,.2f}
Source: {source_of_funds}

Status: {result['status']}
Priority: {auth_check.get('priority', 'MEDIUM')}

{auth_check['reason']}
                    """)
                    
                    # Show next steps
                    if auth_check['requires_approval']:
                        st.markdown("### 📋 Next Steps")
                        st.info("1. Transaction is queued for supervisor approval")
                        st.info("2. Supervisor will review and approve/reject")
                        st.info("3. Customer will be notified of final status")
                        st.info("4. Funds will be credited after approval")
                    else:
                        st.info("💰 Funds will be credited immediately")
                        
                else:
                    st.error(f"❌ Submission failed: {result['error']}")
                    
            except Exception as e:
                st.error(f"System error: {e}")
                return
Amount: {format_currency(amount)}
Teller: {teller['teller_id']}
Branch: {teller['branch_code']}
Remarks: {source_of_funds}
Status: {response['status']}
""", language="text")

            else:
                st.error(response.get("message", "Deposit failed."))
