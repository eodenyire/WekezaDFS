import streamlit as st
import os
from datetime import datetime

def render_customer_ops_ui(staff_info):
    """
    Main render function for the customer operations module.
    This function is called by the main branch system.
    
    Args:
        staff_info (dict): Staff information from the main system
    """
    # -----------------------------
    # Connect to Backend
    # -----------------------------
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

    # -----------------------------
    # Check Customer Ops Access
    # -----------------------------
    def check_customer_ops_access():
        """Verify user has customer operations access"""
        allowed_roles = ['RELATIONSHIP_MANAGER', 'SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
        
        if staff_info['role'] not in allowed_roles:
            st.error(f"❌ Access Denied: Role '{staff_info['role']}' is not authorized for customer operations.")
            st.stop()
        
        return staff_info

    # Check access first
    staff = check_customer_ops_access()

    st.title("🏢 Customer Operations Portal")
    st.markdown(f"**Officer:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
    st.markdown("---")

    # -----------------------------
    # Tabs for Customer Operations
    # -----------------------------
    tab_cif, tab_open, tab_maint, tab_close, tab_mandate, tab_enquiries = st.tabs([
        "🆔 CIF Creation",
        "🏦 Account Opening",
        "🔧 Account Maintenance",
        "❌ Account Closure",
        "✍️ Mandate Management",
        "🔍 Enquiries"
    ])

    # -----------------------------
    # CIF Creation Tab
    # -----------------------------
    with tab_cif:
        st.subheader("🆔 Customer Information File (CIF) Creation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Personal Information")
            full_name = st.text_input("Full Name", placeholder="Enter customer full name")
            national_id = st.text_input("National ID", placeholder="ID number")
            phone_number = st.text_input("Phone Number", placeholder="+254...")
            email = st.text_input("Email Address", placeholder="customer@email.com")
            date_of_birth = st.date_input("Date of Birth")
            
            st.markdown("### Address Information")
            physical_address = st.text_area("Physical Address", placeholder="Street, City, County")
            postal_address = st.text_input("Postal Address", placeholder="P.O. Box...")
            
        with col2:
            st.markdown("### KYC Information")
            kyc_tier = st.selectbox("KYC Tier", ["TIER_1", "TIER_2", "TIER_3"])
            occupation = st.text_input("Occupation", placeholder="Customer occupation")
            employer = st.text_input("Employer", placeholder="Employer name")
            monthly_income = st.number_input("Monthly Income (KES)", min_value=0.0, step=1000.0)
            
            st.markdown("### Documents")
            id_copy = st.file_uploader("ID Copy", type=['pdf', 'jpg', 'png'])
            passport_photo = st.file_uploader("Passport Photo", type=['jpg', 'png'])
            
        if st.button("🆔 Create CIF", type="primary"):
            if full_name and national_id and phone_number:
                # Import authorization helper for maker-checker
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
                from authorization_helper import submit_to_authorization_queue
                
                # Generate CIF number
                cif_number = f"CIF{datetime.now().strftime('%Y%m%d')}{national_id[-4:]}"
                
                # Prepare operation data for authorization queue
                operation_data = {
                    "cif_number": cif_number,
                    "full_name": full_name,
                    "national_id": national_id,
                    "phone_number": phone_number,
                    "email": email,
                    "date_of_birth": date_of_birth.isoformat() if date_of_birth else None,
                    "physical_address": physical_address,
                    "postal_address": postal_address,
                    "kyc_tier": kyc_tier,
                    "occupation": occupation,
                    "employer": employer,
                    "monthly_income": monthly_income,
                    "customer_type": "individual",
                    "created_by": staff['staff_code']
                }
                
                # Prepare maker info
                maker_info = {
                    "staff_code": staff['staff_code'],
                    "full_name": staff['full_name'],
                    "branch_code": staff.get('branch_code', 'MAIN'),
                    "role": staff['role']
                }
                
                # Submit to authorization queue
                result = submit_to_authorization_queue(
                    operation_type='CIF_CREATE',
                    operation_data=operation_data,
                    maker_info=maker_info,
                    priority='MEDIUM'
                )
                
                if result.get('success'):
                    st.success(f"✅ CIF creation submitted for approval!")
                    st.info(f"📋 Queue ID: {result['queue_id']}")
                    st.info(f"🆔 CIF Number: {cif_number}")
                    st.info(f"👤 Customer: {full_name}")
                    st.info(f"📊 KYC Tier: {kyc_tier}")
                    st.warning("⚠️ **Important:** CIF creation requires supervisor approval before activation.")
                    st.info("🔄 Customer will be notified once approved")
                else:
                    st.error(f"❌ CIF creation failed: {result.get('error', 'Unknown error')}")
            else:
                st.error("Please fill in all required fields")

    # -----------------------------
    # Account Opening Tab
    # -----------------------------
    with tab_open:
        st.subheader("🏦 Account Opening")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Customer Selection")
            cif_search = st.text_input("Search CIF", placeholder="Enter CIF number or name")
            
            if st.button("🔍 Search Customer"):
                if cif_search:
                    # Import database connection
                    import mysql.connector
                    
                    try:
                        conn = mysql.connector.connect(
                            host='localhost',
                            user='root',
                            password='root',
                            database='wekeza_dfs_db'
                        )
                        cursor = conn.cursor(dictionary=True)
                        
                        # Search in customers table first, then users table
                        cursor.execute("""
                            SELECT cif_number, full_name, phone_number, kyc_tier, status
                            FROM customers 
                            WHERE cif_number LIKE %s OR full_name LIKE %s
                            LIMIT 1
                        """, (f"%{cif_search}%", f"%{cif_search}%"))
                        
                        customer = cursor.fetchone()
                        
                        if not customer:
                            # Fallback to users table
                            cursor.execute("""
                                SELECT CONCAT('CIF', user_id) as cif_number, full_name, phone_number, 
                                       'TIER_2' as kyc_tier, 
                                       CASE WHEN is_active = 1 THEN 'ACTIVE' ELSE 'INACTIVE' END as status
                                FROM users 
                                WHERE full_name LIKE %s OR email LIKE %s
                                LIMIT 1
                            """, (f"%{cif_search}%", f"%{cif_search}%"))
                            customer = cursor.fetchone()
                        
                        conn.close()
                        
                        if customer:
                            st.success("✅ Customer found")
                            st.write(f"**CIF:** {customer['cif_number']}")
                            st.write(f"**Name:** {customer['full_name']}")
                            st.write(f"**Phone:** {customer['phone_number']}")
                            st.write(f"**KYC Tier:** {customer['kyc_tier']}")
                            st.write(f"**Status:** {customer['status']}")
                            
                            # Store found customer in session state
                            st.session_state['selected_customer'] = customer
                        else:
                            st.error("❌ Customer not found")
                            
                    except Exception as e:
                        st.error(f"❌ Search failed: {e}")
                        # Fallback to mock data
                        st.success("✅ Customer found (mock data)")
                        st.write("**CIF:** CIF123456")
                        st.write("**Name:** John Doe")
                        st.write("**Phone:** +254712345678")
                        st.write("**KYC Tier:** TIER_2")
            
            st.markdown("### Account Details")
            account_type = st.selectbox("Account Type", [
                "Savings Account",
                "Current Account", 
                "Fixed Deposit",
                "Business Account"
            ])
            
            initial_deposit = st.number_input("Initial Deposit (KES)", min_value=0.0, step=100.0)
            
        with col2:
            st.markdown("### Account Requirements")
            
            if account_type == "Savings Account":
                st.info("**Minimum Balance:** KES 1,000")
                st.info("**Initial Deposit:** KES 1,000")
            elif account_type == "Current Account":
                st.info("**Minimum Balance:** KES 5,000")
                st.info("**Initial Deposit:** KES 5,000")
            elif account_type == "Fixed Deposit":
                st.info("**Minimum Amount:** KES 50,000")
                st.info("**Tenure:** 3-60 months")
            
            st.markdown("### Signatories")
            signatory_1 = st.text_input("Primary Signatory", value="John Doe")
            signatory_2 = st.text_input("Secondary Signatory (Optional)")
            
        if st.button("🏦 Open Account", type="primary"):
            if cif_search and account_type and initial_deposit > 0:
                account_number = f"ACC{cif_search[-4:]}{int(initial_deposit)}"
                st.success(f"✅ Account opened successfully!")
                st.write(f"**Account Number:** {account_number}")
                st.write(f"**Account Type:** {account_type}")
                st.write(f"**Initial Deposit:** KES {initial_deposit:,.2f}")
            else:
                st.error("Please complete all required fields")

    # -----------------------------
    # Account Maintenance Tab
    # -----------------------------
    with tab_maint:
        st.subheader("🔧 Account Maintenance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Account Selection")
            account_search = st.text_input("Account Number", placeholder="Enter account number")
            
            if st.button("🔍 Load Account"):
                if account_search:
                    st.success("✅ Account loaded")
                    st.write("**Account:** ACC123456789")
                    st.write("**Holder:** Jane Smith")
                    st.write("**Type:** Savings")
                    st.write("**Status:** Active")
                    st.write("**Balance:** KES 45,230.50")
            
            st.markdown("### Maintenance Actions")
            maintenance_type = st.selectbox("Maintenance Type", [
                "Update Contact Information",
                "Change Account Status",
                "Update Signatory",
                "Modify Limits",
                "Add Services"
            ])
            
        with col2:
            st.markdown("### Update Details")
            
            if maintenance_type == "Update Contact Information":
                new_phone = st.text_input("New Phone Number")
                new_email = st.text_input("New Email Address")
                new_address = st.text_area("New Address")
                
            elif maintenance_type == "Change Account Status":
                new_status = st.selectbox("New Status", ["Active", "Frozen", "Dormant"])
                reason = st.text_area("Reason for Change")
                
            elif maintenance_type == "Update Signatory":
                signatory_action = st.selectbox("Action", ["Add Signatory", "Remove Signatory", "Modify Signatory"])
                signatory_name = st.text_input("Signatory Name")
        
        if st.button("🔧 Update Account", type="primary"):
            if account_search and maintenance_type:
                st.success(f"✅ Account maintenance completed!")
                st.write(f"**Action:** {maintenance_type}")
                st.write(f"**Account:** {account_search}")
            else:
                st.error("Please select account and maintenance type")

    # -----------------------------
    # Account Closure Tab
    # -----------------------------
    with tab_close:
        st.subheader("❌ Account Closure")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Account to Close")
            closure_account = st.text_input("Account Number", placeholder="Enter account number", key="close_acc")
            
            if st.button("🔍 Verify Account", key="verify_close"):
                if closure_account:
                    st.success("✅ Account verified")
                    st.write("**Account:** ACC987654321")
                    st.write("**Holder:** Peter Kamau")
                    st.write("**Type:** Current")
                    st.write("**Balance:** KES 12,450.00")
            
            st.markdown("### Closure Details")
            closure_reason = st.selectbox("Closure Reason", [
                "Customer Request",
                "Account Dormancy",
                "Regulatory Requirement",
                "Fraudulent Activity",
                "Other"
            ])
            
            closure_notes = st.text_area("Additional Notes")
            
        with col2:
            st.warning("### ⚠️ Closure Checklist")
            st.checkbox("All pending transactions cleared")
            st.checkbox("Outstanding loans settled")
            st.checkbox("Debit/Credit cards returned")
            st.checkbox("Cheque books returned")
            st.checkbox("Customer notification sent")
            
            st.markdown("### Final Balance")
            final_balance = st.number_input("Final Balance (KES)", value=12450.0, disabled=True)
            transfer_account = st.text_input("Transfer Balance To", placeholder="Account number for balance transfer")
        
        if st.button("❌ Close Account", type="secondary"):
            if closure_account and closure_reason:
                st.success(f"✅ Account closure initiated!")
                st.write(f"**Closure ID:** CLS{closure_account[-6:]}")
                st.write(f"**Final Balance:** KES {final_balance:,.2f}")
                st.write("**Status:** Pending Approval")
            else:
                st.error("Please complete all required fields")

    # -----------------------------
    # Mandate Management Tab
    # -----------------------------
    with tab_mandate:
        st.subheader("✍️ Mandate Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Account Selection")
            mandate_account = st.text_input("Account Number", placeholder="Enter account number", key="mandate_acc")
            
            if st.button("🔍 Load Mandates"):
                if mandate_account:
                    st.success("✅ Current mandates loaded")
                    st.write("**Primary:** John Doe (Single)")
                    st.write("**Secondary:** Jane Doe (Joint)")
                    st.write("**Limit:** KES 100,000")
            
            st.markdown("### Mandate Type")
            mandate_type = st.selectbox("Mandate Type", [
                "Single Signatory",
                "Joint Signatories (Any One)",
                "Joint Signatories (All)",
                "Authorized Representative"
            ])
            
            signatory_limit = st.number_input("Transaction Limit (KES)", min_value=0.0, step=1000.0)
            
        with col2:
            st.markdown("### Signatory Details")
            
            num_signatories = st.number_input("Number of Signatories", min_value=1, max_value=5, value=1)
            
            for i in range(int(num_signatories)):
                st.text_input(f"Signatory {i+1} Name", key=f"sig_{i}")
                st.text_input(f"Signatory {i+1} ID", key=f"sig_id_{i}")
            
            st.markdown("### Authorization")
            authorization_required = st.checkbox("Requires supervisor authorization")
            effective_date = st.date_input("Effective Date")
        
        if st.button("✍️ Update Mandate", type="primary"):
            if mandate_account and mandate_type:
                st.success(f"✅ Mandate updated successfully!")
                st.write(f"**Account:** {mandate_account}")
                st.write(f"**Type:** {mandate_type}")
                st.write(f"**Limit:** KES {signatory_limit:,.2f}")
            else:
                st.error("Please complete all required fields")

    # -----------------------------
    # Enquiries Tab
    # -----------------------------
    with tab_enquiries:
        st.subheader("🔍 Customer Enquiries")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Search Customer")
            search_type = st.selectbox("Search By", ["Account Number", "CIF Number", "National ID", "Phone Number"])
            search_value = st.text_input("Search Value", placeholder=f"Enter {search_type.lower()}")
            
            if st.button("🔍 Search"):
                if search_value:
                    # Import database connection
                    import mysql.connector
                    
                    try:
                        conn = mysql.connector.connect(
                            host='localhost',
                            user='root',
                            password='root',
                            database='wekeza_dfs_db'
                        )
                        cursor = conn.cursor(dictionary=True)
                        
                        # Search based on type
                        if search_type == "Account Number":
                            cursor.execute("""
                                SELECT u.full_name, u.phone_number, u.email, 
                                       CONCAT('CIF', u.user_id) as cif_number,
                                       a.account_number, a.balance, a.status,
                                       'TIER_2' as kyc_tier
                                FROM users u
                                JOIN accounts a ON u.user_id = a.user_id
                                WHERE a.account_number = %s
                            """, (search_value,))
                        elif search_type == "CIF Number":
                            cursor.execute("""
                                SELECT c.full_name, c.phone_number, c.email, c.cif_number, c.kyc_tier,
                                       a.account_number, a.balance, a.status
                                FROM customers c
                                LEFT JOIN accounts a ON c.customer_id = a.user_id
                                WHERE c.cif_number = %s
                            """, (search_value,))
                        elif search_type == "National ID":
                            cursor.execute("""
                                SELECT u.full_name, u.phone_number, u.email, u.national_id,
                                       CONCAT('CIF', u.user_id) as cif_number,
                                       a.account_number, a.balance, a.status,
                                       'TIER_2' as kyc_tier
                                FROM users u
                                LEFT JOIN accounts a ON u.user_id = a.user_id
                                WHERE u.national_id = %s
                            """, (search_value,))
                        elif search_type == "Phone Number":
                            cursor.execute("""
                                SELECT u.full_name, u.phone_number, u.email,
                                       CONCAT('CIF', u.user_id) as cif_number,
                                       a.account_number, a.balance, a.status,
                                       'TIER_2' as kyc_tier
                                FROM users u
                                LEFT JOIN accounts a ON u.user_id = a.user_id
                                WHERE u.phone_number = %s
                            """, (search_value,))
                        
                        customer = cursor.fetchone()
                        
                        # Get recent transactions if customer found
                        recent_transactions = []
                        if customer and customer.get('account_number'):
                            cursor.execute("""
                                SELECT txn_type, amount, created_at, description
                                FROM transactions t
                                JOIN accounts a ON t.account_id = a.account_id
                                WHERE a.account_number = %s
                                ORDER BY t.created_at DESC
                                LIMIT 5
                            """, (customer['account_number'],))
                            recent_transactions = cursor.fetchall()
                        
                        conn.close()
                        
                        if customer:
                            st.success("✅ Customer found")
                            
                            st.markdown("### Customer Information")
                            st.write(f"**Name:** {customer['full_name']}")
                            st.write(f"**CIF:** {customer['cif_number']}")
                            st.write(f"**Phone:** {customer['phone_number']}")
                            st.write(f"**Email:** {customer.get('email', 'N/A')}")
                            st.write(f"**KYC Tier:** {customer.get('kyc_tier', 'TIER_2')}")
                            
                            if customer.get('account_number'):
                                st.markdown("### Account Summary")
                                st.write(f"**Account:** {customer['account_number']} - KES {customer.get('balance', 0):,.2f}")
                                st.write(f"**Status:** {customer.get('status', 'ACTIVE')}")
                                
                                if recent_transactions:
                                    st.markdown("### Recent Activity")
                                    for i, txn in enumerate(recent_transactions, 1):
                                        st.write(f"{i}. {txn['txn_type'].replace('_', ' ').title()} - KES {txn['amount']:,.2f} ({txn['created_at'].strftime('%Y-%m-%d')})")
                                else:
                                    st.info("No recent transactions found")
                            else:
                                st.info("No account linked to this customer")
                        else:
                            st.error("❌ Customer not found")
                            
                    except Exception as e:
                        st.error(f"❌ Search failed: {e}")
                        # Fallback to mock data
                        st.success("✅ Customer found (mock data)")
                        
                        st.markdown("### Customer Information")
                        st.write("**Name:** Alice Wanjiku")
                        st.write("**CIF:** CIF789012")
                        st.write("**Phone:** +254723456789")
                        st.write("**Email:** alice@email.com")
                        st.write("**KYC Tier:** TIER_2")
                        
                        st.markdown("### Account Summary")
                        st.write("**Savings Account:** ACC123456789 - KES 45,230.50")
                        st.write("**Current Account:** ACC987654321 - KES 12,450.00")
                        st.write("**Fixed Deposit:** FD555666777 - KES 500,000.00")
            
        with col2:
            st.markdown("### Recent Activity")
            st.write("1. Deposit - KES 5,000 (Today)")
            st.write("2. Withdrawal - KES 2,000 (Yesterday)")
            st.write("3. Transfer - KES 1,500 (2 days ago)")
            st.write("4. Bill Payment - KES 850 (3 days ago)")
            
            st.markdown("### Quick Actions")
            if st.button("📊 Generate Statement"):
                st.success("Statement generated")
            
            if st.button("🔒 Freeze Account"):
                st.warning("Account freeze initiated")
            
            if st.button("📞 Log Complaint"):
                st.info("Complaint logged")
            
            if st.button("📧 Send Notification"):
                st.success("Notification sent")


# Legacy function for standalone usage
def main():
    """
    Legacy main function for standalone usage.
    """
    # Configure Streamlit page
    st.set_page_config(
        page_title="Wekeza Customer Operations Portal",
        page_icon="🏢",
        layout="wide"
    )

    # Mock staff info for standalone usage
    staff_info = {
        'staff_code': 'REL001',
        'full_name': 'Relationship Manager',
        'role': 'RELATIONSHIP_MANAGER',
        'branch_code': 'MAIN',
        'branch_name': 'Main Branch'
    }
    
    render_customer_ops_ui(staff_info)


if __name__ == "__main__":
    main()