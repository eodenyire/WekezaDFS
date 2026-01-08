import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import uuid

st.set_page_config(page_title="Wekeza Personal Banking", layout="wide", page_icon="🏦")

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

# Initialize session state
if 'user_data' not in st.session_state: 
    st.session_state['user_data'] = None

def login_register_screen():
    st.title("🏦 Wekeza Personal Banking Portal")
    st.markdown("### Your Complete Digital Banking Solution")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            email = st.text_input("Email Address", placeholder="Enter your email", key="login_email")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_password")
            
            if st.button("🔓 Login", type="primary", use_container_width=True):
                if email and password:
                    authenticate_user(email, password)
                else:
                    st.error("Please enter both email and password")
        
        with col2:
            st.info("**Demo Accounts:**")
            st.write("📧 emmanuel@wekeza.com")
            st.write("🔑 password123")
            st.write("---")
            st.write("📧 nuria@wekeza.com") 
            st.write("🔑 password123")
    
    with tab2:
        st.subheader("Create New Account")
        st.info("🏦 **Visit any Wekeza branch to open your account**")
        st.write("**Required Documents:**")
        st.write("• Valid National ID")
        st.write("• Passport-size photo")
        st.write("• Proof of income")
        st.write("• Initial deposit (KES 1,000 minimum)")
        
        st.markdown("**Branch Locations:**")
        st.write("🏢 **Nairobi CBD** - Kenyatta Avenue")
        st.write("🏢 **Westlands** - Westlands Square")
        st.write("🏢 **Mombasa** - Digo Road")
        st.write("🏢 **Kisumu** - Oginga Odinga Street")

def authenticate_user(email, password):
    """Authenticate user login"""
    try:
        conn = get_db_connection()
        if not conn:
            return
            
        cursor = conn.cursor(dictionary=True)
        
        # Check user credentials (using plain text password to match branch operations)
        cursor.execute("""
            SELECT u.user_id, u.full_name, u.email, u.phone_number, u.national_id,
                   a.account_number, a.balance, a.status as account_status
            FROM users u
            LEFT JOIN accounts a ON u.user_id = a.user_id
            WHERE u.email = %s AND u.password_hash = %s AND u.is_active = 1 AND u.business_id IS NULL
        """, (email, password))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            st.session_state['user_data'] = user
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials or account not found")
            
    except Exception as e:
        st.error(f"Login failed: {e}")
def main_dashboard():
    """Main dashboard for authenticated users"""
    user_data = st.session_state['user_data']
    
    # Sidebar
    st.sidebar.title("🏦 Personal Banking")
    st.sidebar.success("✅ KYC Verified")
    
    # User info in sidebar
    st.sidebar.markdown("### 👤 Account Information")
    st.sidebar.write(f"**Name:** {user_data['full_name']}")
    st.sidebar.write(f"**Account:** {user_data['account_number']}")
    st.sidebar.write(f"**Status:** {user_data['account_status']}")
    
    # Quick links
    st.sidebar.markdown("### 🔗 Quick Links")
    st.sidebar.markdown("- [Admin Panel](http://localhost:8503) 🏦")
    st.sidebar.markdown("- [Branch Operations](http://localhost:8501) 🏪")
    st.sidebar.markdown("- [Business Portal](http://localhost:8504) 🏢")
    
    if st.sidebar.button("🚪 Logout", use_container_width=True): 
        st.session_state['user_data'] = None
        st.rerun()

    # Main content
    st.title(f"🏦 Welcome {user_data['full_name']}")
    
    # Account summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Wallet Balance", f"KES {user_data['balance']:,.2f}")
    
    with col2:
        st.metric("🏦 Account Number", user_data['account_number'])
    
    with col3:
        st.metric("📊 Account Status", user_data['account_status'])
    
    with col4:
        # Get quick stats
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Count today's transactions
            cursor.execute("""
                SELECT COUNT(*) as txn_count
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.user_id = %s AND DATE(t.created_at) = CURDATE()
            """, (user_data['user_id'],))
            
            today_txns = cursor.fetchone()['txn_count']
            conn.close()
            
            st.metric("📈 Today's Transactions", today_txns)
        except:
            st.metric("📈 Today's Transactions", "0")

    # Main navigation tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💰 Borrow", "🛡️ Insure", "💸 Move", "💳 Save", "📊 View", "⚙️ Settings"
    ])

    with tab1:
        render_borrow_section(user_data)
    
    with tab2:
        render_insure_section(user_data)
    
    with tab3:
        render_move_section(user_data)
    
    with tab4:
        # Import and call render_save_section from portal_sections
        from portal_sections import render_save_section
        render_save_section(user_data)
    
    with tab5:
        # Import and call render_view_section from portal_sections  
        from portal_sections import render_view_section
        render_view_section(user_data)
    
    with tab6:
        render_settings_section(user_data)
