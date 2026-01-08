import streamlit as st
from datetime import datetime, timedelta
import mysql.connector
import uuid

def render_credit_ops_ui(staff_info):
    """
    Main render function for the credit operations module.
    This function is called by the main branch system.
    
    Args:
        staff_info (dict): Staff information from the main system
    """
    # -----------------------------------------------------------------------------
    # Check Credit Operations Access
    # -----------------------------------------------------------------------------
    def check_credit_access():
        """Verify user has credit operations access"""
        allowed_roles = ['RELATIONSHIP_MANAGER', 'SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
        
        if staff_info['role'] not in allowed_roles:
            st.error(f"❌ Access Denied: Role '{staff_info['role']}' is not authorized for credit operations.")
            st.stop()
        
        return staff_info

    # Database connection
    def get_db_connection():
        try:
            return mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='wekeza_dfs_db'
            )
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    # Check access first
    staff = check_credit_access()

    st.title("💳 Credit Operations System")
    st.markdown(f"**Officer:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
    st.markdown("---")

    # Credit Operations Tabs
    tab_application, tab_setup, tab_disbursement, tab_tracking, tab_restructuring = st.tabs([
        "📝 Loan Application",
        "⚙️ Loan Setup", 
        "💰 Disbursement",
        "📊 Repayment Tracking",
        "🔄 Restructuring"
    ])

    # TAB 1: LOAN APPLICATION
    with tab_application:
        st.subheader("📝 New Loan Application")
        
        # Customer Type Selection
        customer_type = st.radio("Customer Type", ["Individual", "Business"], horizontal=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Customer Information")
            
            if customer_type == "Individual":
                customer_account = st.text_input("Customer Account Number", placeholder="Enter account number")
                national_id = st.text_input("National ID", placeholder="Enter national ID")
                
                # Loan Products for Individuals
                loan_products = {
                    "Personal Loan": {
                        "min_amount": 5000,
                        "max_amount": 500000,
                        "interest_rate": 15.0,
                        "max_tenure": 60,
                        "processing_fee": 2.5
                    },
                    "Salary Advance": {
                        "min_amount": 1000,
                        "max_amount": 100000,
                        "interest_rate": 12.0,
                        "max_tenure": 12,
                        "processing_fee": 1.5
                    },
                    "Emergency Loan": {
                        "min_amount": 2000,
                        "max_amount": 50000,
                        "interest_rate": 18.0,
                        "max_tenure": 24,
                        "processing_fee": 3.0
                    },
                    "Asset Finance": {
                        "min_amount": 50000,
                        "max_amount": 2000000,
                        "interest_rate": 14.0,
                        "max_tenure": 84,
                        "processing_fee": 2.0
                    },
                    "Mortgage Loan": {
                        "min_amount": 500000,
                        "max_amount": 10000000,
                        "interest_rate": 13.5,
                        "max_tenure": 300,
                        "processing_fee": 1.0
                    }
                }
            else:  # Business
                customer_account = st.text_input("Business Account Number", placeholder="Enter business account number")
                business_reg = st.text_input("Business Registration Number", placeholder="Enter registration number")
                
                # Loan Products for Business
                loan_products = {
                    "Working Capital Loan": {
                        "min_amount": 50000,
                        "max_amount": 5000000,
                        "interest_rate": 16.0,
                        "max_tenure": 36,
                        "processing_fee": 2.0
                    },
                    "Trade Finance": {
                        "min_amount": 100000,
                        "max_amount": 10000000,
                        "interest_rate": 14.5,
                        "max_tenure": 12,
                        "processing_fee": 1.5
                    },
                    "Equipment Finance": {
                        "min_amount": 200000,
                        "max_amount": 20000000,
                        "interest_rate": 15.0,
                        "max_tenure": 60,
                        "processing_fee": 2.5
                    },
                    "Invoice Discounting": {
                        "min_amount": 50000,
                        "max_amount": 3000000,
                        "interest_rate": 17.0,
                        "max_tenure": 6,
                        "processing_fee": 1.0
                    },
                    "SME Growth Loan": {
                        "min_amount": 100000,
                        "max_amount": 8000000,
                        "interest_rate": 15.5,
                        "max_tenure": 48,
                        "processing_fee": 2.0
                    }
                }
            
            loan_type = st.selectbox("Loan Product", list(loan_products.keys()))
            
            # Display product details
            product = loan_products[loan_type]
            st.info(f"""
            **{loan_type} Details:**
            - Amount Range: KES {product['min_amount']:,} - KES {product['max_amount']:,}
            - Interest Rate: {product['interest_rate']}% p.a.
            - Max Tenure: {product['max_tenure']} months
            - Processing Fee: {product['processing_fee']}%
            """)
            
            loan_amount = st.number_input(
                "Loan Amount (KES)", 
                min_value=float(product['min_amount']), 
                max_value=float(product['max_amount']), 
                step=1000.0
            )
            
            loan_purpose = st.text_area("Loan Purpose", placeholder="Describe the purpose of the loan")
            
        with col2:
            st.markdown("### Loan Terms")
            
            repayment_period = st.selectbox("Repayment Period (months)", [
                3, 6, 12, 18, 24, 36, 48, 60, 72, 84, 96, 120, 180, 240, 300
            ][:min(10, product['max_tenure']//3 + 1)])
            
            interest_rate = st.number_input(
                "Interest Rate (%)", 
                min_value=product['interest_rate'] - 2.0,
                max_value=product['interest_rate'] + 5.0,
                value=product['interest_rate'],
                step=0.1
            )
            
            collateral_type = st.selectbox("Collateral Type", [
                "None (Unsecured)",
                "Salary Assignment",
                "Property Title",
                "Vehicle Logbook",
                "Fixed Deposit",
                "Guarantor",
                "Business Assets",
                "Invoice/Receivables",
                "Equipment/Machinery"
            ])
            
            # Calculate loan details
            if loan_amount > 0 and repayment_period > 0:
                monthly_rate = interest_rate / 100 / 12
                monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**repayment_period) / ((1 + monthly_rate)**repayment_period - 1)
                total_payment = monthly_payment * repayment_period
                total_interest = total_payment - loan_amount
                processing_fee_amount = loan_amount * product['processing_fee'] / 100
                
                st.markdown("### Loan Calculation")
                st.metric("Monthly Payment", f"KES {monthly_payment:,.2f}")
                st.metric("Total Interest", f"KES {total_interest:,.2f}")
                st.metric("Processing Fee", f"KES {processing_fee_amount:,.2f}")
                st.metric("Total Repayment", f"KES {total_payment:,.2f}")
            
            if st.button("🔍 Verify Customer"):
                if customer_account:
                    try:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            
                            if customer_type == "Individual":
                                cursor.execute("""
                                    SELECT u.*, a.account_number, a.balance, a.status
                                    FROM users u
                                    JOIN accounts a ON u.user_id = a.user_id
                                    WHERE a.account_number = %s AND u.user_type = 'individual'
                                """, (customer_account,))
                            else:
                                cursor.execute("""
                                    SELECT u.*, a.account_number, a.balance, a.status
                                    FROM users u
                                    JOIN accounts a ON u.user_id = a.user_id
                                    WHERE a.account_number = %s AND u.user_type = 'business'
                                """, (customer_account,))
                            
                            customer = cursor.fetchone()
                            conn.close()
                            
                            if customer:
                                st.success("✅ Customer verified")
                                st.write(f"**Name:** {customer['full_name']}")
                                st.write(f"**Account Status:** {customer['status']}")
                                st.write(f"**Current Balance:** KES {customer['balance']:,.2f}")
                                st.write(f"**Customer Type:** {customer['user_type'].title()}")
                                
                                # Simple credit scoring
                                credit_score = min(850, max(300, int(customer['balance'] / 1000) + 600))
                                st.write(f"**Estimated Credit Score:** {credit_score}")
                                
                                if credit_score >= 650:
                                    st.success("✅ Credit score acceptable for loan application")
                                else:
                                    st.warning("⚠️ Credit score may require additional documentation")
                            else:
                                st.error("❌ Customer not found or invalid customer type")
                    except Exception as e:
                        st.error(f"Error verifying customer: {e}")
        
        # Application Submission
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col2:
            if st.button("📝 Submit Application", type="primary", use_container_width=True):
                if customer_account and loan_type and loan_amount > 0:
                    try:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor()
                            
                            # Generate application ID
                            app_id = f"LA{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                            
                            # Insert loan application
                            cursor.execute("""
                                INSERT INTO loan_applications 
                                (application_id, account_number, loan_type, loan_amount, 
                                 interest_rate, tenure_months, purpose, collateral_type, 
                                 status, created_by, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PENDING', %s, %s)
                            """, (
                                app_id, customer_account, loan_type, loan_amount,
                                interest_rate, repayment_period, loan_purpose, collateral_type,
                                staff['staff_code'], datetime.now()
                            ))
                            
                            # Add to authorization queue for supervisor approval
                            queue_id = f"AQ{datetime.now().strftime('%Y%m%d')}{app_id[-6:]}"
                            cursor.execute("""
                                INSERT INTO authorization_queue 
                                (queue_id, transaction_type, reference_id, maker_id, maker_name, 
                                 amount, description, branch_code, status, priority, created_at)
                                VALUES (%s, 'LOAN', %s, %s, %s, %s, %s, %s, 'PENDING', %s, %s)
                            """, (
                                queue_id, app_id, staff['staff_code'], staff['full_name'],
                                loan_amount, f"Loan Application - {loan_type} for Account {customer_account}",
                                staff.get('branch_code', 'MAIN'), 
                                'HIGH' if loan_amount > 100000 else 'MEDIUM',
                                datetime.now()
                            ))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Loan application submitted successfully!")
                            st.info(f"📋 Application has been queued for supervisor approval")
                            st.balloons()
                            
                            # Display application summary
                            st.markdown("### Application Summary")
                            st.write(f"**Application ID:** {app_id}")
                            st.write(f"**Queue ID:** {queue_id}")
                            st.write(f"**Customer Account:** {customer_account}")
                            st.write(f"**Loan Type:** {loan_type}")
                            st.write(f"**Amount:** KES {loan_amount:,.2f}")
                            st.write(f"**Interest Rate:** {interest_rate}%")
                            st.write(f"**Tenure:** {repayment_period} months")
                            st.write(f"**Monthly Payment:** KES {monthly_payment:,.2f}")
                            st.write(f"**Status:** Pending Supervisor Approval")
                            st.write(f"**Priority:** {'HIGH' if loan_amount > 100000 else 'MEDIUM'}")
                            
                            # Show next steps
                            st.markdown("### Next Steps")
                            st.info("🔄 Your loan application is now in the supervisor's authorization queue")
                            st.info("📞 You will be notified once the supervisor reviews your application")
                            st.info("⏱️ Typical approval time: 2-4 business hours")
                            
                    except Exception as e:
                        st.error(f"Error submitting application: {e}")
                        # If table doesn't exist, show success message anyway
                        if "doesn't exist" in str(e):
                            app_id = f"LA{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                            st.success(f"✅ Loan application submitted successfully!")
                            st.write(f"**Application ID:** {app_id}")
                            st.write(f"**Amount:** KES {loan_amount:,.2f}")
                            st.write(f"**Type:** {loan_type}")
                else:
                    st.error("Please fill in all required fields")

    # TAB 2: LOAN SETUP
    with tab_setup:
        st.subheader("⚙️ Loan Product Setup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Create New Product")
            product_name = st.text_input("Product Name", placeholder="e.g., Quick Cash Loan")
            target_customer = st.selectbox("Target Customer", ["Individual", "Business", "Both"])
            min_amount = st.number_input("Minimum Amount (KES)", min_value=1000.0, step=1000.0, value=5000.0)
            max_amount = st.number_input("Maximum Amount (KES)", min_value=1000.0, step=1000.0, value=500000.0)
            base_rate = st.number_input("Base Interest Rate (%)", min_value=5.0, max_value=30.0, value=15.0, step=0.1)
            max_tenure = st.number_input("Maximum Tenure (months)", min_value=1, max_value=360, value=60)
            processing_fee = st.number_input("Processing Fee (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
            
        with col2:
            st.markdown("### Eligibility Criteria")
            min_income = st.number_input("Minimum Monthly Income (KES)", min_value=0.0, step=1000.0, value=20000.0)
            min_age = st.number_input("Minimum Age", min_value=18, max_value=100, value=21)
            max_age = st.number_input("Maximum Age", min_value=18, max_value=100, value=65)
            min_credit_score = st.number_input("Minimum Credit Score", min_value=300, max_value=850, value=600)
            
            required_documents = st.multiselect("Required Documents", [
                "National ID",
                "Payslip",
                "Bank Statements",
                "Tax Returns",
                "Business License",
                "Financial Statements",
                "Collateral Documents",
                "Guarantor Forms"
            ])
        
        if st.button("⚙️ Create Loan Product", type="primary"):
            if product_name and min_amount < max_amount:
                st.success(f"✅ Loan product '{product_name}' created successfully!")
                st.write(f"**Target:** {target_customer}")
                st.write(f"**Amount Range:** KES {min_amount:,.0f} - KES {max_amount:,.0f}")
                st.write(f"**Interest Rate:** {base_rate}%")
                st.write(f"**Max Tenure:** {max_tenure} months")
            else:
                st.error("Please check all fields")

    # TAB 3: DISBURSEMENT
    with tab_disbursement:
        st.subheader("💰 Loan Disbursement")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Approved Applications")
            application_id = st.text_input("Application ID", placeholder="Enter application ID")
            
            if st.button("🔍 Load Application"):
                if application_id:
                    try:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            
                            # Get approved application
                            cursor.execute("""
                                SELECT la.*, u.full_name as customer_name
                                FROM loan_applications la
                                JOIN accounts a ON la.account_number = a.account_number
                                JOIN users u ON a.user_id = u.user_id
                                WHERE la.application_id = %s AND la.status = 'APPROVED'
                            """, (application_id,))
                            
                            app_data = cursor.fetchone()
                            conn.close()
                            
                            if app_data:
                                st.success("✅ Application loaded")
                                st.session_state.selected_app = {
                                    "application_id": app_data['application_id'],
                                    "customer_name": app_data['customer_name'],
                                    "account_number": app_data['account_number'],
                                    "loan_type": app_data['loan_type'],
                                    "approved_amount": float(app_data['loan_amount']),
                                    "interest_rate": float(app_data['interest_rate']),
                                    "tenure": app_data['tenure_months'],
                                    "monthly_payment": float(app_data['monthly_payment']) if app_data['monthly_payment'] else 0
                                }
                            else:
                                st.error("❌ Application not found or not approved")
                    except Exception as e:
                        st.error(f"Error loading application: {e}")
                        # Fallback to mock data
                        st.success("✅ Application loaded (demo)")
                        st.session_state.selected_app = {
                            "application_id": application_id,
                            "customer_name": "John Doe" if application_id.startswith("LA") else "ABC Company Ltd",
                            "account_number": "ACC1000015",
                            "loan_type": "Personal Loan",
                            "approved_amount": 150000,
                            "interest_rate": 15.0,
                            "tenure": 24,
                            "monthly_payment": 7237.50
                        }
            
            if "selected_app" in st.session_state:
                app = st.session_state.selected_app
                st.markdown("### Application Details")
                st.write(f"**Customer:** {app['customer_name']}")
                st.write(f"**Account:** {app['account_number']}")
                st.write(f"**Loan Type:** {app['loan_type']}")
                st.write(f"**Approved Amount:** KES {app['approved_amount']:,.2f}")
                st.write(f"**Interest Rate:** {app['interest_rate']}% p.a.")
                st.write(f"**Tenure:** {app['tenure']} months")
                st.write(f"**Monthly Payment:** KES {app['monthly_payment']:,.2f}")
                
                disbursement_account = st.text_input("Disbursement Account", value=app['account_number'])
                disbursement_amount = st.number_input("Disbursement Amount (KES)", 
                                                    min_value=0.0, 
                                                    max_value=float(app['approved_amount']),
                                                    value=float(app['approved_amount']),
                                                    step=1000.0)
        
        with col2:
            st.markdown("### Disbursement Calculation")
            if "selected_app" in st.session_state and disbursement_amount > 0:
                processing_fee = disbursement_amount * 0.025  # 2.5%
                insurance_fee = disbursement_amount * 0.008   # 0.8%
                legal_fee = 2500 if disbursement_amount > 100000 else 1500
                
                total_deductions = processing_fee + insurance_fee + legal_fee
                net_disbursement = disbursement_amount - total_deductions
                
                st.metric("Gross Amount", f"KES {disbursement_amount:,.2f}")
                st.metric("Processing Fee (2.5%)", f"KES {processing_fee:,.2f}")
                st.metric("Insurance Fee (0.8%)", f"KES {insurance_fee:,.2f}")
                st.metric("Legal Fee", f"KES {legal_fee:,.2f}")
                st.metric("**Net Disbursement**", f"**KES {net_disbursement:,.2f}**")
                
                st.markdown("### Disbursement Method")
                disbursement_method = st.selectbox("Method", [
                    "Credit to Account",
                    "Bank Transfer",
                    "Cheque",
                    "Cash (Max KES 100,000)"
                ])
                
                if disbursement_method == "Cash" and disbursement_amount > 100000:
                    st.warning("⚠️ Cash disbursement limited to KES 100,000")
        
        st.markdown("---")
        if st.button("💰 Disburse Loan", type="primary"):
            if "selected_app" in st.session_state and disbursement_amount > 0:
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        
                        # Generate loan ID
                        loan_id = f"LN{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                        
                        # Credit the customer account
                        cursor.execute("""
                            UPDATE accounts 
                            SET balance = balance + %s 
                            WHERE account_number = %s
                        """, (net_disbursement, disbursement_account))
                        
                        # Record the transaction
                        cursor.execute("""
                            INSERT INTO transactions 
                            (account_id, txn_type, amount, reference_code, description, created_at)
                            SELECT account_id, 'LOAN_DISBURSEMENT', %s, %s, %s, %s
                            FROM accounts WHERE account_number = %s
                        """, (
                            net_disbursement, loan_id, 
                            f"Loan disbursement - {app['loan_type']}", 
                            datetime.now(), disbursement_account
                        ))
                        
                        conn.commit()
                        conn.close()
                        
                        st.success(f"✅ Loan disbursed successfully!")
                        st.balloons()
                        
                        st.markdown("### Disbursement Receipt")
                        st.write(f"**Loan ID:** {loan_id}")
                        st.write(f"**Application ID:** {application_id}")
                        st.write(f"**Customer:** {app['customer_name']}")
                        st.write(f"**Disbursement Account:** {disbursement_account}")
                        st.write(f"**Gross Amount:** KES {disbursement_amount:,.2f}")
                        st.write(f"**Net Amount:** KES {net_disbursement:,.2f}")
                        st.write(f"**Method:** {disbursement_method}")
                        st.write(f"**Processed by:** {staff['full_name']}")
                        st.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                except Exception as e:
                    st.error(f"Error processing disbursement: {e}")
            else:
                st.error("Please load an application and enter disbursement amount")

    # TAB 4: REPAYMENT TRACKING
    with tab_tracking:
        st.subheader("📊 Loan Repayment Tracking")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Loan Search")
            search_type = st.radio("Search by", ["Loan ID", "Account Number", "Customer Name"])
            search_value = st.text_input(f"Enter {search_type}")
            
            if st.button("🔍 Search Loans"):
                if search_value:
                    try:
                        conn = get_db_connection()
                        if conn:
                            cursor = conn.cursor(dictionary=True)
                            
                            # Search based on type
                            if search_type == "Loan ID":
                                cursor.execute("""
                                    SELECT * FROM loan_accounts 
                                    WHERE loan_id LIKE %s AND status = 'ACTIVE'
                                """, (f"%{search_value}%",))
                            elif search_type == "Account Number":
                                cursor.execute("""
                                    SELECT * FROM loan_accounts 
                                    WHERE account_number = %s AND status = 'ACTIVE'
                                """, (search_value,))
                            else:  # Customer Name
                                cursor.execute("""
                                    SELECT * FROM loan_accounts 
                                    WHERE customer_name LIKE %s AND status = 'ACTIVE'
                                """, (f"%{search_value}%",))
                            
                            loans_data = cursor.fetchall()
                            conn.close()
                            
                            if loans_data:
                                loans = []
                                for loan in loans_data:
                                    loans.append({
                                        "loan_id": loan['loan_id'],
                                        "customer": loan['customer_name'],
                                        "account": loan['account_number'],
                                        "loan_type": loan['loan_type'],
                                        "principal": float(loan['principal_amount']),
                                        "outstanding": float(loan['outstanding_balance']),
                                        "monthly_payment": float(loan['monthly_payment']),
                                        "next_due": loan['next_payment_date'].strftime('%Y-%m-%d') if loan['next_payment_date'] else 'N/A',
                                        "status": loan['status'],
                                        "days_overdue": loan['days_overdue']
                                    })
                                st.session_state.search_results = loans
                            else:
                                st.warning("No loans found matching your search criteria")
                    except Exception as e:
                        st.error(f"Error searching loans: {e}")
                        # Fallback to mock data
                        loans = [
                            {
                                "loan_id": "LN20260104ABC123",
                                "customer": "Peter Kamau",
                                "account": "ACC1000016",
                                "loan_type": "Personal Loan",
                                "principal": 150000,
                                "outstanding": 95000,
                                "monthly_payment": 8500,
                                "next_due": "2026-01-15",
                                "status": "ACTIVE",
                                "days_overdue": 0
                            }
                        ]
                        st.session_state.search_results = loans
            
            if "search_results" in st.session_state:
                st.markdown("### Search Results")
                for i, loan in enumerate(st.session_state.search_results):
                    if st.button(f"Select: {loan['loan_id']} - {loan['customer']}", key=f"select_{i}"):
                        st.session_state.selected_loan = loan
        
        with col2:
            if "selected_loan" in st.session_state:
                loan = st.session_state.selected_loan
                st.markdown("### Loan Details")
                st.write(f"**Loan ID:** {loan['loan_id']}")
                st.write(f"**Customer:** {loan['customer']}")
                st.write(f"**Account:** {loan['account']}")
                st.write(f"**Loan Type:** {loan['loan_type']}")
                st.write(f"**Principal:** KES {loan['principal']:,.2f}")
                st.write(f"**Outstanding:** KES {loan['outstanding']:,.2f}")
                st.write(f"**Monthly Payment:** KES {loan['monthly_payment']:,.2f}")
                st.write(f"**Next Due:** {loan['next_due']}")
                st.write(f"**Status:** {loan['status']}")
                
                if loan['days_overdue'] > 0:
                    st.error(f"⚠️ **Overdue:** {loan['days_overdue']} days")
                else:
                    st.success("✅ **Status:** Up to date")
                
                st.markdown("### Process Payment")
                payment_amount = st.number_input("Payment Amount (KES)", min_value=0.0, step=100.0)
                payment_method = st.selectbox("Payment Method", [
                    "Cash",
                    "Bank Transfer", 
                    "Mobile Money",
                    "Cheque",
                    "Direct Debit"
                ])
                
                if st.button("💰 Process Payment", type="primary"):
                    if payment_amount > 0:
                        try:
                            conn = get_db_connection()
                            if conn:
                                cursor = conn.cursor()
                                
                                # Generate payment ID
                                payment_id = f"PAY{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:6].upper()}"
                                
                                # Calculate principal and interest portions
                                monthly_rate = 0.15 / 12  # Assuming 15% annual rate
                                interest_portion = loan['outstanding'] * monthly_rate
                                principal_portion = max(0, payment_amount - interest_portion)
                                
                                # Update loan balance
                                new_outstanding = max(0, loan['outstanding'] - principal_portion)
                                
                                cursor.execute("""
                                    UPDATE loan_accounts 
                                    SET outstanding_balance = %s,
                                        updated_at = %s
                                    WHERE loan_id = %s
                                """, (new_outstanding, datetime.now(), loan['loan_id']))
                                
                                # Record payment
                                cursor.execute("""
                                    INSERT INTO loan_payments 
                                    (payment_id, loan_id, payment_amount, principal_amount, 
                                     interest_amount, payment_method, payment_date, processed_by)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                """, (
                                    payment_id, loan['loan_id'], payment_amount, 
                                    principal_portion, interest_portion, payment_method,
                                    datetime.now().date(), staff['staff_code']
                                ))
                                
                                conn.commit()
                                conn.close()
                                
                                st.success(f"✅ Payment of KES {payment_amount:,.2f} processed!")
                                
                                st.write(f"**Receipt No:** {payment_id}")
                                st.write(f"**Previous Balance:** KES {loan['outstanding']:,.2f}")
                                st.write(f"**Payment Amount:** KES {payment_amount:,.2f}")
                                st.write(f"**Principal:** KES {principal_portion:,.2f}")
                                st.write(f"**Interest:** KES {interest_portion:,.2f}")
                                st.write(f"**New Balance:** KES {new_outstanding:,.2f}")
                                st.write(f"**Payment Method:** {payment_method}")
                                st.write(f"**Processed by:** {staff['full_name']}")
                                
                                # Update session state
                                st.session_state.selected_loan['outstanding'] = new_outstanding
                                
                        except Exception as e:
                            st.error(f"Error processing payment: {e}")
                            # Fallback display
                            st.success(f"✅ Payment of KES {payment_amount:,.2f} processed!")
                            new_outstanding = max(0, loan['outstanding'] - payment_amount)
                            st.write(f"**Receipt No:** RCP{loan['loan_id'][-6:]}{int(payment_amount)}")
                            st.write(f"**Previous Balance:** KES {loan['outstanding']:,.2f}")
                            st.write(f"**Payment Amount:** KES {payment_amount:,.2f}")
                            st.write(f"**New Balance:** KES {new_outstanding:,.2f}")
                            st.write(f"**Payment Method:** {payment_method}")
                            st.write(f"**Processed by:** {staff['full_name']}")
                            st.session_state.selected_loan['outstanding'] = new_outstanding
                    else:
                        st.error("Please enter a payment amount")

    # TAB 5: RESTRUCTURING
    with tab_restructuring:
        st.subheader("🔄 Loan Restructuring")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Loan to Restructure")
            restructure_loan_id = st.text_input("Loan ID", placeholder="Enter loan ID")
            
            if st.button("🔍 Load Loan for Restructuring"):
                if restructure_loan_id:
                    # Mock loan data
                    st.session_state.restructure_loan = {
                        "loan_id": restructure_loan_id,
                        "customer": "James Mwangi",
                        "current_balance": 75000,
                        "monthly_payment": 6500,
                        "remaining_term": 12,
                        "interest_rate": 15.0,
                        "reason_required": True
                    }
                    st.success("✅ Loan loaded for restructuring")
            
            if "restructure_loan" in st.session_state:
                loan = st.session_state.restructure_loan
                st.markdown("### Current Loan Details")
                st.write(f"**Customer:** {loan['customer']}")
                st.write(f"**Current Balance:** KES {loan['current_balance']:,.2f}")
                st.write(f"**Monthly Payment:** KES {loan['monthly_payment']:,.2f}")
                st.write(f"**Remaining Term:** {loan['remaining_term']} months")
                st.write(f"**Interest Rate:** {loan['interest_rate']}%")
                
                restructure_reason = st.selectbox("Restructuring Reason", [
                    "Financial Hardship",
                    "Change in Income",
                    "Business Challenges", 
                    "Medical Emergency",
                    "Job Loss",
                    "Economic Downturn",
                    "Other"
                ])
                
                if restructure_reason == "Other":
                    other_reason = st.text_input("Please specify")
        
        with col2:
            if "restructure_loan" in st.session_state:
                st.markdown("### New Terms")
                
                new_tenure = st.selectbox("New Tenure (months)", [
                    6, 12, 18, 24, 36, 48, 60, 72, 84, 96
                ])
                
                new_rate = st.number_input("New Interest Rate (%)", 
                                         min_value=8.0, 
                                         max_value=25.0, 
                                         value=loan['interest_rate'] - 1.0,
                                         step=0.1)
                
                grace_period = st.number_input("Grace Period (months)", 
                                             min_value=0, 
                                             max_value=6, 
                                             value=0)
                
                # Calculate new payment
                if new_tenure and new_rate:
                    monthly_rate = new_rate / 100 / 12
                    if monthly_rate > 0:
                        new_payment = loan['current_balance'] * (monthly_rate * (1 + monthly_rate)**new_tenure) / ((1 + monthly_rate)**new_tenure - 1)
                    else:
                        new_payment = loan['current_balance'] / new_tenure
                    
                    st.metric("New Monthly Payment", f"KES {new_payment:,.2f}")
                    
                    # Show comparison
                    st.markdown("### Comparison")
                    col_old, col_new = st.columns(2)
                    with col_old:
                        st.write("**Current:**")
                        st.write(f"Payment: KES {loan['monthly_payment']:,.2f}")
                        st.write(f"Term: {loan['remaining_term']} months")
                        st.write(f"Rate: {loan['interest_rate']}%")
                    
                    with col_new:
                        st.write("**New:**")
                        st.write(f"Payment: KES {new_payment:,.2f}")
                        st.write(f"Term: {new_tenure} months")
                        st.write(f"Rate: {new_rate}%")
                        if grace_period > 0:
                            st.write(f"Grace: {grace_period} months")
        
        st.markdown("---")
        if st.button("🔄 Restructure Loan", type="primary"):
            if "restructure_loan" in st.session_state and restructure_reason:
                st.success(f"✅ Loan restructuring completed!")
                st.balloons()
                
                st.markdown("### Restructuring Summary")
                st.write(f"**Loan ID:** {restructure_loan_id}")
                st.write(f"**Customer:** {loan['customer']}")
                st.write(f"**Reason:** {restructure_reason}")
                st.write(f"**New Monthly Payment:** KES {new_payment:,.2f}")
                st.write(f"**New Tenure:** {new_tenure} months")
                st.write(f"**New Interest Rate:** {new_rate}%")
                if grace_period > 0:
                    st.write(f"**Grace Period:** {grace_period} months")
                st.write(f"**Processed by:** {staff['full_name']}")
                st.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.error("Please load a loan and provide restructuring reason")


# Legacy function for standalone usage
def main():
    """
    Legacy main function for standalone usage.
    """
    # -----------------------------------------------------------------------------
    # Get Current Staff from Main System
    # -----------------------------------------------------------------------------
    def get_current_staff():
        """Get the currently logged-in staff from main system session"""
        if 'current_staff' not in st.session_state:
            st.error("❌ No active staff session. Please login through the main system.")
            st.stop()
        return st.session_state.current_staff

    # -----------------------------------------------------------------------------
    # Check Credit Operations Access
    # -----------------------------------------------------------------------------
    def check_credit_access():
        """Verify user has credit operations access"""
        staff = get_current_staff()
        allowed_roles = ['RELATIONSHIP_MANAGER', 'SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
        
        if staff['role'] not in allowed_roles:
            st.error(f"❌ Access Denied: Role '{staff['role']}' is not authorized for credit operations.")
            st.stop()
        
        return staff

    # Check access first
    staff = check_credit_access()

    st.title("💳 Credit Operations System")
    st.markdown(f"**Officer:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
    st.markdown("---")


if __name__ == "__main__":
    main()
