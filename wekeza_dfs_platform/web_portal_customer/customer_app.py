import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import uuid

st.set_page_config(page_title="Wekeza Personal Banking", layout="centered")

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

if 'user_data' not in st.session_state: 
    st.session_state['user_data'] = None

def login_register_screen():
    st.title("🔐 Wekeza Personal Banking")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Admin"])
    
    with tab1:
        st.subheader("Login to Your Account")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", key="login_btn"):
            if email and password:
                try:
                    conn = get_db_connection()
                    if not conn:
                        st.error("Database connection failed")
                        return
                        
                    cursor = conn.cursor(dictionary=True)
                    
                    # Check user credentials
                    cursor.execute("""
                        SELECT user_id, full_name, email, business_id 
                        FROM users 
                        WHERE email = %s AND password_hash = %s AND is_active = 1
                    """, (email, password))
                    
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user and user['business_id'] is None:  # Only personal users
                        st.session_state['user_data'] = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or this is a business account")
                        
                except Exception as e:
                    st.error(f"Login failed: {e}")
    
    with tab2:
        st.subheader("Create New Account")
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                reg_name = st.text_input("Full Name *")
                reg_email = st.text_input("Email *")
                reg_phone = st.text_input("Phone Number *")
            
            with col2:
                reg_national_id = st.text_input("National ID *")
                reg_password = st.text_input("Create Password *", type="password")
                reg_confirm = st.text_input("Confirm Password *", type="password")
            
            submitted = st.form_submit_button("Create Account", type="primary")
            
            if submitted and all([reg_name, reg_email, reg_phone, reg_national_id, reg_password]):
                if reg_password != reg_confirm:
                    st.error("Passwords don't match!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        # Check if user already exists
                        cursor.execute("SELECT email FROM users WHERE email = %s", (reg_email,))
                        if cursor.fetchone():
                            st.error("Email already exists! Please visit a branch to retrieve your login details.")
                        else:
                            # Create new user
                            cursor.execute("""
                                INSERT INTO users (full_name, email, phone_number, national_id, password_hash, is_active, created_at)
                                VALUES (%s, %s, %s, %s, %s, 1, %s)
                            """, (reg_name, reg_email, reg_phone, reg_national_id, reg_password, datetime.now()))
                            
                            user_id = cursor.lastrowid
                            
                            # Create account
                            account_number = f"ACC{1000000 + user_id}"
                            cursor.execute("""
                                INSERT INTO accounts (user_id, account_number, balance, currency, status, created_at)
                                VALUES (%s, %s, 10000.00, 'KES', 'ACTIVE', %s)
                            """, (user_id, account_number, datetime.now()))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Account created successfully!")
                            st.info(f"🏦 Account Number: {account_number}")
                            st.info(f"💰 Initial Balance: KES 10,000")
                            st.info(f"🔑 You can now login with: {reg_email}")
                            
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
    
    with tab3:
        st.subheader("Admin Access")
        admin_user = st.text_input("Username", value="admin", key="admin_user")
        admin_pass = st.text_input("Password", type="password", value="admin", key="admin_pass")
        
        if st.button("Admin Login", key="admin_btn"):
            if admin_user == "admin" and admin_pass == "admin":
                st.session_state['user_data'] = {
                    'user_id': 0,
                    'full_name': 'Administrator',
                    'email': 'admin',
                    'is_admin': True
                }
                st.success("Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")

def main_dashboard():
    user_data = st.session_state['user_data']
    
    # Admin dashboard
    if user_data.get('is_admin'):
        st.sidebar.title("🔧 Admin Access")
        st.sidebar.success("Administrator")
        st.sidebar.markdown("### 🔗 Quick Links")
        st.sidebar.markdown("- [Full Admin Panel](http://localhost:8503) 🏦")
        st.sidebar.markdown("- [Branch Teller](http://localhost:8505) 🏪")
        st.sidebar.markdown("- [Business Portal](http://localhost:8504) 🏢")
        
        st.title("🔧 Admin Quick Access")
        st.info("For full admin features, visit: http://localhost:8503")
        
        # Quick user creation
        with st.expander("Quick User Creation"):
            with st.form("quick_user"):
                name = st.text_input("Name")
                email = st.text_input("Email")
                password = st.text_input("Password")
                
                if st.form_submit_button("Create User"):
                    if all([name, email, password]):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            cursor.execute("""
                                INSERT INTO users (full_name, email, password_hash, is_active, created_at)
                                VALUES (%s, %s, %s, 1, %s)
                            """, (name, email, password, datetime.now()))
                            
                            user_id = cursor.lastrowid
                            account_number = f"ACC{1000000 + user_id}"
                            
                            cursor.execute("""
                                INSERT INTO accounts (user_id, account_number, balance, currency, status, created_at)
                                VALUES (%s, %s, 10000.00, 'KES', 'ACTIVE', %s)
                            """, (user_id, account_number, datetime.now()))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"User created: {email} / {password}")
                        except Exception as e:
                            st.error(f"Error: {e}")
        
        if st.button("Logout"): 
            st.session_state['user_data'] = None
            st.rerun()
        return
    
    # Regular user dashboard
    user_id = user_data['user_id']
    
    # Add sidebar information
    st.sidebar.title("🏦 Personal Banking")
    st.sidebar.success("KYC Verified")
    st.sidebar.markdown("### 🔗 Quick Links")
    st.sidebar.markdown("- [Admin Panel](http://localhost:8503) 🏦")
    st.sidebar.markdown("- [Branch Teller](http://localhost:8505) 🏪")
    st.sidebar.markdown("- [Business Portal](http://localhost:8504) 🏢")
    
    # Fetch Account Data
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT a.account_number, a.balance, a.status, u.full_name
            FROM accounts a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.user_id = %s
        """, (user_id,))
        
        account_data = cursor.fetchone()
        conn.close()
        
        if not account_data:
            st.error("Account not found")
            return
            
    except Exception as e:
        st.error(f"Database error: {e}")
        return

    st.title(f"🏦 Welcome {user_data['full_name']}")
    
    # Top Cards
    c1, c2, c3 = st.columns(3)
    c1.metric("Wallet Balance", f"KES {account_data['balance']:,.2f}")
    c2.metric("Account Number", account_data['account_number'])
    c3.metric("Account Status", account_data['status'])

    # BIMS TABS
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📉 Borrow", "🛡️ Insure", "💸 Move", "💰 Save", "⚙️ Settings"])

    with tab1: # BORROW
        st.subheader("💰 Wekeza Loans")
        
        # Get user's existing loans
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT * FROM loans 
                WHERE user_id = %s 
                ORDER BY created_at DESC
            """, (user_id,))
            
            existing_loans = cursor.fetchall()
            conn.close()
            
        except Exception as e:
            st.error(f"Error fetching loans: {e}")
            existing_loans = []
        
        # Loan application tabs
        loan_tab1, loan_tab2, loan_tab3 = st.tabs(["Apply for Loan", "My Loans", "Loan Calculator"])
        
        with loan_tab1:
            st.markdown("### 📝 Apply for a New Loan")
            
            # Check if user has pending loans
            pending_loans = [loan for loan in existing_loans if loan['status'] == 'PENDING']
            if pending_loans:
                st.warning("⚠️ You have a pending loan application. Please wait for approval before applying for another loan.")
                st.dataframe(pd.DataFrame(pending_loans)[['loan_id', 'principal_amount', 'status', 'created_at']], use_container_width=True)
            else:
                with st.form("loan_application"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        loan_amount = st.number_input("Loan Amount (KES)", min_value=1000.0, max_value=500000.0, step=1000.0, value=10000.0)
                        loan_purpose = st.selectbox("Loan Purpose", [
                            "Personal Emergency",
                            "Business Capital",
                            "Education",
                            "Medical Bills",
                            "Home Improvement",
                            "Debt Consolidation",
                            "Other"
                        ])
                        
                    with col2:
                        loan_term = st.selectbox("Loan Term", [
                            ("30 days", 30),
                            ("60 days", 60),
                            ("90 days", 90),
                            ("6 months", 180),
                            ("12 months", 365)
                        ], format_func=lambda x: x[0])
                        
                        # Calculate interest based on term
                        term_days = loan_term[1]
                        if term_days <= 30:
                            interest_rate = 15.0
                        elif term_days <= 90:
                            interest_rate = 12.0
                        elif term_days <= 180:
                            interest_rate = 10.0
                        else:
                            interest_rate = 8.0
                        
                        st.metric("Interest Rate", f"{interest_rate}%")
                    
                    # Loan summary
                    interest_amount = loan_amount * (interest_rate / 100)
                    total_due = loan_amount + interest_amount
                    
                    st.markdown("### 📊 Loan Summary")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Principal", f"KES {loan_amount:,.2f}")
                    col2.metric("Interest", f"KES {interest_amount:,.2f}")
                    col3.metric("Total Due", f"KES {total_due:,.2f}")
                    
                    # Terms and conditions
                    st.markdown("### 📋 Terms & Conditions")
                    st.write(f"""
                    - **Loan Amount**: KES {loan_amount:,.2f}
                    - **Interest Rate**: {interest_rate}% flat rate
                    - **Loan Term**: {loan_term[0]}
                    - **Total Repayment**: KES {total_due:,.2f}
                    - **Purpose**: {loan_purpose}
                    
                    **Important Notes:**
                    - Loan approval is subject to credit assessment
                    - Funds will be disbursed to your account upon approval
                    - Late payment may attract penalty charges
                    - Early repayment is allowed without penalty
                    """)
                    
                    agree_terms = st.checkbox("I agree to the terms and conditions")
                    
                    submitted = st.form_submit_button("Submit Loan Application", type="primary")
                    
                    if submitted and agree_terms:
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            
                            # Calculate due date
                            from datetime import datetime, timedelta
                            due_date = datetime.now() + timedelta(days=term_days)
                            
                            # Insert loan application
                            cursor.execute("""
                                INSERT INTO loans (user_id, principal_amount, interest_rate, interest_amount, 
                                                 total_due_amount, balance_remaining, due_date, status, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING', %s)
                            """, (user_id, loan_amount, interest_rate, interest_amount, 
                                  total_due, total_due, due_date, datetime.now()))
                            
                            loan_id = cursor.lastrowid
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Loan application submitted successfully!")
                            st.info(f"📋 Application ID: {loan_id}")
                            st.info("🔄 Your application is under review. You will be notified once approved.")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Application failed: {e}")
                    elif submitted and not agree_terms:
                        st.error("Please agree to the terms and conditions to proceed.")
        
        with loan_tab2:
            st.markdown("### 📋 My Loan History")
            
            if existing_loans:
                # Display loans in a nice format
                for loan in existing_loans:
                    with st.expander(f"Loan #{loan['loan_id']} - {loan['status']} - KES {loan['principal_amount']:,.2f}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Loan Details**")
                            st.write(f"Principal: KES {loan['principal_amount']:,.2f}")
                            st.write(f"Interest: KES {loan['interest_amount']:,.2f}")
                            st.write(f"Total Due: KES {loan['total_due_amount']:,.2f}")
                            st.write(f"Balance: KES {loan['balance_remaining']:,.2f}")
                        
                        with col2:
                            st.write("**Status & Dates**")
                            st.write(f"Status: {loan['status']}")
                            st.write(f"Applied: {loan['created_at'].strftime('%Y-%m-%d')}")
                            if loan['due_date']:
                                st.write(f"Due Date: {loan['due_date'].strftime('%Y-%m-%d')}")
                            if loan['disbursement_date']:
                                st.write(f"Disbursed: {loan['disbursement_date'].strftime('%Y-%m-%d')}")
                        
                        with col3:
                            st.write("**Actions**")
                            if loan['status'] == 'ACTIVE' and loan['balance_remaining'] > 0:
                                # Repayment section
                                repay_amount = st.number_input(
                                    "Repayment Amount", 
                                    min_value=100.0, 
                                    max_value=float(loan['balance_remaining']), 
                                    value=float(loan['balance_remaining']),
                                    key=f"repay_{loan['loan_id']}"
                                )
                                
                                if st.button(f"Make Payment", key=f"pay_{loan['loan_id']}"):
                                    make_loan_payment(user_id, loan['loan_id'], repay_amount, account_data['account_number'])
                            
                            elif loan['status'] == 'PENDING':
                                st.info("⏳ Awaiting approval")
                            elif loan['status'] == 'PAID':
                                st.success("✅ Fully paid")
            else:
                st.info("📝 No loan history found. Apply for your first loan above!")
        
        with loan_tab3:
            st.markdown("### 🧮 Loan Calculator")
            st.write("Calculate your loan repayment before applying")
            
            calc_col1, calc_col2 = st.columns(2)
            
            with calc_col1:
                calc_amount = st.number_input("Loan Amount (KES)", min_value=1000.0, max_value=500000.0, value=50000.0, key="calc_amount")
                calc_term = st.selectbox("Loan Term", [
                    ("30 days", 30, 15.0),
                    ("60 days", 60, 12.0),
                    ("90 days", 90, 12.0),
                    ("6 months", 180, 10.0),
                    ("12 months", 365, 8.0)
                ], format_func=lambda x: f"{x[0]} ({x[2]}% interest)", key="calc_term")
            
            with calc_col2:
                calc_interest = calc_amount * (calc_term[2] / 100)
                calc_total = calc_amount + calc_interest
                
                st.metric("Principal Amount", f"KES {calc_amount:,.2f}")
                st.metric("Interest Amount", f"KES {calc_interest:,.2f}")
                st.metric("Total Repayment", f"KES {calc_total:,.2f}")
                
                # Daily repayment for short terms
                if calc_term[1] <= 90:
                    daily_payment = calc_total / calc_term[1]
                    st.metric("Daily Payment", f"KES {daily_payment:,.2f}")

def make_loan_payment(user_id, loan_id, payment_amount, account_number):
    """Process loan repayment through authorization queue (maker-checker system)"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        # Check account balance first
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get loan details
        cursor.execute("SELECT * FROM loans WHERE loan_id = %s AND user_id = %s", (loan_id, user_id))
        loan = cursor.fetchone()
        
        if not loan:
            st.error("❌ Loan not found!")
            return
        
        # Get account details
        cursor.execute("SELECT * FROM accounts WHERE user_id = %s", (user_id,))
        account = cursor.fetchone()
        conn.close()
        
        if not account or account['balance'] < payment_amount:
            st.error(f"❌ Insufficient balance! Available: KES {account['balance']:,.2f}")
            return
        
        # Get user details for maker info
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT full_name FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        conn.close()
        
        # Prepare operation data for authorization queue
        operation_data = {
            "user_id": user_id,
            "account_number": account_number,
            "loan_id": loan_id,
            "loan_type": loan.get('loan_type', 'Personal Loan'),
            "payment_amount": float(payment_amount),
            "current_balance": float(loan['balance_remaining']),
            "transaction_date": datetime.now().isoformat(),
            "customer_name": user.get('full_name', 'Customer')
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_id}",
            "full_name": f"Customer Self-Service - {user.get('full_name', 'Customer')}",
            "branch_code": "ONLINE"
        }
        
        # Determine priority based on amount
        priority = "URGENT" if payment_amount > 500000 else "HIGH" if payment_amount > 100000 else "MEDIUM"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='LOAN_REPAYMENT',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ Loan payment submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"💰 Payment Amount: KES {payment_amount:,.2f}")
            st.info(f"📋 Loan ID: {loan_id}")
            st.warning("⚠️ **Important:** Your loan payment requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your payment")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            
            # Display authorization receipt
            st.markdown("### 🧾 Loan Payment Authorization Receipt")
            st.code(f"""
WEKEZA BANK - LOAN PAYMENT AUTHORIZATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Queue ID: {result['queue_id']}
Customer: {user.get('full_name', 'Customer')}
Account: {account_number}

Payment Details:
Loan ID: {loan_id}
Payment Amount: KES {payment_amount:,.2f}
Current Loan Balance: KES {loan['balance_remaining']:,.2f}

Status: PENDING APPROVAL
Priority: {priority}

Next Steps:
1. Supervisor will review and approve/reject
2. Payment will be processed after approval
3. Loan balance will be updated after approval
            """)
            st.balloons()
        else:
            st.error(f"❌ Payment submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Payment processing failed: {e}")
        import traceback
        st.error(f"Error details: {traceback.format_exc()}")

    with tab2: # INSURE
        st.subheader("🛡️ Wekeza Salama Insurance")
        
        # Get available insurance products
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT * FROM insurance_products WHERE is_active = 1 ORDER BY product_id")
            insurance_products = cursor.fetchall()
            
            # Get user's existing policies
            cursor.execute("""
                SELECT up.*, ip.product_name, ip.product_code, ip.description
                FROM user_policies up
                JOIN insurance_products ip ON up.product_id = ip.product_id
                WHERE up.user_id = %s
                ORDER BY up.created_at DESC
            """, (user_id,))
            
            user_policies = cursor.fetchall()
            conn.close()
            
        except Exception as e:
            st.error(f"Error fetching insurance data: {e}")
            insurance_products = []
            user_policies = []
        
        # Insurance tabs
        ins_tab1, ins_tab2, ins_tab3, ins_tab4 = st.tabs(["Available Plans", "My Policies", "Make Claim", "Insurance Calculator"])
        
        with ins_tab1:
            st.markdown("### 🛡️ Available Insurance Plans")
            
            if insurance_products:
                for product in insurance_products:
                    with st.expander(f"🛡️ {product['product_name']} - KES {product['premium_amount']}/month"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Product Code:** {product['product_code']}")
                            st.write(f"**Description:** {product['description']}")
                            st.write(f"**Coverage Amount:** KES {product['cover_amount']:,.2f}")
                            st.write(f"**Premium:** KES {product['premium_amount']}/month")
                            st.write(f"**Payment Frequency:** {product['frequency']}")
                            
                            # Check if user already has this policy
                            has_policy = any(p['product_id'] == product['product_id'] and p['status'] == 'ACTIVE' 
                                           for p in user_policies)
                            
                            if has_policy:
                                st.success("✅ You already have this policy")
                            else:
                                # Purchase form
                                with st.form(f"purchase_{product['product_id']}"):
                                    st.markdown("**Purchase Options:**")
                                    
                                    # Coverage amount selection
                                    coverage_options = [
                                        (product['cover_amount'] * 0.5, "Basic Coverage"),
                                        (product['cover_amount'], "Standard Coverage"),
                                        (product['cover_amount'] * 1.5, "Premium Coverage")
                                    ]
                                    
                                    selected_coverage = st.selectbox(
                                        "Coverage Level",
                                        coverage_options,
                                        format_func=lambda x: f"{x[1]} - KES {x[0]:,.2f}",
                                        key=f"coverage_{product['product_id']}"
                                    )
                                    
                                    # Calculate premium based on coverage
                                    coverage_multiplier = selected_coverage[0] / product['cover_amount']
                                    adjusted_premium = float(product['premium_amount']) * coverage_multiplier
                                    
                                    # Auto-renewal option
                                    auto_renew = st.checkbox("Enable Auto-Renewal", value=True, key=f"auto_{product['product_id']}")
                                    
                                    # Beneficiary information (for life insurance)
                                    if 'Life' in product['product_name'] or 'Credit' in product['product_name']:
                                        beneficiary_name = st.text_input("Beneficiary Name", key=f"ben_name_{product['product_id']}")
                                        beneficiary_phone = st.text_input("Beneficiary Phone", key=f"ben_phone_{product['product_id']}")
                                    else:
                                        beneficiary_name = beneficiary_phone = None
                                    
                                    st.info(f"💰 Monthly Premium: KES {adjusted_premium:.2f}")
                                    
                                    submitted = st.form_submit_button("Purchase Policy", type="primary")
                                    
                                    if submitted:
                                        purchase_insurance_policy(
                                            user_id, product['product_id'], selected_coverage[0], 
                                            adjusted_premium, auto_renew, beneficiary_name, beneficiary_phone
                                        )
                        
                        with col2:
                            # Product benefits
                            st.markdown("**Key Benefits:**")
                            if product['product_code'] == 'PAC-001':
                                st.write("• Accidental death cover")
                                st.write("• Permanent disability")
                                st.write("• Medical expenses")
                                st.write("• 24/7 emergency support")
                            elif product['product_code'] == 'CLP-001':
                                st.write("• Loan balance clearance")
                                st.write("• Critical illness cover")
                                st.write("• Disability protection")
                                st.write("• Family financial security")
                            elif product['product_code'] == 'HMC-001':
                                st.write("• Hospitalization cover")
                                st.write("• Outpatient services")
                                st.write("• Emergency medical care")
                                st.write("• Specialist consultations")
                            elif product['product_code'] == 'DAP-001':
                                st.write("• Device theft protection")
                                st.write("• Accidental damage cover")
                                st.write("• Replacement guarantee")
                                st.write("• Global coverage")
            else:
                st.info("No insurance products available at the moment.")
        
        with ins_tab2:
            st.markdown("### 📋 My Insurance Policies")
            
            if user_policies:
                # Policy summary
                active_policies = [p for p in user_policies if p['status'] == 'ACTIVE']
                total_coverage = sum(float(p['cover_amount']) for p in active_policies)
                total_premiums = sum(float(p['premium_paid']) for p in active_policies)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Active Policies", len(active_policies))
                col2.metric("Total Coverage", f"KES {total_coverage:,.2f}")
                col3.metric("Monthly Premiums", f"KES {total_premiums:,.2f}")
                
                st.markdown("---")
                
                # Display policies
                for policy in user_policies:
                    status_color = "🟢" if policy['status'] == 'ACTIVE' else "🔴" if policy['status'] == 'EXPIRED' else "🟡"
                    
                    with st.expander(f"{status_color} {policy['product_name']} - {policy['policy_number']}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write("**Policy Details**")
                            st.write(f"Policy Number: {policy['policy_number']}")
                            st.write(f"Product: {policy['product_name']}")
                            st.write(f"Status: {policy['status']}")
                            st.write(f"Coverage: KES {policy['cover_amount']:,.2f}")
                        
                        with col2:
                            st.write("**Dates & Payments**")
                            if policy['start_date']:
                                st.write(f"Start Date: {policy['start_date']}")
                            if policy['end_date']:
                                st.write(f"End Date: {policy['end_date']}")
                            st.write(f"Premium Paid: KES {policy['premium_paid']:,.2f}")
                            st.write(f"Auto-Renew: {'Yes' if policy['auto_renew'] else 'No'}")
                        
                        with col3:
                            st.write("**Actions**")
                            if policy['status'] == 'ACTIVE':
                                if st.button(f"Make Claim", key=f"claim_{policy['policy_id']}"):
                                    st.session_state[f'claim_policy_{policy["policy_id"]}'] = True
                                
                                if st.button(f"Cancel Policy", key=f"cancel_{policy['policy_id']}"):
                                    cancel_insurance_policy(policy['policy_id'])
                                
                                # Claim form
                                if st.session_state.get(f'claim_policy_{policy["policy_id"]}', False):
                                    with st.form(f"claim_form_{policy['policy_id']}"):
                                        st.markdown("**File Insurance Claim**")
                                        claim_type = st.selectbox("Claim Type", [
                                            "Accidental Death", "Permanent Disability", "Medical Expenses",
                                            "Device Theft", "Device Damage", "Hospitalization", "Emergency Treatment"
                                        ])
                                        claim_amount = st.number_input("Claim Amount (KES)", min_value=100.0, max_value=float(policy['cover_amount']))
                                        claim_description = st.text_area("Incident Description")
                                        
                                        if st.form_submit_button("Submit Claim"):
                                            file_insurance_claim(user_id, policy['policy_id'], claim_type, claim_amount, claim_description)
                                            st.session_state[f'claim_policy_{policy["policy_id"]}'] = False
                                            st.rerun()
                            else:
                                st.info(f"Policy is {policy['status']}")
            else:
                st.info("📝 No insurance policies found. Purchase your first policy above!")
        
        with ins_tab3:
            st.markdown("### 📞 File Insurance Claim")
            
            # Get user's active policies for claims
            active_policies = [p for p in user_policies if p['status'] == 'ACTIVE']
            
            if active_policies:
                with st.form("insurance_claim_form"):
                    # Policy selection
                    policy_options = [(p['policy_id'], f"{p['product_name']} - {p['policy_number']}") for p in active_policies]
                    selected_policy = st.selectbox(
                        "Select Policy",
                        policy_options,
                        format_func=lambda x: x[1]
                    )
                    
                    # Claim details
                    claim_type = st.selectbox("Type of Claim", [
                        "Accidental Death",
                        "Permanent Disability", 
                        "Medical Emergency",
                        "Hospitalization",
                        "Device Theft",
                        "Device Damage",
                        "Critical Illness",
                        "Other"
                    ])
                    
                    claim_amount = st.number_input("Claim Amount (KES)", min_value=100.0, max_value=2000000.0)
                    incident_date = st.date_input("Date of Incident")
                    incident_description = st.text_area("Detailed Description of Incident")
                    
                    # Supporting documents
                    st.markdown("**Required Documents:**")
                    st.write("• Police report (for theft/accidents)")
                    st.write("• Medical reports (for health claims)")
                    st.write("• Death certificate (for death claims)")
                    st.write("• Receipts and invoices")
                    
                    documents_uploaded = st.checkbox("I have uploaded all required documents")
                    
                    submitted = st.form_submit_button("Submit Claim", type="primary")
                    
                    if submitted and documents_uploaded:
                        file_insurance_claim(user_id, selected_policy[0], claim_type, claim_amount, incident_description)
                    elif submitted and not documents_uploaded:
                        st.error("Please confirm that you have uploaded all required documents.")
            else:
                st.info("You need an active insurance policy to file a claim.")
        
        with ins_tab4:
            st.markdown("### 🧮 Insurance Calculator")
            st.write("Calculate your insurance premiums and coverage needs")
            
            calc_col1, calc_col2 = st.columns(2)
            
            with calc_col1:
                st.markdown("**Coverage Calculator**")
                
                # Income-based calculation
                monthly_income = st.number_input("Monthly Income (KES)", min_value=0.0, value=50000.0)
                dependents = st.number_input("Number of Dependents", min_value=0, max_value=10, value=2)
                existing_coverage = st.number_input("Existing Coverage (KES)", min_value=0.0, value=0.0)
                
                # Calculate recommended coverage
                income_multiplier = 60  # 5 years of income
                dependent_multiplier = 500000  # 500k per dependent
                
                recommended_life_cover = (monthly_income * income_multiplier) + (dependents * dependent_multiplier) - existing_coverage
                recommended_health_cover = monthly_income * 24  # 2 years of income
                recommended_accident_cover = monthly_income * 36  # 3 years of income
                
                st.markdown("**Recommended Coverage:**")
                st.write(f"• Life Insurance: KES {recommended_life_cover:,.2f}")
                st.write(f"• Health Insurance: KES {recommended_health_cover:,.2f}")
                st.write(f"• Accident Cover: KES {recommended_accident_cover:,.2f}")
            
            with calc_col2:
                st.markdown("**Premium Calculator**")
                
                if insurance_products:
                    selected_product = st.selectbox(
                        "Select Insurance Product",
                        insurance_products,
                        format_func=lambda x: x['product_name']
                    )
                    
                    coverage_level = st.selectbox("Coverage Level", [
                        (0.5, "Basic (50%)"),
                        (1.0, "Standard (100%)"),
                        (1.5, "Premium (150%)")
                    ], format_func=lambda x: x[1])
                    
                    # Calculate premium
                    base_premium = float(selected_product['premium_amount'])
                    calculated_premium = base_premium * coverage_level[0]
                    calculated_coverage = float(selected_product['cover_amount']) * coverage_level[0]
                    
                    st.markdown("**Premium Breakdown:**")
                    st.metric("Monthly Premium", f"KES {calculated_premium:.2f}")
                    st.metric("Annual Premium", f"KES {calculated_premium * 12:.2f}")
                    st.metric("Coverage Amount", f"KES {calculated_coverage:,.2f}")
                    
                    # Affordability check
                    if monthly_income > 0:
                        premium_percentage = (calculated_premium / monthly_income) * 100
                        if premium_percentage <= 10:
                            st.success(f"✅ Affordable ({premium_percentage:.1f}% of income)")
                        elif premium_percentage <= 15:
                            st.warning(f"⚠️ Moderate ({premium_percentage:.1f}% of income)")
                        else:
                            st.error(f"❌ High cost ({premium_percentage:.1f}% of income)")

def purchase_insurance_policy(user_id, product_id, coverage_amount, premium_amount, auto_renew, beneficiary_name=None, beneficiary_phone=None):
    """Purchase an insurance policy"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check account balance
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
        account = cursor.fetchone()
        
        if not account or account['balance'] < premium_amount:
            st.error(f"Insufficient balance! Required: KES {premium_amount:.2f}, Available: KES {account['balance']:.2f}")
            return
        
        # Generate policy number
        policy_number = f"POL{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate dates
        start_date = datetime.now().date()
        end_date = datetime(start_date.year + 1, start_date.month, start_date.day).date()
        
        # Create policy
        cursor.execute("""
            INSERT INTO user_policies (user_id, product_id, policy_number, start_date, end_date, 
                                     status, auto_renew, premium_paid, cover_amount, created_at)
            VALUES (%s, %s, %s, %s, %s, 'ACTIVE', %s, %s, %s, %s)
        """, (user_id, product_id, policy_number, start_date, end_date, 
              auto_renew, premium_amount, coverage_amount, datetime.now()))
        
        policy_id = cursor.lastrowid
        
        # Deduct premium from account
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE user_id = %s", 
                      (premium_amount, user_id))
        
        # Record transaction
        ref_code = f"INS{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'INSURANCE_PREMIUM', %s, %s, %s, %s
            FROM accounts WHERE user_id = %s
        """, (premium_amount, ref_code, f"Insurance premium for policy {policy_number}", datetime.now(), user_id))
        
        conn.commit()
        conn.close()
        
        st.success(f"🎉 Insurance policy purchased successfully!")
        st.info(f"📋 Policy Number: {policy_number}")
        st.info(f"💰 Premium Paid: KES {premium_amount:.2f}")
        st.info(f"🛡️ Coverage: KES {coverage_amount:,.2f}")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Policy purchase failed: {e}")

def cancel_insurance_policy(policy_id):
    """Cancel an insurance policy"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE user_policies SET status = 'CANCELLED' WHERE policy_id = %s", (policy_id,))
        conn.commit()
        conn.close()
        
        st.success("✅ Policy cancelled successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Policy cancellation failed: {e}")