def render_borrow_section(user_data):
    """Render the borrowing/loans section"""
    st.subheader("💰 Wekeza Loans - Digital Lending")
    
    # Get loan products from database (same as branch operations)
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get loan products for individuals
        cursor.execute("""
            SELECT * FROM loan_products 
            WHERE target_customer IN ('individual', 'both') AND is_active = 1
            ORDER BY product_name
        """)
        loan_products = cursor.fetchall()
        
        # Get user's existing loans from authorization queue, approved loans, and active loan accounts
        cursor.execute("""
            SELECT 
                aq.queue_id as application_id,
                aq.transaction_type,
                aq.amount as loan_amount,
                aq.description as loan_type,
                aq.status,
                aq.created_at,
                aq.priority,
                CASE 
                    WHEN aq.status = 'PENDING' THEN 'PENDING_APPROVAL'
                    WHEN aq.status = 'APPROVED' THEN 'APPROVED_IN_QUEUE'
                    WHEN aq.status = 'REJECTED' THEN 'REJECTED_IN_QUEUE'
                    ELSE aq.status
                END as display_status,
                aq.operation_data,
                NULL as loan_id,
                NULL as outstanding_balance,
                NULL as monthly_payment,
                NULL as next_payment_date,
                NULL as product_name
            FROM authorization_queue aq
            WHERE aq.maker_id LIKE %s AND aq.transaction_type = 'LOAN_APPLICATION'
            
            UNION ALL
            
            SELECT 
                la.application_id,
                'LOAN_APPLICATION' as transaction_type,
                la.loan_amount,
                la.loan_type,
                la.status,
                la.created_at,
                'APPROVED' as priority,
                la.status as display_status,
                '' as operation_data,
                NULL as loan_id,
                NULL as outstanding_balance,
                la.monthly_payment,
                NULL as next_payment_date,
                la.loan_type as product_name
            FROM loan_applications la
            WHERE la.account_number = %s AND la.status IN ('APPROVED', 'DISBURSED', 'REJECTED')
            
            UNION ALL
            
            SELECT 
                lac.application_id,
                'LOAN_ACCOUNT' as transaction_type,
                lac.principal_amount as loan_amount,
                lac.loan_type,
                'ACTIVE' as status,
                lac.created_at,
                'ACTIVE' as priority,
                'ACTIVE' as display_status,
                '' as operation_data,
                lac.loan_id,
                lac.outstanding_balance,
                lac.monthly_payment,
                lac.next_payment_date,
                lac.loan_type as product_name
            FROM loan_accounts lac
            JOIN accounts a ON lac.account_number = a.account_number
            WHERE a.user_id = %s AND lac.status = 'ACTIVE'
            
            ORDER BY created_at DESC
        """, (f"%{user_data['user_id']}%", user_data['account_number'], user_data['user_id']))
        user_loans = cursor.fetchall()
        
        conn.close()
        
    except Exception as e:
        st.error(f"Error loading loan data: {e}")
        loan_products = []
        user_loans = []
    
    # Loan tabs
    loan_tab1, loan_tab2, loan_tab3, loan_tab4 = st.tabs([
        "📝 Apply for Loan", "📋 My Loans", "💳 Loan Payments", "🧮 Calculator"
    ])
    
    with loan_tab1:
        st.markdown("### 📝 Apply for a New Loan")
        
        # Check for pending applications in authorization queue
        pending_loans = [loan for loan in user_loans if loan['display_status'] == 'PENDING_APPROVAL']
        if pending_loans:
            st.warning("⚠️ You have loan applications pending supervisor approval.")
            
            for loan in pending_loans:
                with st.expander(f"Pending Approval - {loan['loan_type']} - KES {loan['loan_amount']:,.2f}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Amount:** KES {loan['loan_amount']:,.2f}")
                        st.write(f"**Type:** {loan['loan_type']}")
                        st.write(f"**Priority:** {loan['priority']}")
                    with col2:
                        st.write(f"**Applied:** {loan['created_at'].strftime('%Y-%m-%d')}")
                        st.write(f"**Status:** Pending Supervisor Approval")
                        st.write(f"**Queue ID:** {loan['application_id']}")
                    
                    st.info("🔄 Your application is in the supervisor's authorization queue")
                    st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
        else:
            # Loan application form
            if loan_products:
                with st.form("loan_application_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Product selection
                        selected_product = st.selectbox(
                            "Select Loan Product",
                            loan_products,
                            format_func=lambda x: f"{x['product_name']} ({x['base_interest_rate']}% p.a.)"
                        )
                        
                        loan_amount = st.number_input(
                            "Loan Amount (KES)",
                            min_value=float(selected_product['min_amount']),
                            max_value=float(selected_product['max_amount']),
                            value=float(selected_product['min_amount']),
                            step=1000.0
                        )
                        
                        loan_term = st.selectbox(
                            "Loan Term (Months)",
                            [3, 6, 9, 12, 18, 24, 36, 48, 60],
                            index=3
                        )
                    
                    with col2:
                        loan_purpose = st.selectbox("Loan Purpose", [
                            "Personal Emergency",
                            "Business Capital", 
                            "Education",
                            "Medical Bills",
                            "Home Improvement",
                            "Debt Consolidation",
                            "Asset Purchase",
                            "Other"
                        ])
                        
                        employment_status = st.selectbox("Employment Status", [
                            "Employed (Permanent)",
                            "Employed (Contract)",
                            "Self-Employed",
                            "Business Owner",
                            "Student",
                            "Other"
                        ])
                        
                        monthly_income = st.number_input("Monthly Income (KES)", min_value=0.0, step=1000.0)
                    
                    # Loan calculation
                    if loan_amount > 0:
                        interest_rate = float(selected_product['base_interest_rate']) / 100
                        processing_fee = loan_amount * (float(selected_product['processing_fee_rate']) / 100)
                        
                        # Calculate monthly payment
                        monthly_rate = interest_rate / 12
                        monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**loan_term) / ((1 + monthly_rate)**loan_term - 1)
                        total_payment = monthly_payment * loan_term
                        total_interest = total_payment - loan_amount
                        
                        st.markdown("### 📊 Loan Summary")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Principal", f"KES {loan_amount:,.2f}")
                        col2.metric("Monthly Payment", f"KES {monthly_payment:,.2f}")
                        col3.metric("Total Interest", f"KES {total_interest:,.2f}")
                        col4.metric("Processing Fee", f"KES {processing_fee:,.2f}")
                        
                        # Affordability check
                        if monthly_income > 0:
                            debt_ratio = (monthly_payment / monthly_income) * 100
                            if debt_ratio <= 30:
                                st.success(f"✅ Affordable - {debt_ratio:.1f}% of income")
                            elif debt_ratio <= 40:
                                st.warning(f"⚠️ Moderate - {debt_ratio:.1f}% of income")
                            else:
                                st.error(f"❌ High risk - {debt_ratio:.1f}% of income")
                    
                    # Terms and conditions
                    st.markdown("### 📋 Terms & Conditions")
                    st.write(f"""
                    **Product:** {selected_product['product_name']}
                    **Interest Rate:** {selected_product['base_interest_rate']}% per annum
                    **Processing Fee:** {selected_product['processing_fee_rate']}% of loan amount
                    **Repayment:** Monthly installments over {loan_term} months
                    
                    **Important Notes:**
                    - Loan approval subject to credit assessment
                    - Funds disbursed within 24 hours of approval
                    - Early repayment allowed with reduced interest
                    - Late payment attracts penalty charges
                    """)
                    
                    agree_terms = st.checkbox("I agree to the terms and conditions")
                    
                    submitted = st.form_submit_button("📝 Submit Application", type="primary")
                    
                    if submitted and agree_terms and monthly_income > 0:
                        submit_loan_application(
                            user_data['user_id'], selected_product['product_id'], 
                            loan_amount, loan_term, loan_purpose, employment_status, monthly_income
                        )
                    elif submitted and not agree_terms:
                        st.error("Please agree to the terms and conditions")
                    elif submitted and monthly_income <= 0:
                        st.error("Please enter your monthly income")
            else:
                st.info("No loan products available at the moment.")
    
    with loan_tab2:
        st.markdown("### 📋 My Loan History")
        
        if user_loans:
            # Loan summary
            active_loans = [loan for loan in user_loans if loan['status'] == 'ACTIVE']
            total_outstanding = sum(float(loan.get('outstanding_balance', 0)) for loan in active_loans)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Loans", len(user_loans))
            col2.metric("Active Loans", len(active_loans))
            col3.metric("Outstanding Balance", f"KES {total_outstanding:,.2f}")
            
            st.markdown("---")
            
            # Display loans
            for loan in user_loans:
                if loan['display_status'] == 'PENDING_APPROVAL':
                    status_color = '🟡'
                    status_text = 'PENDING SUPERVISOR APPROVAL'
                elif loan['display_status'] == 'APPROVED_IN_QUEUE':
                    status_color = '🟢'
                    status_text = 'APPROVED (Processing)'
                elif loan['display_status'] == 'REJECTED_IN_QUEUE':
                    status_color = '❌'
                    status_text = 'REJECTED'
                else:
                    status_color = {
                        'APPROVED': '🟢', 
                        'DISBURSED': '🔵',
                        'REJECTED': '❌'
                    }.get(loan['status'], '⚪')
                    status_text = loan['status']
                
                with st.expander(f"{status_color} {loan['loan_type']} - KES {loan['loan_amount']:,.2f} ({status_text})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write("**Loan Details**")
                        st.write(f"Application ID: {loan['application_id']}")
                        st.write(f"Amount: KES {loan['loan_amount']:,.2f}")
                        st.write(f"Type: {loan['loan_type']}")
                    
                    with col2:
                        st.write("**Status & Dates**")
                        st.write(f"Status: {status_text}")
                        st.write(f"Applied: {loan['created_at'].strftime('%Y-%m-%d')}")
                        if loan['display_status'] == 'PENDING_APPROVAL':
                            st.write(f"Priority: {loan['priority']}")
                        elif loan['display_status'] == 'APPROVED_IN_QUEUE':
                            st.write(f"Approved by supervisor")
                        elif loan['display_status'] == 'REJECTED_IN_QUEUE':
                            st.write(f"Rejected by supervisor")
                        
                    with col3:
                        st.write("**Next Steps**")
                        if loan['display_status'] == 'PENDING_APPROVAL':
                            st.info("⏳ Awaiting supervisor approval")
                            st.info("🔄 Check back in 2-4 hours")
                        elif loan['display_status'] == 'APPROVED_IN_QUEUE':
                            st.success("✅ Approved by supervisor")
                            st.info("🔄 Loan record being created")
                        elif loan['display_status'] == 'REJECTED_IN_QUEUE':
                            st.error("❌ Application rejected")
                            st.info("📞 Contact branch for details")
                        elif loan['status'] == 'APPROVED':
                            st.success("✅ Approved - Ready for disbursement")
                        elif loan['status'] == 'DISBURSED':
                            st.info("💰 Loan disbursed to account")
                        elif loan['status'] == 'REJECTED':
                            st.error("❌ Application rejected")
        else:
            st.info("📝 No loan history found. Apply for your first loan above!")
    
    with loan_tab3:
        render_loan_payments_section(user_data, user_loans)
    
    with loan_tab4:
        render_loan_calculator(loan_products)
def submit_loan_application(user_id, product_id, loan_amount, loan_term, loan_purpose, employment_status, monthly_income):
    """Submit a new loan application through authorization queue"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user's account number
        cursor.execute("SELECT account_number FROM accounts WHERE user_id = %s", (user_id,))
        account = cursor.fetchone()
        if not account:
            st.error("❌ Account not found!")
            return
        
        # Get product details
        cursor.execute("SELECT * FROM loan_products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        if not product:
            st.error("❌ Product not found!")
            return
        
        # Generate unique application ID within reasonable length
        # Format: LA + YYYYMMDDHHMMSS + 2 random chars = LA20260104213045AB (18 chars)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 14 chars
        random_suffix = uuid.uuid4().hex[:2].upper()  # 2 chars
        application_id = f"LA{timestamp}{random_suffix}"  # LA + 14 + 2 = 18 chars total
        
        # Calculate monthly payment
        interest_rate = float(product[5])  # base_interest_rate
        monthly_rate = interest_rate / 100 / 12
        monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**loan_term) / ((1 + monthly_rate)**loan_term - 1)
        processing_fee = loan_amount * (float(product[7]) / 100)  # processing_fee_rate
        
        # Prepare operation data for authorization queue
        operation_data = {
            "application_id": application_id,
            "account_number": account[0],
            "customer_type": "individual",
            "loan_type": product[1],  # product_name
            "loan_amount": loan_amount,
            "interest_rate": interest_rate,
            "tenure_months": loan_term,
            "purpose": loan_purpose,
            "monthly_payment": monthly_payment,
            "processing_fee": processing_fee,
            "employment_status": employment_status,
            "monthly_income": monthly_income,
            "created_by": f"CUSTOMER_{user_id}",
            "user_id": user_id
        }
        
        # Generate unique queue ID within 20 character limit
        # Format: AQ + YYYYMMDDHHMMSS + 4 random chars = AQ20260104213045ABCD (20 chars)
        queue_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 14 chars
        queue_random = uuid.uuid4().hex[:4].upper()  # 4 chars
        queue_id = f"AQ{queue_timestamp}{queue_random}"  # AQ + 14 + 4 = 20 chars total
        priority = 'HIGH' if loan_amount > 100000 else 'MEDIUM'
        
        cursor.execute("""
            INSERT INTO authorization_queue 
            (queue_id, transaction_type, reference_id, maker_id, maker_name, 
             amount, description, branch_code, status, priority, operation_data, created_at)
            VALUES (%s, 'LOAN_APPLICATION', %s, %s, %s, %s, %s, %s, 'PENDING', %s, %s, %s)
        """, (
            queue_id, application_id, f"CUSTOMER_{user_id}", f"Customer Self-Service",
            loan_amount, f"Personal Banking Loan Application - {product[1]} for Account {account[0]}",
            'ONLINE', priority, str(operation_data), datetime.now()
        ))
        
        conn.commit()
        conn.close()
        
        st.success(f"✅ Loan application submitted for approval!")
        st.info(f"📋 Application ID: {application_id}")
        st.info(f"📋 Queue ID: {queue_id}")
        st.warning("⚠️ **Important:** Your loan application requires supervisor approval before processing.")
        st.info("🔄 You will be notified once a supervisor reviews your application")
        st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
        st.balloons()
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Application submission failed: {e}")

def render_loan_payments_section(user_data, user_loans):
    """Render loan payments section"""
    st.markdown("### 💳 Loan Payments & Management")
    
    # Get active loans for payment (from loan_accounts table)
    active_loans = [loan for loan in user_loans if loan['status'] == 'ACTIVE']
    
    if active_loans:
        # Payment form
        with st.form("loan_payment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Select loan for payment
                selected_loan = st.selectbox(
                    "Select Loan for Payment",
                    active_loans,
                    format_func=lambda x: f"{x.get('product_name', x['loan_type'])} - Outstanding: KES {x.get('outstanding_balance', 0):,.2f}"
                )
                
                # Calculate appropriate min/max values for payment
                outstanding = float(selected_loan.get('outstanding_balance', 0)) if selected_loan else 0
                min_payment = min(100.0, outstanding) if outstanding > 0 else 100.0
                max_payment = outstanding if outstanding > 0 else 100000.0
                default_payment = min(min_payment, outstanding) if outstanding > 0 else 100.0
                
                payment_amount = st.number_input(
                    "Payment Amount (KES)",
                    min_value=min_payment,
                    max_value=max_payment,
                    value=default_payment,
                    step=min(100.0, outstanding/10) if outstanding > 0 else 100.0
                )
            
            with col2:
                payment_method = st.selectbox("Payment Method", [
                    "Account Balance",
                    "Mobile Money",
                    "Bank Transfer"
                ])
                
                if selected_loan:
                    st.info(f"**Outstanding Balance:** KES {selected_loan.get('outstanding_balance', 0):,.2f}")
                    if selected_loan.get('monthly_payment'):
                        st.info(f"**Monthly Payment:** KES {selected_loan['monthly_payment']:,.2f}")
                    if selected_loan.get('next_payment_date'):
                        st.info(f"**Next Payment Due:** {selected_loan['next_payment_date']}")
            
            # Payment options
            st.markdown("### Payment Options")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.form_submit_button("💰 Pay Minimum", type="secondary"):
                    if selected_loan and selected_loan.get('monthly_payment'):
                        # Use the smaller of monthly payment or outstanding balance
                        outstanding = float(selected_loan.get('outstanding_balance', 0))
                        monthly = float(selected_loan['monthly_payment'])
                        payment_amt = min(monthly, outstanding) if outstanding > 0 else monthly
                        process_loan_payment(user_data, selected_loan, payment_amt)
            
            with col2:
                if st.form_submit_button("💳 Pay Amount", type="primary"):
                    if payment_amount > 0:
                        process_loan_payment(user_data, selected_loan, payment_amount)
            
            with col3:
                if st.form_submit_button("🎯 Pay Full", type="secondary"):
                    if selected_loan and selected_loan.get('outstanding_balance'):
                        full_amount = float(selected_loan['outstanding_balance'])
                        process_loan_payment(user_data, selected_loan, full_amount)
        
        # Payment history
        st.markdown("### 📊 Recent Payments")
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT lp.payment_id, lp.payment_amount, lp.payment_date, 
                       lp.payment_method, lac.loan_type as product_name
                FROM loan_payments lp
                JOIN loan_accounts lac ON lp.loan_id = lac.loan_id
                WHERE lac.account_number = %s
                ORDER BY lp.payment_date DESC
                LIMIT 10
            """, (user_data['account_number'],))
            
            recent_payments = cursor.fetchall()
            conn.close()
            
            if recent_payments:
                # Create dataframe with explicit column selection
                payment_data = []
                for payment in recent_payments:
                    payment_data.append({
                        'Date': payment['payment_date'].strftime('%Y-%m-%d') if payment['payment_date'] else 'N/A',
                        'Loan Product': payment['product_name'] or 'N/A',
                        'Amount (KES)': float(payment['payment_amount']) if payment['payment_amount'] else 0.0,
                        'Method': payment['payment_method'] or 'N/A'
                    })
                
                payment_df = pd.DataFrame(payment_data)
                st.dataframe(
                    payment_df,
                    column_config={
                        'Amount (KES)': st.column_config.NumberColumn('Amount (KES)', format="%.2f")
                    },
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("No payment history found")
                
        except Exception as e:
            st.error(f"Error loading payment history: {e}")
            # Show debug info
            st.write("Debug: If you just made a payment, it may take a moment to appear in history.")
        
        # Loan management options
        st.markdown("### 🔧 Loan Management")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📄 Request Statement"):
                st.success("📧 Loan statement will be sent to your email within 24 hours")
        
        with col2:
            if st.button("🔄 Request Restructuring"):
                st.info("📞 Our loan officer will contact you within 48 hours to discuss restructuring options")
        
        with col3:
            if st.button("⏰ Set Payment Reminder"):
                st.success("🔔 Payment reminders activated! You'll receive SMS notifications 3 days before due date")
    
    else:
        st.info("No active loans found for payment")
        
        # Show information about disbursed loans that might not be in loan_accounts yet
        disbursed_loans = [loan for loan in user_loans if loan['status'] == 'DISBURSED']
        if disbursed_loans:
            st.warning("⚠️ You have disbursed loans that may need to be activated for payments:")
            for loan in disbursed_loans:
                st.write(f"• {loan['loan_type']} - KES {loan['loan_amount']:,.2f} (Application: {loan['application_id']})")
            st.info("💡 Contact branch operations to activate loan accounts for payment processing")

def process_loan_payment(user_data, loan, payment_amount):
    """Process loan payment through authorization queue (maker-checker system)"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue, check_authorization_thresholds
        
        # Check account balance first
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
        account = cursor.fetchone()
        conn.close()
        
        if not account or account['balance'] < payment_amount:
            st.error(f"❌ Insufficient balance! Available: KES {account['balance']:,.2f}")
            return
        
        # Prepare operation data for authorization queue
        operation_data = {
            "user_id": user_data['user_id'],
            "account_number": user_data['account_number'],
            "loan_id": loan.get('loan_id', loan.get('application_id')),
            "loan_type": loan.get('loan_type', 'Loan'),
            "payment_amount": float(payment_amount),
            "transaction_date": datetime.now().isoformat(),
            "customer_name": user_data['full_name']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
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
            st.info(f"📋 Loan: {loan.get('loan_type', 'Loan')} - {loan.get('loan_id', loan.get('application_id'))}")
            st.warning("⚠️ **Important:** Your loan payment requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your payment")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            
            # Display authorization receipt
            st.markdown("### 🧾 Loan Payment Authorization Receipt")
            st.code(f"""
WEKEZA BANK - LOAN PAYMENT AUTHORIZATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Queue ID: {result['queue_id']}
Customer: {user_data['full_name']}
Account: {user_data['account_number']}

Payment Details:
Loan ID: {loan.get('loan_id', loan.get('application_id'))}
Loan Type: {loan.get('loan_type', 'Loan')}
Payment Amount: KES {payment_amount:,.2f}

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

def render_loan_calculator(loan_products):
    """Render loan calculator"""
    st.markdown("### 🧮 Loan Calculator")
    st.write("Calculate your loan payments before applying")
    
    if loan_products:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_product = st.selectbox(
                "Select Loan Product",
                loan_products,
                format_func=lambda x: f"{x['product_name']} ({x['base_interest_rate']}%)"
            )
            
            calc_amount = st.number_input(
                "Loan Amount (KES)",
                min_value=float(selected_product['min_amount']),
                max_value=float(selected_product['max_amount']),
                value=float(selected_product['min_amount']),
                step=1000.0
            )
            
            calc_term = st.selectbox("Loan Term (Months)", [3, 6, 9, 12, 18, 24, 36, 48, 60])
        
        with col2:
            if calc_amount > 0:
                # Calculate loan details
                interest_rate = float(selected_product['base_interest_rate']) / 100
                processing_fee = calc_amount * (float(selected_product['processing_fee_rate']) / 100)
                
                # Monthly payment calculation
                monthly_rate = interest_rate / 12
                monthly_payment = (calc_amount * monthly_rate * (1 + monthly_rate)**calc_term) / ((1 + monthly_rate)**calc_term - 1)
                total_payment = monthly_payment * calc_term
                total_interest = total_payment - calc_amount
                
                st.metric("Monthly Payment", f"KES {monthly_payment:,.2f}")
                st.metric("Total Interest", f"KES {total_interest:,.2f}")
                st.metric("Processing Fee", f"KES {processing_fee:,.2f}")
                st.metric("Total Cost", f"KES {total_payment + processing_fee:,.2f}")
                
                # Amortization schedule preview
                st.markdown("**Payment Schedule Preview:**")
                for month in range(1, min(6, calc_term + 1)):
                    st.write(f"Month {month}: KES {monthly_payment:,.2f}")
                if calc_term > 5:
                    st.write(f"... and {calc_term - 5} more payments")
    else:
        st.info("No loan products available for calculation")
def render_insure_section(user_data):
    """Render the insurance section"""
    st.subheader("🛡️ Wekeza Salama Insurance")
    
    # Get insurance data from database (same as branch operations)
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get insurance products
        cursor.execute("SELECT * FROM insurance_products WHERE is_active = 1 ORDER BY product_name")
        insurance_products = cursor.fetchall()
        
        # Get user's policies (both active and pending)
        cursor.execute("""
            SELECT p.policy_number, p.policy_type as product_name, p.coverage_amount, 
                   p.annual_premium, p.status, p.created_at, p.beneficiary_name, 
                   p.beneficiary_relationship, pr.product_name as full_product_name,
                   'ACTIVE_POLICY' as source_type, p.policy_id
            FROM insurance_policies p
            LEFT JOIN insurance_products pr ON p.product_id = pr.product_id
            WHERE p.account_number = %s
            
            UNION ALL
            
            SELECT 
                CONCAT('PENDING-', aq.queue_id) as policy_number,
                aq.description as product_name,
                aq.amount as coverage_amount,
                aq.amount as annual_premium,
                CASE 
                    WHEN aq.status = 'PENDING' THEN 'PENDING_APPROVAL'
                    WHEN aq.status = 'APPROVED' THEN 'APPROVED_PENDING_CREATION'
                    ELSE aq.status
                END as status,
                aq.created_at,
                '' as beneficiary_name,
                '' as beneficiary_relationship,
                aq.description as full_product_name,
                'AUTHORIZATION_QUEUE' as source_type,
                NULL as policy_id
            FROM authorization_queue aq
            WHERE aq.transaction_type = 'POLICY_SALE' 
            AND aq.maker_id LIKE %s
            
            ORDER BY created_at DESC
        """, (user_data['account_number'], f"%CUSTOMER_{user_data['user_id']}%"))
        user_policies = cursor.fetchall()
        
        # Get user's claims
        cursor.execute("""
            SELECT c.claim_reference, c.claim_type, c.claim_amount, c.description, 
                   c.status, c.created_at, p.policy_number, 
                   COALESCE(pr.product_name, p.policy_type) as product_name
            FROM insurance_claims c
            LEFT JOIN insurance_policies p ON c.policy_id = p.policy_id
            LEFT JOIN insurance_products pr ON p.product_id = pr.product_id
            WHERE (p.account_number = %s OR c.user_id = %s)
            ORDER BY c.created_at DESC
        """, (user_data['account_number'], user_data['user_id']))
        user_claims = cursor.fetchall()
        
        conn.close()
        
    except Exception as e:
        st.error(f"Error loading insurance data: {e}")
        insurance_products = []
        user_policies = []
        user_claims = []
    
    # Insurance tabs
    ins_tab1, ins_tab2, ins_tab3, ins_tab4, ins_tab5 = st.tabs([
        "🛡️ Buy Insurance", "📋 My Policies", "💰 Pay Premiums", "📞 File Claim", "🧮 Calculator"
    ])
    
    with ins_tab1:
        st.markdown("### 🛡️ Available Insurance Products")
        
        if insurance_products:
            # Product categories
            personal_products = [p for p in insurance_products if 'Personal' in p.get('category', '') or 'Life' in p['product_name'] or 'Health' in p['product_name']]
            business_products = [p for p in insurance_products if 'Business' in p.get('category', '') or 'Commercial' in p['product_name']]
            
            product_tab1, product_tab2 = st.tabs(["👤 Personal Insurance", "🏢 Business Insurance"])
            
            with product_tab1:
                render_insurance_products(user_data, personal_products, "Personal", user_policies)
            
            with product_tab2:
                render_insurance_products(user_data, business_products, "Business", user_policies)
        else:
            st.info("No insurance products available at the moment.")
    
    with ins_tab2:
        render_my_policies_section(user_data, user_policies)
    
    with ins_tab3:
        render_premium_payments_section(user_data, user_policies)
    
    with ins_tab4:
        render_claims_section(user_data, user_policies, user_claims)
    
    with ins_tab5:
        render_insurance_calculator(insurance_products)

def render_insurance_products(user_data, products, category, user_policies):
    """Render insurance products for purchase"""
    if not products:
        st.info(f"No {category.lower()} insurance products available.")
        return
    
    for product in products:
        with st.expander(f"🛡️ {product['product_name']} - From KES {product['premium_amount']}/month"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write(f"**Product Code:** {product['product_code']}")
                st.write(f"**Description:** {product.get('description', 'Comprehensive coverage')}")
                st.write(f"**Base Coverage:** KES {product['cover_amount']:,.2f}")
                st.write(f"**Base Premium:** KES {product['premium_amount']}/month")
                st.write(f"**Payment Frequency:** {product['frequency']}")
                
                # Check if user already has this policy
                has_policy = any(p['product_id'] == product['product_id'] and p['status'] == 'ACTIVE' 
                               for p in user_policies if p.get('product_id'))
                
                if has_policy:
                    st.success("✅ You already have this policy")
                else:
                    # Purchase form
                    with st.form(f"purchase_{product['product_id']}"):
                        st.markdown("**Customize Your Coverage:**")
                        
                        # Coverage options
                        coverage_multiplier = st.selectbox(
                            "Coverage Level",
                            [(0.5, "Basic (50%)", "Affordable protection"),
                             (1.0, "Standard (100%)", "Recommended coverage"),
                             (1.5, "Premium (150%)", "Enhanced protection"),
                             (2.0, "Platinum (200%)", "Maximum coverage")],
                            format_func=lambda x: f"{x[1]} - {x[2]}",
                            index=1
                        )
                        
                        # Calculate adjusted amounts
                        adjusted_coverage = float(product['cover_amount']) * coverage_multiplier[0]
                        adjusted_premium = float(product['premium_amount']) * coverage_multiplier[0]
                        
                        # Beneficiary info for life insurance
                        if 'Life' in product['product_name'] or 'Death' in product.get('description', ''):
                            beneficiary_name = st.text_input("Beneficiary Name *")
                            beneficiary_relationship = st.selectbox("Relationship", [
                                "Spouse", "Child", "Parent", "Sibling", "Other Family"
                            ])
                        else:
                            beneficiary_name = beneficiary_relationship = None
                        
                        # Auto-renewal
                        auto_renew = st.checkbox("Enable Auto-Renewal", value=True)
                        
                        st.info(f"💰 Monthly Premium: KES {adjusted_premium:.2f}")
                        st.info(f"🛡️ Coverage Amount: KES {adjusted_coverage:,.2f}")
                        
                        submitted = st.form_submit_button("🛡️ Purchase Policy", type="primary")
                        
                        if submitted:
                            if 'Life' in product['product_name'] and not beneficiary_name:
                                st.error("Beneficiary name is required for life insurance")
                            else:
                                purchase_insurance_policy(
                                    user_data, product, adjusted_coverage, adjusted_premium,
                                    auto_renew, beneficiary_name, beneficiary_relationship
                                )
            
            with col2:
                # Product benefits
                st.markdown("**Key Benefits:**")
                if 'Life' in product['product_name']:
                    st.write("• Death benefit coverage")
                    st.write("• Permanent disability")
                    st.write("• Critical illness cover")
                    st.write("• Family financial security")
                elif 'Health' in product['product_name']:
                    st.write("• Hospitalization cover")
                    st.write("• Outpatient services")
                    st.write("• Emergency medical care")
                    st.write("• Specialist consultations")
                elif 'Education' in product['product_name']:
                    st.write("• Education fee coverage")
                    st.write("• Savings component")
                    st.write("• Maturity benefits")
                    st.write("• Flexible premiums")
                else:
                    st.write("• Comprehensive coverage")
                    st.write("• 24/7 support")
                    st.write("• Quick claim processing")
                    st.write("• Competitive premiums")

def purchase_insurance_policy(user_data, product, coverage_amount, premium_amount, auto_renew, beneficiary_name=None, beneficiary_relationship=None):
    """Purchase an insurance policy through authorization queue"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        # Check account balance
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
        account = cursor.fetchone()
        conn.close()
        
        if not account or account['balance'] < premium_amount:
            st.error(f"❌ Insufficient balance! Required: KES {premium_amount:.2f}, Available: KES {account['balance']:.2f}")
            return
        
        # Prepare operation data for authorization queue
        operation_data = {
            "account_number": user_data['account_number'],
            "product_id": product['product_id'],
            "product_name": product['product_name'],
            "coverage_amount": coverage_amount,
            "premium_amount": premium_amount,
            "annual_premium": premium_amount * 12,
            "auto_renew": auto_renew,
            "beneficiary_name": beneficiary_name,
            "beneficiary_relationship": beneficiary_relationship,
            "user_id": user_data['user_id']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
            "branch_code": "ONLINE"
        }
        
        # Determine priority based on coverage amount
        priority = "URGENT" if coverage_amount > 1000000 else "HIGH" if coverage_amount > 500000 else "MEDIUM"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='POLICY_SALE',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ Insurance policy purchase submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"🛡️ Product: {product['product_name']}")
            st.info(f"💰 Coverage: KES {coverage_amount:,.2f}")
            st.info(f"💳 Premium: KES {premium_amount:.2f}/month")
            st.warning("⚠️ **Important:** Your insurance policy purchase requires supervisor approval before activation.")
            st.info("🔄 You will be notified once a supervisor reviews your application")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ Policy purchase submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Policy purchase submission failed: {e}")

def render_my_policies_section(user_data, user_policies):
    """Render my policies section"""
    st.markdown("### 📋 My Insurance Policies")
    
    if user_policies:
        # Policy summary
        active_policies = [p for p in user_policies if p['status'] == 'ACTIVE']
        total_coverage = sum(float(p['coverage_amount']) for p in active_policies)
        total_premiums = sum(float(p['annual_premium']) / 12 for p in active_policies)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Active Policies", len(active_policies))
        col2.metric("Total Coverage", f"KES {total_coverage:,.2f}")
        col3.metric("Monthly Premiums", f"KES {total_premiums:,.2f}")
        
        st.markdown("---")
        
        # Display policies
        for policy in user_policies:
            status_color = {
                'ACTIVE': '🟢',
                'EXPIRED': '🔴', 
                'CANCELLED': '⚫',
                'LAPSED': '🟡'
            }.get(policy['status'], '⚪')
            
            with st.expander(f"{status_color} {policy.get('product_name', 'Insurance Policy')} - {policy['policy_number']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write("**Policy Details**")
                    st.write(f"Policy Number: {policy['policy_number']}")
                    st.write(f"Product: {policy.get('product_name', 'N/A')}")
                    st.write(f"Status: {policy['status']}")
                    st.write(f"Coverage: KES {policy['coverage_amount']:,.2f}")
                
                with col2:
                    st.write("**Dates & Payments**")
                    if policy.get('start_date'):
                        st.write(f"Start Date: {policy['start_date']}")
                    if policy.get('maturity_date'):
                        st.write(f"Maturity Date: {policy['maturity_date']}")
                    st.write(f"Annual Premium: KES {policy['annual_premium']:,.2f}")
                    st.write(f"Payment Frequency: {policy.get('payment_frequency', 'Monthly')}")
                
                with col3:
                    st.write("**Beneficiary & Actions**")
                    if policy.get('beneficiary_name'):
                        st.write(f"Beneficiary: {policy['beneficiary_name']}")
                        st.write(f"Relationship: {policy.get('beneficiary_relationship', 'N/A')}")
                    
                    if policy['status'] == 'ACTIVE':
                        if st.button(f"📞 File Claim", key=f"claim_{policy['policy_id']}"):
                            st.session_state[f'show_claim_form_{policy["policy_id"]}'] = True
                        
                        if st.button(f"❌ Cancel Policy", key=f"cancel_{policy['policy_id']}"):
                            cancel_insurance_policy(policy['policy_id'])
    else:
        st.info("📝 No insurance policies found. Purchase your first policy above!")

def render_premium_payments_section(user_data, user_policies):
    """Render premium payments section"""
    st.markdown("### 💰 Premium Payments")
    
    active_policies = [p for p in user_policies if p['status'] == 'ACTIVE']
    
    if active_policies:
        # Payment form
        with st.form("premium_payment_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                selected_policy = st.selectbox(
                    "Select Policy for Payment",
                    active_policies,
                    format_func=lambda x: f"{x.get('product_name', 'Policy')} - {x['policy_number']}"
                )
                
                # Calculate premium amount based on frequency
                annual_premium = float(selected_policy['annual_premium'])
                if selected_policy.get('payment_frequency') == 'Monthly':
                    due_amount = annual_premium / 12
                elif selected_policy.get('payment_frequency') == 'Quarterly':
                    due_amount = annual_premium / 4
                else:
                    due_amount = annual_premium
                
                payment_amount = st.number_input(
                    "Payment Amount (KES)",
                    min_value=100.0,
                    value=due_amount,
                    step=100.0
                )
            
            with col2:
                payment_method = st.selectbox("Payment Method", [
                    "Account Balance",
                    "Mobile Money",
                    "Bank Transfer"
                ])
                
                st.info(f"**Due Amount:** KES {due_amount:,.2f}")
                st.info(f"**Policy Coverage:** KES {selected_policy['coverage_amount']:,.2f}")
            
            if st.form_submit_button("💰 Pay Premium", type="primary"):
                process_premium_payment(user_data, selected_policy, payment_amount)
        
        # Payment history
        st.markdown("### 📊 Payment History")
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT pp.*, p.policy_number, p.policy_type
                FROM premium_payments pp
                JOIN insurance_policies p ON pp.policy_number = p.policy_number
                WHERE p.account_number = %s
                ORDER BY pp.payment_date DESC
                LIMIT 10
            """, (user_data['account_number'],))
            
            payment_history = cursor.fetchall()
            conn.close()
            
            if payment_history:
                payment_df = pd.DataFrame(payment_history)
                st.dataframe(
                    payment_df[['payment_date', 'policy_number', 'payment_amount', 'payment_method']],
                    column_config={
                        'payment_date': 'Date',
                        'policy_number': 'Policy Number',
                        'payment_amount': st.column_config.NumberColumn('Amount (KES)', format="%.2f"),
                        'payment_method': 'Method'
                    },
                    use_container_width=True
                )
            else:
                st.info("No payment history found")
                
        except Exception as e:
            st.info("Payment history not available")
    else:
        st.info("No active policies found for premium payment")

def process_premium_payment(user_data, policy, payment_amount):
    """Process premium payment through authorization queue"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        # Check account balance
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
        account = cursor.fetchone()
        conn.close()
        
        if not account or account['balance'] < payment_amount:
            st.error(f"❌ Insufficient balance! Available: KES {account['balance']:,.2f}")
            return
        
        # Prepare operation data for authorization queue
        operation_data = {
            "account_number": user_data['account_number'],
            "policy_number": policy['policy_number'],
            "policy_id": policy['policy_id'],
            "payment_amount": payment_amount,
            "payment_period": f"{datetime.now().strftime('%B %Y')}",
            "user_id": user_data['user_id']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
            "branch_code": "ONLINE"
        }
        
        # Determine priority based on amount
        priority = "HIGH" if payment_amount > 50000 else "MEDIUM"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='PREMIUM_COLLECTION',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ Premium payment submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"📋 Policy: {policy['policy_number']}")
            st.info(f"💰 Amount: KES {payment_amount:,.2f}")
            st.warning("⚠️ **Important:** Your premium payment requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your payment")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            st.rerun()
        else:
            st.error(f"❌ Premium payment submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Premium payment submission failed: {e}")

def render_claims_section(user_data, user_policies, user_claims):
    """Render claims section"""
    st.markdown("### 📞 Insurance Claims")
    
    active_policies = [p for p in user_policies if p['status'] == 'ACTIVE']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### File New Claim")
        
        if active_policies:
            with st.form("claim_form"):
                selected_policy = st.selectbox(
                    "Select Policy",
                    active_policies,
                    format_func=lambda x: f"{x.get('product_name', 'Policy')} - {x['policy_number']}"
                )
                
                claim_type = st.selectbox("Claim Type", [
                    "Death Benefit", "Medical Claim", "Disability", "Maturity Benefit",
                    "Accident", "Critical Illness", "Hospitalization", "Other"
                ])
                
                claim_amount = st.number_input(
                    "Claim Amount (KES)",
                    min_value=100.0,
                    max_value=float(selected_policy['coverage_amount']),
                    step=1000.0
                )
                
                incident_date = st.date_input("Date of Incident")
                claim_description = st.text_area("Detailed Description")
                
                documents_ready = st.checkbox("I have all required documents ready")
                
                if st.form_submit_button("📞 Submit Claim", type="primary"):
                    if documents_ready:
                        file_insurance_claim(user_data, selected_policy, claim_type, claim_amount, claim_description)
                    else:
                        st.error("Please confirm you have all required documents")
        else:
            st.info("No active policies available for claims")
    
    with col2:
        st.markdown("#### My Claims History")
        
        if user_claims:
            for claim in user_claims:
                status_color = {
                    'SUBMITTED': '🟡',
                    'UNDER_REVIEW': '🔵',
                    'APPROVED': '🟢',
                    'REJECTED': '🔴'
                }.get(claim['status'], '⚪')
                
                with st.expander(f"{status_color} {claim['claim_reference']} - {claim['status']}"):
                    st.write(f"**Policy:** {claim['policy_number']}")
                    st.write(f"**Type:** {claim['claim_type']}")
                    st.write(f"**Amount:** KES {claim['claim_amount']:,.2f}")
                    st.write(f"**Status:** {claim['status']}")
                    st.write(f"**Submitted:** {claim['created_at'].strftime('%Y-%m-%d')}")
                    if claim.get('description'):
                        st.write(f"**Description:** {claim['description']}")
        else:
            st.info("No claims history found")

def file_insurance_claim(user_data, policy, claim_type, claim_amount, description):
    """File an insurance claim through authorization queue"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        # Generate claim reference
        claim_ref = f"CLM{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Prepare operation data for authorization queue
        operation_data = {
            "policy_id": policy['policy_id'],
            "policy_number": policy['policy_number'],
            "claim_reference": claim_ref,
            "claim_type": claim_type,
            "claim_amount": claim_amount,
            "description": description,
            "user_id": user_data['user_id']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
            "branch_code": "ONLINE"
        }
        
        # All claims require approval regardless of amount
        priority = "URGENT" if claim_amount > 500000 else "HIGH"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='CLAIMS_PROCESSING',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ Insurance claim submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"📋 Claim Reference: {claim_ref}")
            st.info(f"🛡️ Policy: {policy['policy_number']}")
            st.info(f"💰 Claim Amount: KES {claim_amount:,.2f}")
            st.warning("⚠️ **Important:** Your insurance claim requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your claim")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            st.rerun()
        else:
            st.error(f"❌ Claim submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Claim filing submission failed: {e}")

def cancel_insurance_policy(policy_id):
    """Cancel an insurance policy"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE insurance_policies SET status = 'CANCELLED' WHERE policy_id = %s", (policy_id,))
        conn.commit()
        conn.close()
        
        st.success("✅ Policy cancelled successfully!")
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Policy cancellation failed: {e}")

def render_insurance_calculator(insurance_products):
    """Render insurance calculator"""
    st.markdown("### 🧮 Insurance Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Coverage Needs Calculator**")
        
        monthly_income = st.number_input("Monthly Income (KES)", min_value=0.0, value=50000.0)
        dependents = st.number_input("Number of Dependents", min_value=0, max_value=10, value=2)
        existing_coverage = st.number_input("Existing Coverage (KES)", min_value=0.0, value=0.0)
        
        # Calculate recommended coverage
        income_multiplier = 60  # 5 years of income
        dependent_multiplier = 500000  # 500k per dependent
        
        recommended_life = (monthly_income * income_multiplier) + (dependents * dependent_multiplier) - existing_coverage
        recommended_health = monthly_income * 24  # 2 years of income
        
        st.markdown("**Recommended Coverage:**")
        st.metric("Life Insurance", f"KES {recommended_life:,.2f}")
        st.metric("Health Insurance", f"KES {recommended_health:,.2f}")
    
    with col2:
        st.markdown("**Premium Calculator**")
        
        if insurance_products:
            selected_product = st.selectbox(
                "Select Product",
                insurance_products,
                format_func=lambda x: x['product_name']
            )
            
            coverage_level = st.selectbox("Coverage Level", [
                (0.5, "Basic (50%)"),
                (1.0, "Standard (100%)"),
                (1.5, "Premium (150%)")
            ], format_func=lambda x: x[1], index=1)
            
            # Calculate premium
            base_premium = float(selected_product['premium_amount'])
            calculated_premium = base_premium * coverage_level[0]
            calculated_coverage = float(selected_product['cover_amount']) * coverage_level[0]
            
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
        else:
            st.info("No products available for calculation")
def render_move_section(user_data):
    """Render the money transfer section"""
    st.subheader("💸 Move Money - Transfers & Payments")
    
    # Transfer tabs
    move_tab1, move_tab2, move_tab3, move_tab4, move_tab5 = st.tabs([
        "🏦 Bank Transfer", "📱 Mobile Money", "💳 Bill Payments", "📈 CDSC Transfer", "📊 Transfer History"
    ])
    
    with move_tab1:
        render_bank_transfer_section(user_data)
    
    with move_tab2:
        render_mobile_money_section(user_data)
    
    with move_tab3:
        render_bill_payments_section(user_data)
    
    with move_tab4:
        render_cdsc_transfer_section(user_data)
    
    with move_tab5:
        render_transfer_history_section(user_data)

def render_bank_transfer_section(user_data):
    """Render bank transfer section"""
    st.markdown("### 🏦 Bank Transfers")
    
    transfer_type = st.radio("Transfer Type", [
        "Internal Transfer (Wekeza to Wekeza)",
        "External Transfer (Other Banks)"
    ], horizontal=True)
    
    with st.form("bank_transfer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            if transfer_type.startswith("Internal"):
                recipient_account = st.text_input("Recipient Wekeza Account", placeholder="ACC1000XXX")
                transfer_fee = 0.0
                st.info("💰 **Transfer Fee:** FREE for internal transfers")
            else:
                recipient_bank = st.selectbox("Recipient Bank", [
                    "Equity Bank", "KCB Bank", "Cooperative Bank", "NCBA Bank",
                    "Absa Bank", "Standard Chartered", "DTB Bank", "Family Bank"
                ])
                recipient_account = st.text_input("Recipient Account Number")
                transfer_fee = 150.0
                st.info("💰 **Transfer Fee:** KES 150.00")
            
            recipient_name = st.text_input("Recipient Name")
            transfer_amount = st.number_input("Transfer Amount (KES)", min_value=100.0, step=100.0)
        
        with col2:
            transfer_reference = st.text_input("Reference/Description", placeholder="Payment for...")
            
            # Show available balance and total cost
            available_balance = user_data['balance']
            total_cost = transfer_amount + transfer_fee
            
            st.metric("Available Balance", f"KES {available_balance:,.2f}")
            st.metric("Transfer Amount", f"KES {transfer_amount:,.2f}")
            st.metric("Transfer Fee", f"KES {transfer_fee:,.2f}")
            st.metric("Total Cost", f"KES {total_cost:,.2f}")
            
            # Balance check
            if total_cost > available_balance:
                st.error("❌ Insufficient balance!")
            else:
                st.success("✅ Sufficient balance")
        
        # Verification step
        if transfer_amount > 0 and recipient_account and recipient_name:
            st.markdown("### 🔍 Transfer Verification")
            st.write(f"**From:** {user_data['account_number']} ({user_data['full_name']})")
            st.write(f"**To:** {recipient_account} ({recipient_name})")
            if transfer_type.startswith("External"):
                st.write(f"**Bank:** {recipient_bank}")
            st.write(f"**Amount:** KES {transfer_amount:,.2f}")
            st.write(f"**Fee:** KES {transfer_fee:,.2f}")
            st.write(f"**Total:** KES {total_cost:,.2f}")
            st.write(f"**Reference:** {transfer_reference}")
            
            verify_transfer = st.checkbox("I have verified the transfer details")
        
        submitted = st.form_submit_button("💸 Send Money", type="primary")
        
        if submitted and verify_transfer and total_cost <= available_balance:
            process_bank_transfer(
                user_data, recipient_account, recipient_name, transfer_amount, 
                transfer_fee, transfer_reference, transfer_type
            )
        elif submitted and not verify_transfer:
            st.error("Please verify the transfer details")
        elif submitted and total_cost > available_balance:
            st.error("Insufficient balance for this transfer")

def process_bank_transfer(user_data, recipient_account, recipient_name, amount, fee, reference, transfer_type):
    """Process bank transfer through authorization queue"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Check if internal transfer and validate recipient
        if transfer_type.startswith("Internal"):
            cursor.execute("SELECT * FROM accounts WHERE account_number = %s AND status = 'ACTIVE'", (recipient_account,))
            recipient = cursor.fetchone()
            
            if not recipient:
                st.error("❌ Recipient account not found or inactive")
                return
        
        # Check account balance
        total_debit = amount + fee
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
        account = cursor.fetchone()
        
        if not account or account['balance'] < total_debit:
            st.error(f"❌ Insufficient balance! Required: KES {total_debit:,.2f}, Available: KES {account['balance']:,.2f}")
            return
        
        conn.close()
        
        # Prepare operation data for authorization queue
        operation_data = {
            "sender_account": user_data['account_number'],
            "recipient_account": recipient_account,
            "recipient_name": recipient_name,
            "amount": amount,
            "fee": fee,
            "total_amount": total_debit,
            "reference": reference,
            "transfer_type": transfer_type,
            "user_id": user_data['user_id']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
            "branch_code": "ONLINE"
        }
        
        # Determine priority based on amount
        priority = "URGENT" if total_debit > 500000 else "HIGH" if total_debit > 100000 else "MEDIUM"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='BANK_TRANSFER',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ Transfer submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"💰 Amount: KES {amount:,.2f}")
            st.info(f"👤 Recipient: {recipient_name}")
            st.warning("⚠️ **Important:** Your transfer requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your transfer")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            st.balloons()
            st.rerun()
        else:
            st.error(f"❌ Transfer submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Transfer submission failed: {e}")