def file_insurance_claim(user_id, policy_id, claim_type, claim_amount, description):
    """File an insurance claim"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Generate claim reference
        claim_ref = f"CLM{uuid.uuid4().hex[:8].upper()}"
        
        # Insert claim (assuming we have an insurance_claims table)
        cursor.execute("""
            INSERT INTO insurance_claims (policy_id, user_id, claim_reference, claim_type, claim_amount, 
                                        description, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, 'SUBMITTED', %s)
        """, (policy_id, user_id, claim_ref, claim_type, claim_amount, description, datetime.now()))
        
        conn.commit()
        conn.close()
        
        st.success(f"✅ Insurance claim filed successfully!")
        st.info(f"📋 Claim Reference: {claim_ref}")
        st.info("🔄 Your claim is under review. You will be contacted within 48 hours.")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Claim filing failed: {e}")

    with tab3: # MOVE
        st.subheader("Internal Transfer")
        st.info("Transfer features coming soon...")

    with tab4: # SAVE (Statement)
        st.subheader("My Statement")
        st.info("Statement features coming soon...")

    with tab5: # SETTINGS
        st.subheader("Account Settings")
        st.info("Settings features coming soon...")
    
    if st.sidebar.button("Logout"): 
        st.session_state['user_data'] = None
        st.rerun()

if st.session_state['user_data']: 
    main_dashboard()
else: 
    login_register_screen()