def render_mobile_money_section(user_data):
    """Render mobile money transfer section"""
    st.markdown("### 📱 Mobile Money Transfer")
    
    with st.form("mobile_money_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            mobile_provider = st.selectbox("Mobile Money Provider", [
                "M-Pesa (Safaricom)",
                "Airtel Money",
                "T-Kash (Telkom)"
            ])
            
            recipient_phone = st.text_input("Recipient Phone Number", placeholder="254712345678")
            recipient_name = st.text_input("Recipient Name")
            transfer_amount = st.number_input("Transfer Amount (KES)", min_value=10.0, max_value=150000.0, step=10.0)
        
        with col2:
            # Calculate mobile money fees (similar to branch operations)
            if transfer_amount <= 100:
                mm_fee = 11.0
            elif transfer_amount <= 500:
                mm_fee = 22.0
            elif transfer_amount <= 1000:
                mm_fee = 29.0
            elif transfer_amount <= 1500:
                mm_fee = 29.0
            elif transfer_amount <= 2500:
                mm_fee = 44.0
            elif transfer_amount <= 3500:
                mm_fee = 56.0
            elif transfer_amount <= 5000:
                mm_fee = 75.0
            elif transfer_amount <= 7500:
                mm_fee = 87.0
            elif transfer_amount <= 10000:
                mm_fee = 115.0
            elif transfer_amount <= 15000:
                mm_fee = 167.0
            elif transfer_amount <= 20000:
                mm_fee = 185.0
            elif transfer_amount <= 35000:
                mm_fee = 197.0
            elif transfer_amount <= 50000:
                mm_fee = 278.0
            else:
                mm_fee = 315.0
            
            total_cost = transfer_amount + mm_fee
            
            st.metric("Transfer Amount", f"KES {transfer_amount:,.2f}")
            st.metric("Mobile Money Fee", f"KES {mm_fee:,.2f}")
            st.metric("Total Cost", f"KES {total_cost:,.2f}")
            
            # Balance check
            if total_cost > user_data['balance']:
                st.error("❌ Insufficient balance!")
            else:
                st.success("✅ Sufficient balance")
        
        transfer_reason = st.text_input("Transfer Reason", placeholder="Payment for goods/services")
        
        submitted = st.form_submit_button("📱 Send to Mobile Money", type="primary")
        
        if submitted and recipient_phone and recipient_name and transfer_amount > 0:
            if total_cost <= user_data['balance']:
                process_mobile_money_transfer(
                    user_data, mobile_provider, recipient_phone, recipient_name, 
                    transfer_amount, mm_fee, transfer_reason
                )
            else:
                st.error("Insufficient balance for this transfer")

def process_mobile_money_transfer(user_data, provider, phone, name, amount, fee, reason):
    """Process mobile money transfer through authorization queue"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        # Check account balance
        total_debit = amount + fee
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
        account = cursor.fetchone()
        conn.close()
        
        if not account or account['balance'] < total_debit:
            st.error(f"❌ Insufficient balance! Required: KES {total_debit:,.2f}, Available: KES {account['balance']:,.2f}")
            return
        
        # Prepare operation data for authorization queue
        operation_data = {
            "account_number": user_data['account_number'],
            "provider": provider,
            "recipient_phone": phone,
            "recipient_name": name,
            "amount": amount,
            "fee": fee,
            "total_amount": total_debit,
            "reason": reason,
            "user_id": user_data['user_id']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
            "branch_code": "ONLINE"
        }
        
        # Determine priority based on amount
        priority = "URGENT" if total_debit > 100000 else "HIGH" if total_debit > 50000 else "MEDIUM"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='MOBILE_MONEY_TRANSFER',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ Mobile money transfer submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"📱 Provider: {provider}")
            st.info(f"📞 Recipient: {phone} ({name})")
            st.info(f"💰 Amount: KES {amount:,.2f}")
            st.warning("⚠️ **Important:** Your mobile money transfer requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your transfer")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            st.rerun()
        else:
            st.error(f"❌ Transfer submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Mobile money transfer submission failed: {e}")

def render_bill_payments_section(user_data):
    """Render bill payments section"""
    st.markdown("### 💳 Bill Payments")
    
    with st.form("bill_payment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            bill_category = st.selectbox("Bill Category", [
                "Utilities", "Insurance", "Loan Repayment", "School Fees", 
                "Government Services", "Subscription Services", "Other"
            ])
            
            if bill_category == "Utilities":
                biller = st.selectbox("Select Biller", [
                    "Kenya Power (KPLC)", "Nairobi Water", "Kenya Pipeline", 
                    "Safaricom Postpay", "Airtel Postpay", "Zuku", "DSTV", "GoTV"
                ])
            elif bill_category == "Insurance":
                biller = st.selectbox("Select Insurer", [
                    "Jubilee Insurance", "CIC Insurance", "APA Insurance", 
                    "Madison Insurance", "Britam Insurance"
                ])
            elif bill_category == "Loan Repayment":
                biller = st.selectbox("Select Lender", [
                    "KCB Bank", "Equity Bank", "Cooperative Bank", "NCBA Bank",
                    "Tala", "Branch", "Timiza", "Fuliza"
                ])
            else:
                biller = st.text_input("Biller Name")
            
            account_number = st.text_input("Account/Reference Number")
            payment_amount = st.number_input("Payment Amount (KES)", min_value=10.0, step=10.0)
        
        with col2:
            # Bill payment fee
            bill_fee = 50.0  # Standard fee as per branch operations
            total_cost = payment_amount + bill_fee
            
            st.metric("Payment Amount", f"KES {payment_amount:,.2f}")
            st.metric("Service Fee", f"KES {bill_fee:,.2f}")
            st.metric("Total Cost", f"KES {total_cost:,.2f}")
            
            # Balance check
            if total_cost > user_data['balance']:
                st.error("❌ Insufficient balance!")
            else:
                st.success("✅ Sufficient balance")
            
            payment_reference = st.text_input("Payment Reference", placeholder="Optional reference")
        
        submitted = st.form_submit_button("💳 Pay Bill", type="primary")
        
        if submitted and biller and account_number and payment_amount > 0:
            if total_cost <= user_data['balance']:
                process_bill_payment(
                    user_data, bill_category, biller, account_number, 
                    payment_amount, bill_fee, payment_reference
                )
            else:
                st.error("Insufficient balance for this payment")

def process_bill_payment(user_data, category, biller, account_number, amount, fee, reference):
    """Process bill payment through authorization queue"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        # Check account balance
        total_debit = amount + fee
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
        account = cursor.fetchone()
        conn.close()
        
        if not account or account['balance'] < total_debit:
            st.error(f"❌ Insufficient balance! Required: KES {total_debit:,.2f}, Available: KES {account['balance']:,.2f}")
            return
        
        # Prepare operation data for authorization queue
        operation_data = {
            "account_number": user_data['account_number'],
            "category": category,
            "biller": biller,
            "biller_account": account_number,
            "amount": amount,
            "fee": fee,
            "total_amount": total_debit,
            "reference": reference,
            "user_id": user_data['user_id']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
            "branch_code": "ONLINE"
        }
        
        # Determine priority based on amount
        priority = "URGENT" if total_debit > 100000 else "HIGH" if total_debit > 50000 else "MEDIUM"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='BILL_PAYMENT',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ Bill payment submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"🏢 Biller: {biller}")
            st.info(f"🔢 Account: {account_number}")
            st.info(f"💰 Amount: KES {amount:,.2f}")
            st.warning("⚠️ **Important:** Your bill payment requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your payment")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            st.rerun()
        else:
            st.error(f"❌ Bill payment submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ Bill payment submission failed: {e}")

def render_cdsc_transfer_section(user_data):
    """Render CDSC transfer section"""
    st.markdown("### 📈 CDSC Transfer (Capital Markets)")
    
    st.info("💡 **CDSC (Central Depository & Settlement Corporation)** - Transfer funds for stock market investments")
    
    with st.form("cdsc_transfer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            cdsc_account = st.text_input("CDSC Account Number", placeholder="Enter your CDSC account")
            broker_name = st.selectbox("Select Broker", [
                "Genghis Capital", "Kestrel Capital", "Sterling Capital", 
                "AIB Capital", "Faida Investment Bank", "Standard Investment Bank",
                "CFC Stanbic Investment Services", "Other"
            ])
            
            if broker_name == "Other":
                broker_name = st.text_input("Broker Name")
            
            transfer_amount = st.number_input("Transfer Amount (KES)", min_value=1000.0, step=1000.0)
        
        with col2:
            # CDSC transfer fee
            cdsc_fee = 100.0  # Standard fee as per branch operations
            total_cost = transfer_amount + cdsc_fee
            
            st.metric("Transfer Amount", f"KES {transfer_amount:,.2f}")
            st.metric("CDSC Transfer Fee", f"KES {cdsc_fee:,.2f}")
            st.metric("Total Cost", f"KES {total_cost:,.2f}")
            
            # Balance check
            if total_cost > user_data['balance']:
                st.error("❌ Insufficient balance!")
            else:
                st.success("✅ Sufficient balance")
            
            transfer_purpose = st.text_area("Transfer Purpose", placeholder="Stock purchase, rights issue, etc.")
        
        submitted = st.form_submit_button("📈 Transfer to CDSC", type="primary")
        
        if submitted and cdsc_account and transfer_amount > 0:
            if total_cost <= user_data['balance']:
                process_cdsc_transfer(
                    user_data, cdsc_account, broker_name, transfer_amount, cdsc_fee, transfer_purpose
                )
            else:
                st.error("Insufficient balance for this transfer")

def process_cdsc_transfer(user_data, cdsc_account, broker, amount, fee, purpose):
    """Process CDSC transfer through authorization queue"""
    try:
        # Import authorization helper
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'branch_operations', 'shared'))
        from authorization_helper import submit_to_authorization_queue
        
        # Check account balance
        total_debit = amount + fee
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_data['user_id'],))
        account = cursor.fetchone()
        conn.close()
        
        if not account or account['balance'] < total_debit:
            st.error(f"❌ Insufficient balance! Required: KES {total_debit:,.2f}, Available: KES {account['balance']:,.2f}")
            return
        
        # Prepare operation data for authorization queue
        operation_data = {
            "account_number": user_data['account_number'],
            "cdsc_account": cdsc_account,
            "broker": broker,
            "amount": amount,
            "fee": fee,
            "total_amount": total_debit,
            "purpose": purpose,
            "user_id": user_data['user_id']
        }
        
        # Prepare maker info
        maker_info = {
            "user_id": f"CUSTOMER_{user_data['user_id']}",
            "full_name": f"Customer Self-Service - {user_data['full_name']}",
            "branch_code": "ONLINE"
        }
        
        # Determine priority based on amount
        priority = "URGENT" if total_debit > 500000 else "HIGH" if total_debit > 100000 else "MEDIUM"
        
        # Submit to authorization queue
        result = submit_to_authorization_queue(
            operation_type='CDSC_TRANSFER',
            operation_data=operation_data,
            maker_info=maker_info,
            priority=priority
        )
        
        if result.get('success'):
            st.success(f"✅ CDSC transfer submitted for supervisor approval!")
            st.info(f"📋 Queue ID: {result['queue_id']}")
            st.info(f"📈 CDSC Account: {cdsc_account}")
            st.info(f"🏢 Broker: {broker}")
            st.info(f"💰 Amount: KES {amount:,.2f}")
            st.warning("⚠️ **Important:** Your CDSC transfer requires supervisor approval before processing.")
            st.info("🔄 You will be notified once a supervisor reviews your transfer")
            st.info("⏱️ Typical approval time: 2-4 business hours during banking hours")
            st.rerun()
        else:
            st.error(f"❌ CDSC transfer submission failed: {result.get('error', 'Unknown error')}")
        
    except Exception as e:
        st.error(f"❌ CDSC transfer submission failed: {e}")

def render_transfer_history_section(user_data):
    """Render transfer history section"""
    st.markdown("### 📊 Transfer History")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_filter = st.selectbox("Time Period", [
            "Last 7 days", "Last 30 days", "Last 90 days", "All time"
        ])
    
    with col2:
        transaction_type = st.selectbox("Transaction Type", [
            "All Transfers", "Bank Transfers", "Mobile Money", "Bill Payments", "CDSC Transfers"
        ])
    
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get transfer history
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Build date filter
        if date_filter == "Last 7 days":
            date_condition = "AND t.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)"
        elif date_filter == "Last 30 days":
            date_condition = "AND t.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)"
        elif date_filter == "Last 90 days":
            date_condition = "AND t.created_at >= DATE_SUB(NOW(), INTERVAL 90 DAY)"
        else:
            date_condition = ""
        
        # Build type filter
        if transaction_type == "Bank Transfers":
            type_condition = "AND t.txn_type IN ('TRANSFER_OUT', 'TRANSFER_IN')"
        elif transaction_type == "Mobile Money":
            type_condition = "AND t.txn_type LIKE '%MOBILE_MONEY%'"
        elif transaction_type == "Bill Payments":
            type_condition = "AND t.txn_type LIKE '%BILL_PAYMENT%'"
        elif transaction_type == "CDSC Transfers":
            type_condition = "AND t.txn_type LIKE '%CDSC%'"
        else:
            type_condition = "AND t.txn_type IN ('TRANSFER_OUT', 'TRANSFER_IN', 'MOBILE_MONEY_OUT', 'BILL_PAYMENT', 'CDSC_TRANSFER')"
        
        cursor.execute(f"""
            SELECT t.*, a.account_number
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = %s {date_condition} {type_condition}
            ORDER BY t.created_at DESC
            LIMIT 50
        """, (user_data['user_id'],))
        
        transfers = cursor.fetchall()
        conn.close()
        
        if transfers:
            # Summary metrics
            total_sent = sum(t['amount'] for t in transfers if t['txn_type'] in ['TRANSFER_OUT', 'MOBILE_MONEY_OUT', 'BILL_PAYMENT', 'CDSC_TRANSFER'])
            total_received = sum(t['amount'] for t in transfers if t['txn_type'] == 'TRANSFER_IN')
            total_fees = sum(t['amount'] for t in transfers if 'FEE' in t['txn_type'])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Sent", f"KES {total_sent:,.2f}")
            col2.metric("Total Received", f"KES {total_received:,.2f}")
            col3.metric("Total Fees", f"KES {total_fees:,.2f}")
            col4.metric("Transactions", len(transfers))
            
            st.markdown("---")
            
            # Transfer list
            for transfer in transfers:
                # Determine transfer direction and icon
                if transfer['txn_type'] == 'TRANSFER_IN':
                    icon = "📥"
                    color = "success"
                elif transfer['txn_type'] in ['TRANSFER_OUT', 'MOBILE_MONEY_OUT']:
                    icon = "📤"
                    color = "info"
                elif transfer['txn_type'] == 'BILL_PAYMENT':
                    icon = "💳"
                    color = "warning"
                elif transfer['txn_type'] == 'CDSC_TRANSFER':
                    icon = "📈"
                    color = "secondary"
                else:
                    icon = "💰"
                    color = "primary"
                
                with st.expander(f"{icon} {transfer['txn_type'].replace('_', ' ').title()} - KES {transfer['amount']:,.2f} ({transfer['created_at'].strftime('%Y-%m-%d %H:%M')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Reference:** {transfer['reference_code']}")
                        st.write(f"**Amount:** KES {transfer['amount']:,.2f}")
                        st.write(f"**Type:** {transfer['txn_type'].replace('_', ' ').title()}")
                    
                    with col2:
                        st.write(f"**Date:** {transfer['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                        st.write(f"**Account:** {transfer['account_number']}")
                        if transfer.get('description'):
                            st.write(f"**Description:** {transfer['description']}")
        else:
            st.info("No transfer history found for the selected criteria")
            
    except Exception as e:
        st.error(f"Error loading transfer history: {e}")

def render_settings_section(user_data):
    """Render the settings section - import from portal_sections"""
    from portal_sections import render_settings_section as render_settings
    render_settings(user_data)

# Main execution
if st.session_state['user_data']: 
    main_dashboard()
else: 
    login_register_screen()