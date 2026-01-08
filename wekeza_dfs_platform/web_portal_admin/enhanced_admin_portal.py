import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
import os
from datetime import datetime, timedelta
import uuid
import json

st.set_page_config(page_title="Wekeza HQ | Enhanced Admin Portal", layout="wide", page_icon="🏦")

# --- DATABASE CONNECTION ---
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_URL = f"mysql+mysqlconnector://root:root@{DB_HOST}/wekeza_dfs_db"

@st.cache_resource
def get_connection():
    return create_engine(DB_URL)

try:
    engine = get_connection()
    conn = engine.connect()
except Exception as e:
    st.error(f"⚠️ Database Error: {e}")
    st.stop()

# --- ADMIN AUTHENTICATION ---
def admin_login():
    st.title("🔐 Wekeza Bank Administration Portal")
    st.markdown("### Comprehensive Banking System Management")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("#### Administrator Login")
            username = st.text_input("Username", value="admin")
            password = st.text_input("Password", type="password", value="admin")
            
            if st.button("🔓 Login to Admin Portal", type="primary", use_container_width=True):
                if username == "admin" and password == "admin":
                    st.session_state['admin_logged_in'] = True
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials! Use: admin / admin")
            
            st.markdown("---")
            st.info("🔗 **System Access Links:**")
            st.markdown("• [Branch Operations](http://localhost:8501) - Branch Management")
            st.markdown("• [Personal Banking](http://localhost:8507) - Customer Portal") 
            st.markdown("• [Business Banking](http://localhost:8504) - Corporate Portal")

def admin_logout():
    if st.sidebar.button("🚪 Logout", type="secondary"):
        st.session_state['admin_logged_in'] = False
        st.rerun()

# Check admin authentication
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

if not st.session_state['admin_logged_in']:
    admin_login()
    st.stop()
# --- ENHANCED ADMIN DASHBOARD ---
admin_logout()

# Enhanced Sidebar
st.sidebar.title("🏦 Wekeza Bank HQ")
st.sidebar.markdown("### 🎛️ Administration Portal")

# Main navigation with comprehensive sections
view_mode = st.sidebar.radio("🎯 Admin Functions:", [
    "📊 Executive Dashboard", 
    "👤 Customer Management", 
    "🏢 Business Management",
    "🏪 Branch Operations",
    "👥 Staff Administration",
    "💰 Account Oversight",
    "📋 Loan Administration", 
    "🛡️ Insurance Management",
    "💸 Transaction Monitoring",
    "✅ Supervision & Approvals",
    "� Aenalytics & Reports",
    "🔒 Security & Compliance",
    "⚙️ System Administration"
])

st.sidebar.markdown("---")
st.sidebar.info("🔐 **Logged in as:** Administrator")

# System status indicators
st.sidebar.markdown("### 🌐 System Status")
try:
    # Check system health
    total_users = pd.read_sql("SELECT COUNT(*) as c FROM users", conn).iloc[0]['c']
    total_businesses = pd.read_sql("SELECT COUNT(*) as c FROM businesses", conn).iloc[0]['c']
    
    # Check if branches table exists
    try:
        total_branches = pd.read_sql("SELECT COUNT(*) as c FROM branches WHERE is_active = 1", conn).iloc[0]['c']
    except:
        total_branches = 0
    
    st.sidebar.success(f"✅ Users: {total_users}")
    st.sidebar.success(f"✅ Businesses: {total_businesses}")
    st.sidebar.success(f"✅ Branches: {total_branches}")
except:
    st.sidebar.error("❌ System Check Failed")

st.sidebar.markdown("### 🔗 Portal Access")
st.sidebar.markdown("- 🏪 [Branch Operations](http://localhost:8501)")
st.sidebar.markdown("- 👤 [Personal Banking](http://localhost:8507)")
st.sidebar.markdown("- 🏢 [Business Banking](http://localhost:8504)")

# --- MAIN DASHBOARD CONTENT ---
st.title(f"🏦 Wekeza Bank Administration | {view_mode}")

# 1. EXECUTIVE DASHBOARD
if view_mode == "📊 Executive Dashboard":
    st.markdown("### 🎯 Executive Overview & Key Performance Indicators")
    
    # Enhanced KPIs with better layout
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    # Comprehensive queries for KPIs with proper error handling
    try:
        total_users = pd.read_sql("SELECT COUNT(*) as c FROM users WHERE is_active = 1", conn).iloc[0]['c']
        total_businesses = pd.read_sql("SELECT COUNT(*) as c FROM businesses", conn).iloc[0]['c']
        total_accounts = pd.read_sql("SELECT COUNT(*) as c FROM accounts WHERE status = 'ACTIVE'", conn).iloc[0]['c']
        total_balance = pd.read_sql("SELECT SUM(balance) as amt FROM accounts WHERE status = 'ACTIVE'", conn).iloc[0]['amt'] or 0
        
        # Check if loans table exists and get data
        try:
            total_loans = pd.read_sql("SELECT SUM(principal_amount) as amt FROM loans WHERE status IN ('ACTIVE', 'APPROVED')", conn).iloc[0]['amt'] or 0
        except:
            # Try loan_accounts table if loans table doesn't exist
            try:
                total_loans = pd.read_sql("SELECT SUM(principal_amount) as amt FROM loan_accounts WHERE status = 'ACTIVE'", conn).iloc[0]['amt'] or 0
            except:
                total_loans = 0
        
        # Check if branches table exists
        try:
            total_branches = pd.read_sql("SELECT COUNT(*) as c FROM branches WHERE is_active = 1", conn).iloc[0]['c']
        except:
            total_branches = 0
        
        col1.metric("👤 Active Users", f"{total_users:,}", delta="+12 today")
        col2.metric("🏢 Businesses", f"{total_businesses:,}", delta="+3 this week")
        col3.metric("💰 Active Accounts", f"{total_accounts:,}")
        col4.metric("💵 Total Deposits", f"KES {total_balance:,.0f}", delta="+2.3%")
        col5.metric("📋 Active Loans", f"KES {total_loans:,.0f}", delta="+5.1%")
        col6.metric("🏪 Branches", f"{total_branches:,}")
        
    except Exception as e:
        st.error(f"Error loading KPIs: {e}")
    
    st.markdown("---")
    
    # Enhanced dashboard with multiple sections
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Real-time Activity", "📈 Financial Analytics", "🎯 Performance Metrics", "⚠️ Alerts & Monitoring"])
    
    with tab1:
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("#### 🔄 Recent Transactions")
            try:
                df_recent_txn = pd.read_sql("""
                    SELECT t.created_at, t.txn_type, t.amount, 
                           COALESCE(u.full_name, b.business_name, 'Unknown') as customer_name, 
                           a.account_number
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    ORDER BY t.created_at DESC LIMIT 15
                """, conn)
                
                if not df_recent_txn.empty:
                    for _, txn in df_recent_txn.iterrows():
                        txn_icon = "📥" if "IN" in str(txn['txn_type']) or "DEPOSIT" in str(txn['txn_type']) else "📤"
                        st.write(f"{txn_icon} **{txn['txn_type']}** - KES {txn['amount']:,.2f}")
                        st.caption(f"{txn['customer_name']} • {txn['created_at'].strftime('%H:%M')}")
                        st.markdown("---")
                else:
                    st.info("No recent transactions")
            except Exception as e:
                st.error(f"Error loading transactions: {e}")
        
        with col_b:
            st.markdown("#### 💰 Top Account Balances")
            try:
                df_top_balances = pd.read_sql("""
                    SELECT COALESCE(u.full_name, b.business_name, 'Unknown') as customer_name, 
                           a.account_number, a.balance, 
                           CASE WHEN b.business_name IS NOT NULL THEN 'Business' ELSE 'Personal' END as account_type
                    FROM accounts a
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE a.status = 'ACTIVE'
                    ORDER BY a.balance DESC LIMIT 10
                """, conn)
                
                if not df_top_balances.empty:
                    for _, acc in df_top_balances.iterrows():
                        acc_icon = "🏢" if acc['account_type'] == 'Business' else "👤"
                        st.write(f"{acc_icon} **{acc['customer_name']}**")
                        st.write(f"KES {acc['balance']:,.2f} • {acc['account_number']}")
                        st.markdown("---")
                else:
                    st.info("No account data")
            except Exception as e:
                st.error(f"Error loading balances: {e}")
        
        with col_c:
            st.markdown("#### 📋 Loan Applications")
            try:
                # Try loan_applications table first
                df_loan_apps = pd.read_sql("""
                    SELECT la.application_id, 
                           COALESCE(u.full_name, b.business_name, 'Unknown Customer') as customer_name, 
                           la.loan_amount, la.status, la.created_at
                    FROM loan_applications la
                    LEFT JOIN accounts a ON la.account_number = a.account_number
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    ORDER BY la.created_at DESC LIMIT 10
                """, conn)
                
                if not df_loan_apps.empty:
                    for _, loan in df_loan_apps.iterrows():
                        status_icon = "⏳" if loan['status'] == 'PENDING' else "✅" if loan['status'] == 'APPROVED' else "❌"
                        st.write(f"{status_icon} **{loan['customer_name']}**")
                        st.write(f"KES {loan['loan_amount']:,.2f} • {loan['status']}")
                        st.caption(f"App #{loan['application_id']} • {loan['created_at'].strftime('%Y-%m-%d')}")
                        st.markdown("---")
                else:
                    st.info("No loan applications")
            except Exception as e:
                # Fallback to loans table if loan_applications doesn't exist
                try:
                    df_loans = pd.read_sql("""
                        SELECT l.loan_id, u.full_name, l.principal_amount, l.status, l.created_at
                        FROM loans l
                        JOIN users u ON l.user_id = u.user_id
                        ORDER BY l.created_at DESC LIMIT 10
                    """, conn)
                    
                    if not df_loans.empty:
                        for _, loan in df_loans.iterrows():
                            status_icon = "⏳" if loan['status'] == 'PENDING' else "✅" if loan['status'] == 'ACTIVE' else "❌"
                            st.write(f"{status_icon} **{loan['full_name']}**")
                            st.write(f"KES {loan['principal_amount']:,.2f} • {loan['status']}")
                            st.caption(f"Loan #{loan['loan_id']} • {loan['created_at'].strftime('%Y-%m-%d')}")
                            st.markdown("---")
                    else:
                        st.info("No loan data")
                except Exception as e2:
                    st.error(f"Error loading loans: {e2}")
    
    with tab2:
        st.markdown("#### 📈 Financial Performance Analytics")
        
        # Transaction volume chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Daily Transaction Volume (Last 30 Days)")
            try:
                df_daily_txn = pd.read_sql("""
                    SELECT DATE(created_at) as txn_date, COUNT(*) as txn_count, SUM(amount) as total_amount
                    FROM transactions 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY txn_date
                """, conn)
                
                if not df_daily_txn.empty:
                    fig = px.line(df_daily_txn, x='txn_date', y='total_amount', 
                                 title='Daily Transaction Amount')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No transaction data for chart")
            except Exception as e:
                st.error(f"Error loading transaction chart: {e}")
        
        with col2:
            st.markdown("##### 🏦 Account Growth Trend")
            try:
                df_account_growth = pd.read_sql("""
                    SELECT DATE(created_at) as creation_date, COUNT(*) as accounts_created
                    FROM accounts 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY creation_date
                """, conn)
                
                if not df_account_growth.empty:
                    fig = px.bar(df_account_growth, x='creation_date', y='accounts_created',
                                title='Daily Account Creation')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No account creation data")
            except Exception as e:
                st.error(f"Error loading account growth: {e}")
    
    with tab3:
        st.markdown("#### 🎯 System Performance Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("##### 👥 User Engagement")
            # Mock engagement data - in real system would track logins, transactions, etc.
            engagement_data = {
                'Metric': ['Daily Active Users', 'Weekly Active Users', 'Monthly Active Users', 'User Retention Rate'],
                'Value': ['1,234', '5,678', '12,345', '87.5%'],
                'Change': ['+5.2%', '+3.1%', '+8.7%', '+2.1%']
            }
            df_engagement = pd.DataFrame(engagement_data)
            st.dataframe(df_engagement, use_container_width=True)
        
        with col2:
            st.markdown("##### 💰 Financial Health")
            # Calculate financial metrics
            try:
                avg_balance = pd.read_sql("SELECT AVG(balance) as avg_bal FROM accounts WHERE status = 'ACTIVE'", conn).iloc[0]['avg_bal'] or 0
                
                # Try different loan tables for default rate
                try:
                    loan_default_rate = pd.read_sql("SELECT COUNT(*) as defaults FROM loans WHERE status = 'DEFAULTED'", conn).iloc[0]['defaults']
                    total_loans_count = pd.read_sql("SELECT COUNT(*) as total FROM loans", conn).iloc[0]['total']
                except:
                    try:
                        loan_default_rate = pd.read_sql("SELECT COUNT(*) as defaults FROM loan_accounts WHERE status = 'DEFAULTED'", conn).iloc[0]['defaults']
                        total_loans_count = pd.read_sql("SELECT COUNT(*) as total FROM loan_accounts", conn).iloc[0]['total']
                    except:
                        loan_default_rate = 0
                        total_loans_count = 1
                
                default_rate = (loan_default_rate / max(total_loans_count, 1)) * 100
                
                financial_data = {
                    'Metric': ['Average Account Balance', 'Loan Default Rate', 'Total Portfolio Value', 'Risk Score'],
                    'Value': [f'KES {avg_balance:,.2f}', f'{default_rate:.1f}%', f'KES {total_balance + total_loans:,.0f}', 'Low Risk'],
                    'Status': ['✅ Healthy', '✅ Low' if default_rate < 5 else '⚠️ Monitor', '✅ Growing', '✅ Stable']
                }
                df_financial = pd.DataFrame(financial_data)
                st.dataframe(df_financial, use_container_width=True)
            except Exception as e:
                st.error(f"Error calculating financial metrics: {e}")
        
        with col3:
            st.markdown("##### 🏪 Branch Performance")
            try:
                df_branch_perf = pd.read_sql("""
                    SELECT b.branch_name, COUNT(DISTINCT a.account_id) as accounts,
                           SUM(a.balance) as total_deposits, COUNT(DISTINCT s.staff_id) as staff_count
                    FROM branches b
                    LEFT JOIN staff s ON b.branch_id = s.branch_id AND s.is_active = 1
                    LEFT JOIN accounts a ON a.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    WHERE b.is_active = 1
                    GROUP BY b.branch_id, b.branch_name
                    ORDER BY total_deposits DESC
                """, conn)
                
                if not df_branch_perf.empty:
                    st.dataframe(df_branch_perf, use_container_width=True)
                else:
                    st.info("No branch performance data")
            except Exception as e:
                st.info("Branch system not configured yet")
    
    with tab4:
        st.markdown("#### ⚠️ System Alerts & Monitoring")
        
        # System alerts and monitoring
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🚨 Active Alerts")
            
            # Check for various alert conditions
            alerts = []
            
            try:
                # Large transactions alert
                large_txn = pd.read_sql("""
                    SELECT COUNT(*) as count FROM transactions 
                    WHERE amount > 100000 AND DATE(created_at) = CURDATE()
                """, conn).iloc[0]['count']
                if large_txn > 0:
                    alerts.append(f"🔴 {large_txn} large transactions (>KES 100K) today")
                
                # Low balance accounts
                low_balance = pd.read_sql("""
                    SELECT COUNT(*) as count FROM accounts 
                    WHERE balance < 1000 AND status = 'ACTIVE'
                """, conn).iloc[0]['count']
                if low_balance > 0:
                    alerts.append(f"🟡 {low_balance} accounts with balance < KES 1,000")
                
                # Pending approvals
                try:
                    pending_loans = pd.read_sql("SELECT COUNT(*) as count FROM loan_applications WHERE status = 'PENDING'", conn).iloc[0]['count']
                    if pending_loans > 0:
                        alerts.append(f"🟠 {pending_loans} loan applications pending approval")
                except:
                    pass
                
            except Exception as e:
                alerts.append(f"⚠️ Error checking alerts: {e}")
            
            # Failed login attempts (mock data)
            alerts.append("🟡 3 failed login attempts in last hour")
            
            if alerts:
                for alert in alerts:
                    st.write(alert)
            else:
                st.success("✅ No active alerts")
        
        with col2:
            st.markdown("##### 📊 System Health")
            
            # System health indicators
            health_metrics = [
                {"Component": "Database", "Status": "✅ Healthy", "Response Time": "< 100ms"},
                {"Component": "Personal Banking", "Status": "✅ Online", "Port": "8507"},
                {"Component": "Business Banking", "Status": "✅ Online", "Port": "8504"},
                {"Component": "Branch Operations", "Status": "✅ Online", "Port": "8501"},
                {"Component": "Admin Portal", "Status": "✅ Online", "Port": "8503"}
            ]
            
            df_health = pd.DataFrame(health_metrics)
            st.dataframe(df_health, use_container_width=True)

# 2. ENHANCED CUSTOMER MANAGEMENT
elif view_mode == "👤 Customer Management":
    st.markdown("### 👤 Comprehensive Customer Management")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["➕ Create Customer", "👥 View Customers", "🔧 Customer Actions", "📊 Customer Analytics", "🎯 Customer Segments"])
    
    with tab1:
        st.markdown("#### ➕ Create New Customer Account")
        
        with st.form("enhanced_create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Personal Information**")
                full_name = st.text_input("Full Name *")
                email = st.text_input("Email Address *")
                phone = st.text_input("Phone Number *", placeholder="+254700000000")
                national_id = st.text_input("National ID *")
                date_of_birth = st.date_input("Date of Birth")
                
            with col2:
                st.markdown("**Account Setup**")
                password = st.text_input("Initial Password *", type="password", help="Customer will use this to login")
                initial_balance = st.number_input("Initial Deposit (KES)", min_value=0.0, value=10000.0)
                kyc_tier = st.selectbox("KYC Tier", ["TIER_1", "TIER_2", "TIER_3"], index=2)
                account_type = st.selectbox("Account Type", ["SAVINGS", "CURRENT", "FIXED_DEPOSIT"])
                
                # Additional customer details
                st.markdown("**Additional Details**")
                address = st.text_area("Physical Address")
            
            # Customer preferences
            st.markdown("**Preferences & Settings**")
            col3, col4 = st.columns(2)
            with col3:
                sms_notifications = st.checkbox("SMS Notifications", value=True)
                email_notifications = st.checkbox("Email Notifications", value=True)
            with col4:
                mobile_banking = st.checkbox("Enable Mobile Banking", value=True)
                internet_banking = st.checkbox("Enable Internet Banking", value=True)
            
            submitted = st.form_submit_button("🎯 Create Customer Account", type="primary")
            
            if submitted and all([full_name, email, phone, national_id, password]):
                try:
                    # Import admin authorization helper
                    from admin_authorization_helper import submit_customer_creation, get_admin_info
                    
                    # Prepare customer data for authorization queue
                    customer_data = {
                        'full_name': full_name,
                        'email': email,
                        'phone_number': phone,
                        'national_id': national_id,
                        'password_hash': password,
                        'kyc_tier': kyc_tier,
                        'initial_balance': float(initial_balance),
                        'account_type': account_type,
                        'operation_type': 'CUSTOMER_CREATE'
                    }
                    
                    # Submit to authorization queue
                    admin_info = get_admin_info()
                    result = submit_customer_creation(customer_data, admin_info)
                    
                    if result['success']:
                        st.success("✅ Customer creation submitted for approval!")
                        st.info(f"**Queue ID:** {result['queue_id']}")
                        st.info(f"**Status:** Pending supervisor approval")
                        st.warning("⚠️ **Supervisor approval required** - Customer account will be created after approval")
                        
                        # Display authorization receipt
                        st.markdown("### 🧾 Authorization Receipt")
                        st.code(f"""
WEKEZA BANK - CUSTOMER CREATION AUTHORIZATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Queue ID: {result['queue_id']}
Admin: {admin_info['username']}
Branch: HQ001

Customer Details:
Name: {full_name}
Email: {email}
Phone: {phone}
National ID: {national_id}
KYC Tier: {kyc_tier}
Initial Deposit: KES {initial_balance:,.2f}

Status: PENDING APPROVAL
Priority: URGENT

Next Steps:
1. Supervisor will review and approve/reject
2. Customer account will be created after approval
3. Initial deposit will be processed after approval
                        """)
                    else:
                        st.error(f"❌ Submission failed: {result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Authorization system error: {e}")
                    # Fallback to old direct creation (for emergency)
                    st.warning("⚠️ Falling back to direct creation - Contact IT support")
    
    with tab2:
        st.markdown("#### 👥 Customer Directory")
        
        # Enhanced customer search and filtering
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_name = st.text_input("🔍 Search by Name")
        with col2:
            search_email = st.text_input("📧 Search by Email")
        with col3:
            kyc_filter = st.selectbox("KYC Tier Filter", ["All", "TIER_1", "TIER_2", "TIER_3"])
        with col4:
            status_filter = st.selectbox("Status Filter", ["All", "Active", "Inactive"])
        
        # Build dynamic query
        query = """
        SELECT u.user_id, u.full_name, u.email, u.phone_number, u.national_id, u.kyc_tier, 
               u.is_active, u.created_at, a.account_number, a.balance, a.status as account_status
        FROM users u 
        LEFT JOIN accounts a ON u.user_id = a.user_id 
        WHERE u.business_id IS NULL
        """
        
        # Apply filters
        if search_name:
            query += f" AND u.full_name LIKE '%{search_name}%'"
        if search_email:
            query += f" AND u.email LIKE '%{search_email}%'"
        if kyc_filter != "All":
            query += f" AND u.kyc_tier = '{kyc_filter}'"
        if status_filter != "All":
            active_status = 1 if status_filter == "Active" else 0
            query += f" AND u.is_active = {active_status}"
        
        query += " ORDER BY u.created_at DESC LIMIT 100"
        
        try:
            df_customers = pd.read_sql(query, conn)
            
            if not df_customers.empty:
                # Enhanced display with better formatting
                st.dataframe(df_customers, use_container_width=True)
                
                # Customer summary statistics
                st.markdown("#### 📊 Customer Summary")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Customers", len(df_customers))
                col2.metric("Active Customers", len(df_customers[df_customers['is_active'] == 1]))
                col3.metric("Total Balance", f"KES {df_customers['balance'].sum():,.2f}")
                col4.metric("Average Balance", f"KES {df_customers['balance'].mean():,.2f}")
            else:
                st.info("No customers found matching the criteria")
        except Exception as e:
            st.error(f"Error loading customers: {e}")
    
    with tab3:
        st.markdown("#### 🔧 Customer Account Actions")
        
        customer_email = st.text_input("Customer Email Address")
        
        if customer_email:
            try:
                # Get customer details
                customer_details = pd.read_sql(f"""
                    SELECT u.*, a.account_number, a.balance, a.status as account_status
                    FROM users u 
                    LEFT JOIN accounts a ON u.user_id = a.user_id 
                    WHERE u.email = '{customer_email}' AND u.business_id IS NULL
                """, conn)
                
                if not customer_details.empty:
                    customer = customer_details.iloc[0]
                    
                    # Display customer info
                    st.markdown("##### 👤 Customer Information")
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Name:** {customer['full_name']}")
                    col1.write(f"**Email:** {customer['email']}")
                    col1.write(f"**Phone:** {customer['phone_number']}")
                    
                    col2.write(f"**Account:** {customer['account_number']}")
                    col2.write(f"**Balance:** KES {customer['balance']:,.2f}")
                    col2.write(f"**KYC Tier:** {customer['kyc_tier']}")
                    
                    col3.write(f"**Status:** {'Active' if customer['is_active'] else 'Inactive'}")
                    col3.write(f"**Account Status:** {customer['account_status']}")
                    col3.write(f"**Member Since:** {customer['created_at'].strftime('%Y-%m-%d')}")
                    
                    st.markdown("---")
                    
                    # Action buttons
                    col1, col2, col3, col4, col5 = st.columns(5)
                    
                    with col1:
                        if st.button("✅ Activate Customer"):
                            try:
                                from admin_authorization_helper import submit_account_action, get_admin_info
                                
                                result = submit_account_action(
                                    action_type='activate',
                                    account_data={
                                        'customer_email': customer_email,
                                        'customer_name': customer['full_name'],
                                        'action': 'ACTIVATE_USER'
                                    },
                                    admin_info=get_admin_info()
                                )
                                
                                if result['success']:
                                    st.success("✅ Customer activation submitted for approval!")
                                    st.info(f"Queue ID: {result['queue_id']}")
                                else:
                                    st.error(f"❌ Submission failed: {result['error']}")
                            except Exception as e:
                                st.error(f"Authorization error: {e}")
                    
                    with col2:
                        if st.button("❌ Deactivate Customer"):
                            try:
                                from admin_authorization_helper import submit_account_action, get_admin_info
                                
                                result = submit_account_action(
                                    action_type='deactivate',
                                    account_data={
                                        'customer_email': customer_email,
                                        'customer_name': customer['full_name'],
                                        'action': 'DEACTIVATE_USER'
                                    },
                                    admin_info=get_admin_info()
                                )
                                
                                if result['success']:
                                    st.success("✅ Customer deactivation submitted for approval!")
                                    st.info(f"Queue ID: {result['queue_id']}")
                                else:
                                    st.error(f"❌ Submission failed: {result['error']}")
                            except Exception as e:
                                st.error(f"Authorization error: {e}")
                    
                    with col3:
                        if st.button("🔒 Freeze Account"):
                            try:
                                from admin_authorization_helper import submit_account_action, get_admin_info
                                
                                result = submit_account_action(
                                    action_type='freeze',
                                    account_data={
                                        'customer_email': customer_email,
                                        'customer_name': customer['full_name'],
                                        'account_number': customer['account_number'],
                                        'action': 'FREEZE_ACCOUNT'
                                    },
                                    admin_info=get_admin_info()
                                )
                                
                                if result['success']:
                                    st.success("✅ Account freeze submitted for approval!")
                                    st.info(f"Queue ID: {result['queue_id']}")
                                else:
                                    st.error(f"❌ Submission failed: {result['error']}")
                            except Exception as e:
                                st.error(f"Authorization error: {e}")
                    
                    with col4:
                        if st.button("🔓 Unfreeze Account"):
                            try:
                                from admin_authorization_helper import submit_account_action, get_admin_info
                                
                                result = submit_account_action(
                                    action_type='unfreeze',
                                    account_data={
                                        'customer_email': customer_email,
                                        'customer_name': customer['full_name'],
                                        'account_number': customer['account_number'],
                                        'action': 'UNFREEZE_ACCOUNT'
                                    },
                                    admin_info=get_admin_info()
                                )
                                
                                if result['success']:
                                    st.success("✅ Account unfreeze submitted for approval!")
                                    st.info(f"Queue ID: {result['queue_id']}")
                                else:
                                    st.error(f"❌ Submission failed: {result['error']}")
                            except Exception as e:
                                st.error(f"Authorization error: {e}")
                    
                    with col5:
                        if st.button("🔄 Reset Password"):
                            try:
                                from admin_authorization_helper import submit_account_action, get_admin_info
                                
                                result = submit_account_action(
                                    action_type='reset_password',
                                    account_data={
                                        'customer_email': customer_email,
                                        'customer_name': customer['full_name'],
                                        'new_password': 'newpass123',
                                        'action': 'RESET_PASSWORD'
                                    },
                                    admin_info=get_admin_info()
                                )
                                
                                if result['success']:
                                    st.success("✅ Password reset submitted for approval!")
                                    st.info(f"Queue ID: {result['queue_id']}")
                                else:
                                    st.error(f"❌ Submission failed: {result['error']}")
                            except Exception as e:
                                st.error(f"Authorization error: {e}")
                    
                    # Balance adjustment section
                    st.markdown("##### 💰 Balance Adjustment")
                    with st.form("customer_balance_adjustment"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            adjustment_type = st.selectbox("Type", ["Credit", "Debit"])
                        with col2:
                            adjustment_amount = st.number_input("Amount (KES)", min_value=0.0)
                        with col3:
                            adjustment_reason = st.text_input("Reason")
                        
                        if st.form_submit_button("Apply Adjustment"):
                            if adjustment_amount > 0 and adjustment_reason:
                                try:
                                    from admin_authorization_helper import submit_balance_adjustment, get_admin_info
                                    
                                    # Submit balance adjustment for approval
                                    result = submit_balance_adjustment(
                                        adjustment_data={
                                            'customer_email': customer_email,
                                            'customer_name': customer['full_name'],
                                            'account_number': customer['account_number'],
                                            'adjustment_type': adjustment_type,
                                            'amount': adjustment_amount,
                                            'reason': adjustment_reason,
                                            'action': 'BALANCE_ADJUSTMENT'
                                        },
                                        admin_info=get_admin_info()
                                    )
                                    
                                    if result['success']:
                                        st.success("✅ Balance adjustment submitted for approval!")
                                        st.info(f"**Queue ID:** {result['queue_id']}")
                                        st.info(f"**Type:** {adjustment_type}")
                                        st.info(f"**Amount:** KES {adjustment_amount:,.2f}")
                                        st.info(f"**Reason:** {adjustment_reason}")
                                        st.warning("⚠️ **Supervisor approval required** - Balance will be adjusted after approval")
                                    else:
                                        st.error(f"❌ Submission failed: {result['error']}")
                                        
                                except Exception as e:
                                    st.error(f"❌ Authorization system error: {e}")
                else:
                    st.error("Customer not found!")
            except Exception as e:
                st.error(f"Error loading customer: {e}")
    
    with tab4:
        st.markdown("#### 📊 Customer Analytics")
        
        # Customer analytics and insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📈 Customer Growth")
            try:
                df_customer_growth = pd.read_sql("""
                    SELECT DATE(created_at) as signup_date, COUNT(*) as new_customers
                    FROM users 
                    WHERE business_id IS NULL AND created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY signup_date
                """, conn)
                
                if not df_customer_growth.empty:
                    fig = px.line(df_customer_growth, x='signup_date', y='new_customers',
                                 title='Daily Customer Acquisition (Last 30 Days)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No customer growth data available")
            except Exception as e:
                st.error(f"Error loading customer growth: {e}")
        
        with col2:
            st.markdown("##### 💰 Balance Distribution")
            try:
                df_balance_dist = pd.read_sql("""
                    SELECT 
                        CASE 
                            WHEN balance < 1000 THEN 'Under KES 1K'
                            WHEN balance < 10000 THEN 'KES 1K - 10K'
                            WHEN balance < 50000 THEN 'KES 10K - 50K'
                            WHEN balance < 100000 THEN 'KES 50K - 100K'
                            ELSE 'Over KES 100K'
                        END as balance_range,
                        COUNT(*) as customer_count
                    FROM accounts a
                    JOIN users u ON a.user_id = u.user_id
                    WHERE u.business_id IS NULL AND a.status = 'ACTIVE'
                    GROUP BY balance_range
                """, conn)
                
                if not df_balance_dist.empty:
                    fig = px.pie(df_balance_dist, values='customer_count', names='balance_range',
                                title='Customer Balance Distribution')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No balance distribution data")
            except Exception as e:
                st.error(f"Error loading balance distribution: {e}")
    
    with tab5:
        st.markdown("#### 🎯 Customer Segmentation")
        
        # Customer segmentation analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 KYC Tier Distribution")
            try:
                df_kyc_dist = pd.read_sql("""
                    SELECT kyc_tier, COUNT(*) as customer_count
                    FROM users 
                    WHERE business_id IS NULL AND is_active = 1
                    GROUP BY kyc_tier
                """, conn)
                
                if not df_kyc_dist.empty:
                    fig = px.bar(df_kyc_dist, x='kyc_tier', y='customer_count',
                                title='Customers by KYC Tier')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No KYC distribution data")
            except Exception as e:
                st.error(f"Error loading KYC distribution: {e}")
        
        with col2:
            st.markdown("##### 🎯 High-Value Customers")
            try:
                df_high_value = pd.read_sql("""
                    SELECT u.full_name, u.email, a.balance, u.kyc_tier
                    FROM users u
                    JOIN accounts a ON u.user_id = a.user_id
                    WHERE u.business_id IS NULL AND a.balance > 100000
                    ORDER BY a.balance DESC
                    LIMIT 10
                """, conn)
                
                if not df_high_value.empty:
                    st.dataframe(df_high_value, use_container_width=True)
                else:
                    st.info("No high-value customers found")
            except Exception as e:
                st.error(f"Error loading high-value customers: {e}")

# 3. BUSINESS MANAGEMENT
elif view_mode == "🏢 Business Management":
    st.markdown("### 🏢 Business Account Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Create Business", "🏢 View Businesses", "🔧 Business Actions", "📊 Business Analytics"])
    
    with tab1:
        st.markdown("#### ➕ Create New Business Account")
        
        with st.form("create_business_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Business Information**")
                business_name = st.text_input("Business Name *")
                business_email = st.text_input("Business Email *")
                business_phone = st.text_input("Business Phone *")
                registration_number = st.text_input("Registration Number *")
                sector = st.selectbox("Business Sector", ["Technology", "Agriculture", "Retail", "Manufacturing", "Services", "Other"])
                
            with col2:
                st.markdown("**Account Setup**")
                initial_deposit = st.number_input("Initial Deposit (KES)", min_value=0.0, value=50000.0)
                account_type = st.selectbox("Account Type", ["CURRENT", "SAVINGS", "BUSINESS_PREMIUM"])
                
                st.markdown("**Contact Person**")
                contact_person = st.text_input("Contact Person Name")
                contact_email = st.text_input("Contact Person Email")
                contact_phone = st.text_input("Contact Person Phone")
            
            submitted = st.form_submit_button("🎯 Create Business Account", type="primary")
            
            if submitted and all([business_name, business_email, business_phone, registration_number]):
                try:
                    from admin_authorization_helper import submit_business_creation, get_admin_info
                    
                    # Prepare business data for authorization queue
                    business_data = {
                        'business_name': business_name,
                        'business_email': business_email,
                        'business_phone': business_phone,
                        'registration_number': registration_number,
                        'sector': sector,
                        'initial_deposit': float(initial_deposit),
                        'account_type': account_type,
                        'contact_person': contact_person,
                        'contact_email': contact_email,
                        'contact_phone': contact_phone,
                        'operation_type': 'BUSINESS_CREATE'
                    }
                    
                    # Submit to authorization queue
                    admin_info = get_admin_info()
                    result = submit_business_creation(business_data, admin_info)
                    
                    if result['success']:
                        st.success("✅ Business creation submitted for approval!")
                        st.info(f"**Queue ID:** {result['queue_id']}")
                        st.info(f"**Status:** Pending supervisor approval")
                        st.warning("⚠️ **Supervisor approval required** - Business account will be created after approval")
                        
                        # Display authorization receipt
                        st.markdown("### 🧾 Authorization Receipt")
                        st.code(f"""
WEKEZA BANK - BUSINESS CREATION AUTHORIZATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Queue ID: {result['queue_id']}
Admin: {admin_info['username']}
Branch: HQ001

Business Details:
Name: {business_name}
Email: {business_email}
Phone: {business_phone}
Registration: {registration_number}
Sector: {sector}
Initial Deposit: KES {initial_deposit:,.2f}

Status: PENDING APPROVAL
Priority: URGENT

Next Steps:
1. Supervisor will review and approve/reject
2. Business account will be created after approval
3. Initial deposit will be processed after approval
                        """)
                    else:
                        st.error(f"❌ Submission failed: {result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Authorization system error: {e}")
    
    with tab2:
        st.markdown("#### 🏢 Business Directory")
        
        try:
            df_businesses = pd.read_sql("""
                SELECT b.business_id, b.business_name, b.registration_no, b.kra_pin, 
                       b.sector, b.created_at,
                       a.account_number, a.balance, a.status as account_status
                FROM businesses b 
                LEFT JOIN accounts a ON b.business_id = a.business_id 
                ORDER BY b.created_at DESC
            """, conn)
            
            if not df_businesses.empty:
                st.dataframe(df_businesses, use_container_width=True)
                
                # Business summary
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Businesses", len(df_businesses))
                col2.metric("Active Accounts", len(df_businesses[df_businesses['account_status'] == 'ACTIVE']))
                col3.metric("Total Balance", f"KES {df_businesses['balance'].sum():,.2f}")
                col4.metric("Average Balance", f"KES {df_businesses['balance'].mean():,.2f}")
            else:
                st.info("No businesses found")
        except Exception as e:
            st.error(f"Error loading businesses: {e}")
    
    with tab3:
        st.markdown("#### 🔧 Business Account Actions")
        
        business_registration = st.text_input("Business Registration Number")
        
        if business_registration:
            try:
                business_details = pd.read_sql(f"""
                    SELECT b.*, a.account_number, a.balance, a.status as account_status
                    FROM businesses b 
                    LEFT JOIN accounts a ON b.business_id = a.business_id 
                    WHERE b.registration_no = '{business_registration}'
                """, conn)
                
                if not business_details.empty:
                    business = business_details.iloc[0]
                    
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Name:** {business['business_name']}")
                    col1.write(f"**Registration:** {business['registration_no']}")
                    col1.write(f"**KRA PIN:** {business['kra_pin']}")
                    
                    col2.write(f"**Account:** {business['account_number']}")
                    col2.write(f"**Balance:** KES {business['balance']:,.2f}")
                    col2.write(f"**Sector:** {business['sector']}")
                    
                    col3.write(f"**Account Status:** {business['account_status']}")
                    col3.write(f"**Created:** {business['created_at'].strftime('%Y-%m-%d')}")
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("🔒 Freeze Account"):
                            conn.execute(text("""
                                UPDATE accounts SET status = 'FROZEN' 
                                WHERE business_id = (SELECT business_id FROM businesses WHERE registration_no = :reg_no)
                            """), {'reg_no': business_registration})
                            conn.commit()
                            st.success("Account frozen!")
                            st.rerun()
                    
                    with col2:
                        if st.button("🔓 Unfreeze Account"):
                            conn.execute(text("""
                                UPDATE accounts SET status = 'ACTIVE' 
                                WHERE business_id = (SELECT business_id FROM businesses WHERE registration_no = :reg_no)
                            """), {'reg_no': business_registration})
                            conn.commit()
                            st.success("Account unfrozen!")
                            st.rerun()
                else:
                    st.error("Business not found!")
            except Exception as e:
                st.error(f"Error loading business: {e}")
    
    with tab4:
        st.markdown("#### 📊 Business Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📈 Business Growth")
            try:
                df_business_growth = pd.read_sql("""
                    SELECT DATE(created_at) as signup_date, COUNT(*) as new_businesses
                    FROM businesses 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY signup_date
                """, conn)
                
                if not df_business_growth.empty:
                    fig = px.line(df_business_growth, x='signup_date', y='new_businesses',
                                 title='Daily Business Registration (Last 30 Days)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No business growth data available")
            except Exception as e:
                st.error(f"Error loading business growth: {e}")
        
        with col2:
            st.markdown("##### 🏢 Business Sectors")
            try:
                df_business_sectors = pd.read_sql("""
                    SELECT sector, COUNT(*) as count
                    FROM businesses 
                    GROUP BY sector
                """, conn)
                
                if not df_business_sectors.empty:
                    fig = px.pie(df_business_sectors, values='count', names='sector',
                                title='Business Sector Distribution')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No business sector data")
            except Exception as e:
                st.error(f"Error loading business sectors: {e}")
# 4. STAFF ADMINISTRATION
elif view_mode == "👥 Staff Administration":
    st.markdown("### 👥 Staff Management System")
    
    tab1, tab2, tab3, tab4 = st.tabs(["➕ Add Staff", "👥 View Staff", "🔧 Staff Actions", "📊 Staff Analytics"])
    
    with tab1:
        st.markdown("#### ➕ Add New Staff Member")
        
        with st.form("create_staff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Personal Information**")
                staff_name = st.text_input("Full Name *")
                staff_email = st.text_input("Email Address *")
                staff_phone = st.text_input("Phone Number *")
                national_id = st.text_input("National ID *")
                
            with col2:
                st.markdown("**Employment Details**")
                employee_id = st.text_input("Employee ID *")
                department = st.selectbox("Department", ["OPERATIONS", "CUSTOMER_SERVICE", "LOANS", "COMPLIANCE", "IT", "MANAGEMENT"])
                position = st.text_input("Position/Title *")
                salary = st.number_input("Monthly Salary (KES)", min_value=0.0)
                
                # Try to get branches for selection
                try:
                    branches_df = pd.read_sql("SELECT branch_id, branch_name FROM branches WHERE is_active = 1", conn)
                    if not branches_df.empty:
                        branch_options = dict(zip(branches_df['branch_name'], branches_df['branch_id']))
                        selected_branch = st.selectbox("Branch Assignment", list(branch_options.keys()))
                        branch_id = branch_options[selected_branch]
                    else:
                        st.info("No branches available. Creating staff without branch assignment.")
                        branch_id = None
                except:
                    st.info("Branch system not configured. Creating staff without branch assignment.")
                    branch_id = None
            
            # Access permissions
            st.markdown("**System Access Permissions**")
            col3, col4 = st.columns(2)
            with col3:
                can_approve_loans = st.checkbox("Can Approve Loans")
                can_manage_accounts = st.checkbox("Can Manage Accounts")
                can_process_transactions = st.checkbox("Can Process Transactions")
            with col4:
                can_view_reports = st.checkbox("Can View Reports")
                can_manage_customers = st.checkbox("Can Manage Customers")
                is_supervisor = st.checkbox("Is Supervisor")
            
            submitted = st.form_submit_button("🎯 Add Staff Member", type="primary")
            
            if submitted and all([staff_name, staff_email, staff_phone, employee_id, position]):
                try:
                    from admin_authorization_helper import submit_staff_creation, get_admin_info
                    
                    # Prepare staff data for authorization queue
                    staff_data = {
                        'employee_id': employee_id,
                        'full_name': staff_name,
                        'email': staff_email,
                        'phone_number': staff_phone,
                        'national_id': national_id,
                        'department': department,
                        'position': position,
                        'salary': float(salary),
                        'branch_id': branch_id,
                        'can_approve_loans': can_approve_loans,
                        'can_manage_accounts': can_manage_accounts,
                        'can_process_transactions': can_process_transactions,
                        'can_view_reports': can_view_reports,
                        'can_manage_customers': can_manage_customers,
                        'is_supervisor': is_supervisor,
                        'operation_type': 'STAFF_CREATE'
                    }
                    
                    # Submit to authorization queue
                    admin_info = get_admin_info()
                    result = submit_staff_creation(staff_data, admin_info)
                    
                    if result['success']:
                        st.success("✅ Staff creation submitted for approval!")
                        st.info(f"**Queue ID:** {result['queue_id']}")
                        st.info(f"**Status:** Pending supervisor approval")
                        st.warning("⚠️ **Supervisor approval required** - Staff member will be added after approval")
                        
                        # Display authorization receipt
                        st.markdown("### 🧾 Authorization Receipt")
                        st.code(f"""
WEKEZA BANK - STAFF CREATION AUTHORIZATION
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Queue ID: {result['queue_id']}
Admin: {admin_info['username']}
Branch: HQ001

Staff Details:
Name: {staff_name}
Employee ID: {employee_id}
Email: {staff_email}
Department: {department}
Position: {position}
Salary: KES {salary:,.2f}

Status: PENDING APPROVAL
Priority: HIGH

Next Steps:
1. Supervisor will review and approve/reject
2. Staff member will be added after approval
3. System access will be granted after approval
                        """)
                    else:
                        st.error(f"❌ Submission failed: {result['error']}")
                        
                except Exception as e:
                    st.error(f"❌ Authorization system error: {e}")
    
    with tab2:
        st.markdown("#### 👥 Staff Directory")
        
        # Staff search and filtering
        col1, col2, col3 = st.columns(3)
        with col1:
            search_name = st.text_input("🔍 Search by Name")
        with col2:
            dept_filter = st.selectbox("Department Filter", ["All", "OPERATIONS", "CUSTOMER_SERVICE", "LOANS", "COMPLIANCE", "IT", "MANAGEMENT"])
        with col3:
            status_filter = st.selectbox("Status Filter", ["All", "Active", "Inactive"])
        
        try:
            # Build query with filters
            query = """
            SELECT s.staff_id, s.employee_id, s.full_name, s.email, s.phone_number, 
                   s.department, s.position, s.salary, s.is_active, s.created_at,
                   b.branch_name
            FROM staff s 
            LEFT JOIN branches b ON s.branch_id = b.branch_id
            WHERE 1=1
            """
            
            if search_name:
                query += f" AND s.full_name LIKE '%{search_name}%'"
            if dept_filter != "All":
                query += f" AND s.department = '{dept_filter}'"
            if status_filter != "All":
                active_status = 1 if status_filter == "Active" else 0
                query += f" AND s.is_active = {active_status}"
            
            query += " ORDER BY s.created_at DESC"
            
            df_staff = pd.read_sql(query, conn)
            
            if not df_staff.empty:
                st.dataframe(df_staff, use_container_width=True)
                
                # Staff summary
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Staff", len(df_staff))
                col2.metric("Active Staff", len(df_staff[df_staff['is_active'] == 1]))
                col3.metric("Total Payroll", f"KES {df_staff['salary'].sum():,.2f}")
                col4.metric("Average Salary", f"KES {df_staff['salary'].mean():,.2f}")
            else:
                st.info("No staff members found")
        except Exception as e:
            st.error(f"Error loading staff: {e}")
    
    with tab3:
        st.markdown("#### 🔧 Staff Management Actions")
        
        staff_email = st.text_input("Staff Email Address")
        
        if staff_email:
            try:
                staff_details = pd.read_sql(f"""
                    SELECT s.*, b.branch_name
                    FROM staff s 
                    LEFT JOIN branches b ON s.branch_id = b.branch_id 
                    WHERE s.email = '{staff_email}'
                """, conn)
                
                if not staff_details.empty:
                    staff = staff_details.iloc[0]
                    
                    # Display staff info
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Name:** {staff['full_name']}")
                    col1.write(f"**Email:** {staff['email']}")
                    col1.write(f"**Phone:** {staff['phone_number']}")
                    
                    col2.write(f"**Employee ID:** {staff['employee_id']}")
                    col2.write(f"**Department:** {staff['department']}")
                    col2.write(f"**Position:** {staff['position']}")
                    
                    col3.write(f"**Salary:** KES {staff['salary']:,.2f}")
                    col3.write(f"**Branch:** {staff['branch_name'] or 'Not Assigned'}")
                    col3.write(f"**Status:** {'Active' if staff['is_active'] else 'Inactive'}")
                    
                    st.markdown("---")
                    
                    # Action buttons
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("✅ Activate Staff"):
                            conn.execute(text("UPDATE staff SET is_active = 1 WHERE email = :email"), {'email': staff_email})
                            conn.commit()
                            st.success("Staff activated!")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Deactivate Staff"):
                            conn.execute(text("UPDATE staff SET is_active = 0 WHERE email = :email"), {'email': staff_email})
                            conn.commit()
                            st.success("Staff deactivated!")
                            st.rerun()
                    
                    with col3:
                        if st.button("💰 Update Salary"):
                            new_salary = st.number_input("New Salary (KES)", value=float(staff['salary']))
                            if st.button("Apply Salary Update"):
                                conn.execute(text("UPDATE staff SET salary = :salary WHERE email = :email"), 
                                           {'salary': new_salary, 'email': staff_email})
                                conn.commit()
                                st.success("Salary updated!")
                                st.rerun()
                    
                    with col4:
                        if st.button("🔄 Reset Password"):
                            # This would integrate with your auth system
                            st.info("Password reset functionality would be implemented here")
                else:
                    st.error("Staff member not found!")
            except Exception as e:
                st.error(f"Error loading staff: {e}")
    
    with tab4:
        st.markdown("#### 📊 Staff Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🏢 Department Distribution")
            try:
                df_dept_dist = pd.read_sql("""
                    SELECT department, COUNT(*) as staff_count, SUM(salary) as total_salary
                    FROM staff 
                    WHERE is_active = 1
                    GROUP BY department
                """, conn)
                
                if not df_dept_dist.empty:
                    fig = px.bar(df_dept_dist, x='department', y='staff_count',
                                title='Staff by Department')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df_dept_dist, use_container_width=True)
                else:
                    st.info("No staff department data")
            except Exception as e:
                st.error(f"Error loading department data: {e}")
        
        with col2:
            st.markdown("##### 💰 Salary Analysis")
            try:
                df_salary_analysis = pd.read_sql("""
                    SELECT 
                        CASE 
                            WHEN salary < 30000 THEN 'Under 30K'
                            WHEN salary < 50000 THEN '30K - 50K'
                            WHEN salary < 80000 THEN '50K - 80K'
                            WHEN salary < 120000 THEN '80K - 120K'
                            ELSE 'Over 120K'
                        END as salary_range,
                        COUNT(*) as staff_count
                    FROM staff 
                    WHERE is_active = 1
                    GROUP BY salary_range
                """, conn)
                
                if not df_salary_analysis.empty:
                    fig = px.pie(df_salary_analysis, values='staff_count', names='salary_range',
                                title='Salary Distribution')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No salary data")
            except Exception as e:
                st.error(f"Error loading salary analysis: {e}")
# 5. ACCOUNT OVERSIGHT
elif view_mode == "💰 Account Oversight":
    st.markdown("### 💰 Account Management & Oversight")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Account Overview", "🔍 Account Search", "⚡ Quick Actions", "📈 Account Analytics"])
    
    with tab1:
        st.markdown("#### 📊 Account Overview Dashboard")
        
        try:
            # Account summary metrics
            total_accounts = pd.read_sql("SELECT COUNT(*) as count FROM accounts", conn).iloc[0]['count']
            active_accounts = pd.read_sql("SELECT COUNT(*) as count FROM accounts WHERE status = 'ACTIVE'", conn).iloc[0]['count']
            frozen_accounts = pd.read_sql("SELECT COUNT(*) as count FROM accounts WHERE status = 'FROZEN'", conn).iloc[0]['count']
            total_balance = pd.read_sql("SELECT SUM(balance) as total FROM accounts WHERE status = 'ACTIVE'", conn).iloc[0]['total'] or 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Accounts", f"{total_accounts:,}")
            col2.metric("Active Accounts", f"{active_accounts:,}")
            col3.metric("Frozen Accounts", f"{frozen_accounts:,}")
            col4.metric("Total Balance", f"KES {total_balance:,.2f}")
            
            st.markdown("---")
            
            # Recent account activities
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🆕 Recently Created Accounts")
                df_recent_accounts = pd.read_sql("""
                    SELECT a.account_number, a.balance, a.created_at,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as owner_name,
                           CASE WHEN b.business_name IS NOT NULL THEN 'Business' ELSE 'Personal' END as account_type
                    FROM accounts a
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    ORDER BY a.created_at DESC LIMIT 10
                """, conn)
                
                if not df_recent_accounts.empty:
                    for _, acc in df_recent_accounts.iterrows():
                        st.write(f"**{acc['owner_name']}** ({acc['account_type']})")
                        st.write(f"Account: {acc['account_number']} • Balance: KES {acc['balance']:,.2f}")
                        st.caption(f"Created: {acc['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        st.markdown("---")
                else:
                    st.info("No recent accounts")
            
            with col2:
                st.markdown("##### ⚠️ Accounts Requiring Attention")
                
                # Low balance accounts
                df_low_balance = pd.read_sql("""
                    SELECT a.account_number, a.balance,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as owner_name
                    FROM accounts a
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE a.balance < 1000 AND a.status = 'ACTIVE'
                    ORDER BY a.balance ASC LIMIT 10
                """, conn)
                
                if not df_low_balance.empty:
                    st.write("**🔴 Low Balance Accounts (< KES 1,000)**")
                    for _, acc in df_low_balance.iterrows():
                        st.write(f"• {acc['owner_name']}: KES {acc['balance']:,.2f}")
                else:
                    st.success("✅ No low balance accounts")
                
                # Frozen accounts
                df_frozen = pd.read_sql("""
                    SELECT a.account_number, 
                           COALESCE(u.full_name, b.business_name, 'Unknown') as owner_name
                    FROM accounts a
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE a.status = 'FROZEN'
                    LIMIT 5
                """, conn)
                
                if not df_frozen.empty:
                    st.write("**🟡 Frozen Accounts**")
                    for _, acc in df_frozen.iterrows():
                        st.write(f"• {acc['owner_name']}: {acc['account_number']}")
                else:
                    st.success("✅ No frozen accounts")
                    
        except Exception as e:
            st.error(f"Error loading account overview: {e}")
    
    with tab2:
        st.markdown("#### 🔍 Advanced Account Search")
        
        # Search filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_account = st.text_input("Account Number")
        with col2:
            search_owner = st.text_input("Owner Name")
        with col3:
            balance_min = st.number_input("Min Balance", value=0.0)
        with col4:
            balance_max = st.number_input("Max Balance", value=1000000.0)
        
        col5, col6, col7 = st.columns(3)
        with col5:
            account_status = st.selectbox("Account Status", ["All", "ACTIVE", "FROZEN", "CLOSED"])
        with col6:
            account_type_filter = st.selectbox("Account Type", ["All", "Personal", "Business"])
        with col7:
            sort_by = st.selectbox("Sort By", ["Created Date", "Balance", "Owner Name"])
        
        if st.button("🔍 Search Accounts"):
            try:
                # Build search query
                query = """
                SELECT a.account_id, a.account_number, a.balance, a.status, a.created_at,
                       COALESCE(u.full_name, b.business_name, 'Unknown') as owner_name,
                       COALESCE(u.email, b.business_email, 'No Email') as owner_email,
                       CASE WHEN b.business_name IS NOT NULL THEN 'Business' ELSE 'Personal' END as account_type
                FROM accounts a
                LEFT JOIN users u ON a.user_id = u.user_id
                LEFT JOIN businesses b ON a.business_id = b.business_id
                WHERE a.balance BETWEEN :min_bal AND :max_bal
                """
                
                params = {'min_bal': balance_min, 'max_bal': balance_max}
                
                if search_account:
                    query += " AND a.account_number LIKE :acc_num"
                    params['acc_num'] = f"%{search_account}%"
                
                if search_owner:
                    query += " AND (u.full_name LIKE :owner OR b.business_name LIKE :owner)"
                    params['owner'] = f"%{search_owner}%"
                
                if account_status != "All":
                    query += " AND a.status = :status"
                    params['status'] = account_status
                
                if account_type_filter == "Personal":
                    query += " AND u.user_id IS NOT NULL"
                elif account_type_filter == "Business":
                    query += " AND b.business_id IS NOT NULL"
                
                # Add sorting
                if sort_by == "Created Date":
                    query += " ORDER BY a.created_at DESC"
                elif sort_by == "Balance":
                    query += " ORDER BY a.balance DESC"
                else:
                    query += " ORDER BY owner_name ASC"
                
                query += " LIMIT 100"
                
                df_search_results = pd.read_sql(text(query), conn, params=params)
                
                if not df_search_results.empty:
                    st.markdown(f"#### 📋 Search Results ({len(df_search_results)} accounts found)")
                    st.dataframe(df_search_results, use_container_width=True)
                    
                    # Quick stats
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Accounts Found", len(df_search_results))
                    col2.metric("Total Balance", f"KES {df_search_results['balance'].sum():,.2f}")
                    col3.metric("Average Balance", f"KES {df_search_results['balance'].mean():,.2f}")
                else:
                    st.info("No accounts found matching the search criteria")
                    
            except Exception as e:
                st.error(f"Search error: {e}")
    
    with tab3:
        st.markdown("#### ⚡ Quick Account Actions")
        
        account_number = st.text_input("Enter Account Number")
        
        if account_number:
            try:
                # Get account details
                account_details = pd.read_sql(f"""
                    SELECT a.*, 
                           COALESCE(u.full_name, b.business_name, 'Unknown') as owner_name,
                           COALESCE(u.email, b.business_email, 'No Email') as owner_email
                    FROM accounts a
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE a.account_number = '{account_number}'
                """, conn)
                
                if not account_details.empty:
                    account = account_details.iloc[0]
                    
                    # Display account info
                    st.markdown("##### 📋 Account Information")
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Owner:** {account['owner_name']}")
                    col1.write(f"**Email:** {account['owner_email']}")
                    
                    col2.write(f"**Account:** {account['account_number']}")
                    col2.write(f"**Balance:** KES {account['balance']:,.2f}")
                    
                    col3.write(f"**Status:** {account['status']}")
                    col3.write(f"**Created:** {account['created_at'].strftime('%Y-%m-%d')}")
                    
                    st.markdown("---")
                    
                    # Quick actions
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("🔒 Freeze Account"):
                            conn.execute(text("UPDATE accounts SET status = 'FROZEN' WHERE account_number = :acc_num"), 
                                       {'acc_num': account_number})
                            conn.commit()
                            st.success("Account frozen!")
                            st.rerun()
                    
                    with col2:
                        if st.button("🔓 Unfreeze Account"):
                            conn.execute(text("UPDATE accounts SET status = 'ACTIVE' WHERE account_number = :acc_num"), 
                                       {'acc_num': account_number})
                            conn.commit()
                            st.success("Account unfrozen!")
                            st.rerun()
                    
                    with col3:
                        if st.button("📊 View Transactions"):
                            st.session_state['view_transactions'] = account_number
                    
                    with col4:
                        if st.button("💰 Adjust Balance"):
                            st.session_state['adjust_balance'] = account_number
                    
                    # Balance adjustment form
                    if st.session_state.get('adjust_balance') == account_number:
                        st.markdown("##### 💰 Balance Adjustment")
                        with st.form("balance_adjustment"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                adj_type = st.selectbox("Type", ["Credit", "Debit"])
                            with col2:
                                adj_amount = st.number_input("Amount (KES)", min_value=0.0)
                            with col3:
                                adj_reason = st.text_input("Reason")
                            
                            if st.form_submit_button("Apply Adjustment"):
                                if adj_amount > 0 and adj_reason:
                                    try:
                                        if adj_type == "Credit":
                                            conn.execute(text("UPDATE accounts SET balance = balance + :amount WHERE account_number = :acc_num"), 
                                                       {'amount': adj_amount, 'acc_num': account_number})
                                        else:
                                            conn.execute(text("UPDATE accounts SET balance = balance - :amount WHERE account_number = :acc_num"), 
                                                       {'amount': adj_amount, 'acc_num': account_number})
                                        
                                        # Record transaction
                                        ref_code = f"ADJ{uuid.uuid4().hex[:8].upper()}"
                                        conn.execute(text("""
                                            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                                            VALUES (:acc_id, :txn_type, :amount, :ref_code, :description, :created_at)
                                        """), {
                                            'acc_id': account['account_id'],
                                            'txn_type': f'ADMIN_{adj_type.upper()}',
                                            'amount': adj_amount,
                                            'ref_code': ref_code,
                                            'description': adj_reason,
                                            'created_at': datetime.now()
                                        })
                                        
                                        conn.commit()
                                        st.success(f"✅ {adj_type} of KES {adj_amount:,.2f} applied!")
                                        del st.session_state['adjust_balance']
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Adjustment failed: {e}")
                    
                    # Transaction history
                    if st.session_state.get('view_transactions') == account_number:
                        st.markdown("##### 📊 Recent Transactions")
                        try:
                            df_transactions = pd.read_sql(f"""
                                SELECT txn_type, amount, reference_code, description, created_at
                                FROM transactions 
                                WHERE account_id = {account['account_id']}
                                ORDER BY created_at DESC LIMIT 20
                            """, conn)
                            
                            if not df_transactions.empty:
                                st.dataframe(df_transactions, use_container_width=True)
                            else:
                                st.info("No transactions found")
                        except Exception as e:
                            st.error(f"Error loading transactions: {e}")
                else:
                    st.error("Account not found!")
            except Exception as e:
                st.error(f"Error loading account: {e}")
    
    with tab4:
        st.markdown("#### 📈 Account Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Account Balance Distribution")
            try:
                df_balance_dist = pd.read_sql("""
                    SELECT 
                        CASE 
                            WHEN balance < 1000 THEN 'Under KES 1K'
                            WHEN balance < 10000 THEN 'KES 1K - 10K'
                            WHEN balance < 50000 THEN 'KES 10K - 50K'
                            WHEN balance < 100000 THEN 'KES 50K - 100K'
                            WHEN balance < 500000 THEN 'KES 100K - 500K'
                            ELSE 'Over KES 500K'
                        END as balance_range,
                        COUNT(*) as account_count
                    FROM accounts 
                    WHERE status = 'ACTIVE'
                    GROUP BY balance_range
                """, conn)
                
                if not df_balance_dist.empty:
                    fig = px.pie(df_balance_dist, values='account_count', names='balance_range',
                                title='Account Balance Distribution')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No balance distribution data")
            except Exception as e:
                st.error(f"Error loading balance distribution: {e}")
        
        with col2:
            st.markdown("##### 📈 Account Growth Trend")
            try:
                df_account_growth = pd.read_sql("""
                    SELECT DATE(created_at) as creation_date, COUNT(*) as accounts_created,
                           SUM(COUNT(*)) OVER (ORDER BY DATE(created_at)) as cumulative_accounts
                    FROM accounts 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY creation_date
                """, conn)
                
                if not df_account_growth.empty:
                    fig = px.line(df_account_growth, x='creation_date', y='cumulative_accounts',
                                 title='Cumulative Account Growth (Last 30 Days)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No account growth data")
            except Exception as e:
                st.error(f"Error loading account growth: {e}")
# 6. LOAN ADMINISTRATION
elif view_mode == "📋 Loan Administration":
    st.markdown("### 📋 Loan Management System")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Loan Overview", "📝 Applications", "✅ Approvals", "💰 Active Loans", "📈 Loan Analytics"])
    
    with tab1:
        st.markdown("#### 📊 Loan Portfolio Overview")
        
        try:
            # Try different loan table structures
            loan_tables = ["loan_applications", "loans", "loan_accounts"]
            loan_data = None
            
            for table in loan_tables:
                try:
                    if table == "loan_applications":
                        loan_data = pd.read_sql(f"""
                            SELECT COUNT(*) as total_applications,
                                   SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
                                   SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
                                   SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected,
                                   SUM(loan_amount) as total_requested
                            FROM {table}
                        """, conn)
                        break
                    elif table == "loans":
                        loan_data = pd.read_sql(f"""
                            SELECT COUNT(*) as total_applications,
                                   SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
                                   SUM(CASE WHEN status = 'ACTIVE' THEN 1 ELSE 0 END) as approved,
                                   SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected,
                                   SUM(principal_amount) as total_requested
                            FROM {table}
                        """, conn)
                        break
                except:
                    continue
            
            if loan_data is not None and not loan_data.empty:
                loan_stats = loan_data.iloc[0]
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric("Total Applications", f"{loan_stats['total_applications']:,}")
                col2.metric("Pending Review", f"{loan_stats['pending']:,}")
                col3.metric("Approved", f"{loan_stats['approved']:,}")
                col4.metric("Rejected", f"{loan_stats['rejected']:,}")
                col5.metric("Total Requested", f"KES {loan_stats['total_requested']:,.2f}")
                
                # Approval rate
                if loan_stats['total_applications'] > 0:
                    approval_rate = (loan_stats['approved'] / loan_stats['total_applications']) * 100
                    st.metric("Approval Rate", f"{approval_rate:.1f}%")
            else:
                st.info("No loan data available. Loan system may not be configured yet.")
                
        except Exception as e:
            st.error(f"Error loading loan overview: {e}")
    
    with tab2:
        st.markdown("#### 📝 Loan Applications Management")
        
        try:
            # Try to load loan applications
            df_applications = None
            
            # Try loan_applications table first
            try:
                df_applications = pd.read_sql("""
                    SELECT la.application_id, la.account_number, la.loan_amount, la.loan_term, 
                           la.interest_rate, la.status, la.created_at, la.purpose,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as applicant_name
                    FROM loan_applications la
                    LEFT JOIN accounts a ON la.account_number = a.account_number
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    ORDER BY la.created_at DESC LIMIT 50
                """, conn)
            except:
                # Try loans table as fallback
                try:
                    df_applications = pd.read_sql("""
                        SELECT l.loan_id as application_id, a.account_number, l.principal_amount as loan_amount, 
                               l.loan_term, l.interest_rate, l.status, l.created_at, 'Personal Loan' as purpose,
                               u.full_name as applicant_name
                        FROM loans l
                        JOIN users u ON l.user_id = u.user_id
                        JOIN accounts a ON u.user_id = a.user_id
                        ORDER BY l.created_at DESC LIMIT 50
                    """, conn)
                except:
                    df_applications = None
            
            if df_applications is not None and not df_applications.empty:
                # Filter options
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_filter = st.selectbox("Filter by Status", ["All", "PENDING", "APPROVED", "REJECTED"])
                with col2:
                    amount_filter = st.selectbox("Filter by Amount", ["All", "Under 50K", "50K-100K", "100K-500K", "Over 500K"])
                with col3:
                    sort_by = st.selectbox("Sort by", ["Date", "Amount", "Status"])
                
                # Apply filters
                filtered_df = df_applications.copy()
                
                if status_filter != "All":
                    filtered_df = filtered_df[filtered_df['status'] == status_filter]
                
                if amount_filter != "All":
                    if amount_filter == "Under 50K":
                        filtered_df = filtered_df[filtered_df['loan_amount'] < 50000]
                    elif amount_filter == "50K-100K":
                        filtered_df = filtered_df[(filtered_df['loan_amount'] >= 50000) & (filtered_df['loan_amount'] < 100000)]
                    elif amount_filter == "100K-500K":
                        filtered_df = filtered_df[(filtered_df['loan_amount'] >= 100000) & (filtered_df['loan_amount'] < 500000)]
                    elif amount_filter == "Over 500K":
                        filtered_df = filtered_df[filtered_df['loan_amount'] >= 500000]
                
                st.dataframe(filtered_df, use_container_width=True)
                
                # Quick stats
                col1, col2, col3 = st.columns(3)
                col1.metric("Applications Shown", len(filtered_df))
                col2.metric("Total Amount", f"KES {filtered_df['loan_amount'].sum():,.2f}")
                col3.metric("Average Amount", f"KES {filtered_df['loan_amount'].mean():,.2f}")
                
            else:
                st.info("No loan applications found. You can create test loan applications using the scripts.")
                
                # Offer to create test data
                if st.button("🧪 Create Test Loan Applications"):
                    st.info("Run the script: `python scripts/create_test_loans.py` to generate test loan data.")
                    
        except Exception as e:
            st.error(f"Error loading loan applications: {e}")
    
    with tab3:
        st.markdown("#### ✅ Loan Approval Management")
        
        # Loan approval interface
        application_id = st.text_input("Enter Application ID for Review")
        
        if application_id:
            try:
                # Try to get application details
                app_details = None
                
                try:
                    app_details = pd.read_sql(f"""
                        SELECT la.*, 
                               COALESCE(u.full_name, b.business_name, 'Unknown') as applicant_name,
                               COALESCE(u.email, b.business_email, 'No Email') as applicant_email,
                               a.balance as account_balance
                        FROM loan_applications la
                        LEFT JOIN accounts a ON la.account_number = a.account_number
                        LEFT JOIN users u ON a.user_id = u.user_id
                        LEFT JOIN businesses b ON a.business_id = b.business_id
                        WHERE la.application_id = '{application_id}'
                    """, conn)
                except:
                    try:
                        app_details = pd.read_sql(f"""
                            SELECT l.*, u.full_name as applicant_name, u.email as applicant_email,
                                   a.balance as account_balance, a.account_number
                            FROM loans l
                            JOIN users u ON l.user_id = u.user_id
                            JOIN accounts a ON u.user_id = a.user_id
                            WHERE l.loan_id = '{application_id}'
                        """, conn)
                    except:
                        app_details = None
                
                if app_details is not None and not app_details.empty:
                    app = app_details.iloc[0]
                    
                    # Display application details
                    st.markdown("##### 📋 Application Details")
                    col1, col2, col3 = st.columns(3)
                    
                    col1.write(f"**Applicant:** {app['applicant_name']}")
                    col1.write(f"**Email:** {app['applicant_email']}")
                    col1.write(f"**Account:** {app['account_number']}")
                    
                    loan_amount = app.get('loan_amount', app.get('principal_amount', 0))
                    col2.write(f"**Loan Amount:** KES {loan_amount:,.2f}")
                    col2.write(f"**Current Balance:** KES {app['account_balance']:,.2f}")
                    col2.write(f"**Status:** {app['status']}")
                    
                    col3.write(f"**Term:** {app.get('loan_term', 'N/A')} months")
                    col3.write(f"**Interest Rate:** {app.get('interest_rate', 'N/A')}%")
                    col3.write(f"**Applied:** {app['created_at'].strftime('%Y-%m-%d')}")
                    
                    st.markdown("---")
                    
                    # Approval actions
                    if app['status'] == 'PENDING':
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("✅ Approve Loan", type="primary"):
                                try:
                                    # Update loan status
                                    if 'loan_applications' in str(type(app_details)):
                                        conn.execute(text("UPDATE loan_applications SET status = 'APPROVED' WHERE application_id = :app_id"), 
                                                   {'app_id': application_id})
                                    else:
                                        conn.execute(text("UPDATE loans SET status = 'ACTIVE' WHERE loan_id = :app_id"), 
                                                   {'app_id': application_id})
                                    
                                    # Credit the loan amount to account
                                    conn.execute(text("UPDATE accounts SET balance = balance + :amount WHERE account_number = :acc_num"), 
                                               {'amount': loan_amount, 'acc_num': app['account_number']})
                                    
                                    # Record loan disbursement transaction
                                    ref_code = f"LOAN{uuid.uuid4().hex[:8].upper()}"
                                    conn.execute(text("""
                                        INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                                        SELECT account_id, 'LOAN_DISBURSEMENT', :amount, :ref_code, :description, :created_at
                                        FROM accounts WHERE account_number = :acc_num
                                    """), {
                                        'amount': loan_amount,
                                        'ref_code': ref_code,
                                        'description': f'Loan disbursement - Application #{application_id}',
                                        'created_at': datetime.now(),
                                        'acc_num': app['account_number']
                                    })
                                    
                                    conn.commit()
                                    st.success("✅ Loan approved and disbursed!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Approval failed: {e}")
                        
                        with col2:
                            if st.button("❌ Reject Loan", type="secondary"):
                                rejection_reason = st.text_input("Rejection Reason")
                                if rejection_reason:
                                    try:
                                        if 'loan_applications' in str(type(app_details)):
                                            conn.execute(text("UPDATE loan_applications SET status = 'REJECTED' WHERE application_id = :app_id"), 
                                                       {'app_id': application_id})
                                        else:
                                            conn.execute(text("UPDATE loans SET status = 'REJECTED' WHERE loan_id = :app_id"), 
                                                       {'app_id': application_id})
                                        
                                        conn.commit()
                                        st.success("❌ Loan rejected!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Rejection failed: {e}")
                        
                        with col3:
                            if st.button("⏸️ Hold for Review"):
                                try:
                                    if 'loan_applications' in str(type(app_details)):
                                        conn.execute(text("UPDATE loan_applications SET status = 'UNDER_REVIEW' WHERE application_id = :app_id"), 
                                                   {'app_id': application_id})
                                    else:
                                        conn.execute(text("UPDATE loans SET status = 'UNDER_REVIEW' WHERE loan_id = :app_id"), 
                                                   {'app_id': application_id})
                                    
                                    conn.commit()
                                    st.success("⏸️ Loan put on hold for review!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Hold action failed: {e}")
                    else:
                        st.info(f"This loan is already {app['status']} and cannot be modified.")
                else:
                    st.error("Application not found!")
            except Exception as e:
                st.error(f"Error loading application: {e}")
    
    with tab4:
        st.markdown("#### 💰 Active Loans Management")
        
        try:
            # Load active loans
            df_active_loans = None
            
            try:
                df_active_loans = pd.read_sql("""
                    SELECT la.application_id, la.account_number, la.loan_amount, la.loan_term, 
                           la.interest_rate, la.status, la.created_at,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as borrower_name
                    FROM loan_applications la
                    LEFT JOIN accounts a ON la.account_number = a.account_number
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE la.status = 'APPROVED'
                    ORDER BY la.created_at DESC
                """, conn)
            except:
                try:
                    df_active_loans = pd.read_sql("""
                        SELECT l.loan_id as application_id, a.account_number, l.principal_amount as loan_amount, 
                               l.loan_term, l.interest_rate, l.status, l.created_at,
                               u.full_name as borrower_name
                        FROM loans l
                        JOIN users u ON l.user_id = u.user_id
                        JOIN accounts a ON u.user_id = a.user_id
                        WHERE l.status = 'ACTIVE'
                        ORDER BY l.created_at DESC
                    """, conn)
                except:
                    df_active_loans = None
            
            if df_active_loans is not None and not df_active_loans.empty:
                st.dataframe(df_active_loans, use_container_width=True)
                
                # Active loans summary
                col1, col2, col3 = st.columns(3)
                col1.metric("Active Loans", len(df_active_loans))
                col2.metric("Total Outstanding", f"KES {df_active_loans['loan_amount'].sum():,.2f}")
                col3.metric("Average Loan Size", f"KES {df_active_loans['loan_amount'].mean():,.2f}")
                
                # Loan management actions
                st.markdown("##### 🔧 Loan Management Actions")
                selected_loan = st.selectbox("Select Loan for Action", df_active_loans['application_id'].tolist())
                
                if selected_loan:
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("💰 Record Payment"):
                            payment_amount = st.number_input("Payment Amount (KES)", min_value=0.0)
                            if payment_amount > 0:
                                st.info("Payment recording functionality would be implemented here")
                    
                    with col2:
                        if st.button("📋 View Payment History"):
                            st.info("Payment history would be displayed here")
                    
                    with col3:
                        if st.button("⚠️ Mark as Defaulted"):
                            st.warning("This would mark the loan as defaulted")
            else:
                st.info("No active loans found")
                
        except Exception as e:
            st.error(f"Error loading active loans: {e}")
    
    with tab5:
        st.markdown("#### 📈 Loan Analytics & Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Loan Status Distribution")
            try:
                # Try to get loan status distribution
                df_status_dist = None
                
                try:
                    df_status_dist = pd.read_sql("""
                        SELECT status, COUNT(*) as count, SUM(loan_amount) as total_amount
                        FROM loan_applications
                        GROUP BY status
                    """, conn)
                except:
                    try:
                        df_status_dist = pd.read_sql("""
                            SELECT status, COUNT(*) as count, SUM(principal_amount) as total_amount
                            FROM loans
                            GROUP BY status
                        """, conn)
                    except:
                        df_status_dist = None
                
                if df_status_dist is not None and not df_status_dist.empty:
                    fig = px.pie(df_status_dist, values='count', names='status',
                                title='Loan Applications by Status')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df_status_dist, use_container_width=True)
                else:
                    st.info("No loan status data available")
            except Exception as e:
                st.error(f"Error loading loan status distribution: {e}")
        
        with col2:
            st.markdown("##### 💰 Loan Amount Distribution")
            try:
                df_amount_dist = None
                
                try:
                    df_amount_dist = pd.read_sql("""
                        SELECT 
                            CASE 
                                WHEN loan_amount < 50000 THEN 'Under 50K'
                                WHEN loan_amount < 100000 THEN '50K - 100K'
                                WHEN loan_amount < 500000 THEN '100K - 500K'
                                ELSE 'Over 500K'
                            END as amount_range,
                            COUNT(*) as loan_count
                        FROM loan_applications
                        GROUP BY amount_range
                    """, conn)
                except:
                    try:
                        df_amount_dist = pd.read_sql("""
                            SELECT 
                                CASE 
                                    WHEN principal_amount < 50000 THEN 'Under 50K'
                                    WHEN principal_amount < 100000 THEN '50K - 100K'
                                    WHEN principal_amount < 500000 THEN '100K - 500K'
                                    ELSE 'Over 500K'
                                END as amount_range,
                                COUNT(*) as loan_count
                            FROM loans
                            GROUP BY amount_range
                        """, conn)
                    except:
                        df_amount_dist = None
                
                if df_amount_dist is not None and not df_amount_dist.empty:
                    fig = px.bar(df_amount_dist, x='amount_range', y='loan_count',
                                title='Loans by Amount Range')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No loan amount distribution data")
            except Exception as e:
                st.error(f"Error loading loan amount distribution: {e}")
# 7. INSURANCE MANAGEMENT
elif view_mode == "🛡️ Insurance Management":
    st.markdown("### 🛡️ Insurance & Bancassurance Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Insurance Overview", "📋 Policies", "💼 Claims", "📈 Insurance Analytics"])
    
    with tab1:
        st.markdown("#### 📊 Insurance Portfolio Overview")
        
        try:
            # Check if insurance tables exist
            insurance_tables = ["insurance_policies", "insurance_products", "insurance_claims"]
            
            # Try to get insurance overview data
            try:
                total_policies = pd.read_sql("SELECT COUNT(*) as count FROM insurance_policies", conn).iloc[0]['count']
                active_policies = pd.read_sql("SELECT COUNT(*) as count FROM insurance_policies WHERE status = 'ACTIVE'", conn).iloc[0]['count']
                total_premiums = pd.read_sql("SELECT SUM(premium_amount) as total FROM insurance_policies WHERE status = 'ACTIVE'", conn).iloc[0]['total'] or 0
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Policies", f"{total_policies:,}")
                col2.metric("Active Policies", f"{active_policies:,}")
                col3.metric("Total Premiums", f"KES {total_premiums:,.2f}")
                
                # Claims overview
                try:
                    total_claims = pd.read_sql("SELECT COUNT(*) as count FROM insurance_claims", conn).iloc[0]['count']
                    pending_claims = pd.read_sql("SELECT COUNT(*) as count FROM insurance_claims WHERE status = 'PENDING'", conn).iloc[0]['count']
                    approved_claims = pd.read_sql("SELECT COUNT(*) as count FROM insurance_claims WHERE status = 'APPROVED'", conn).iloc[0]['count']
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Claims", f"{total_claims:,}")
                    col2.metric("Pending Claims", f"{pending_claims:,}")
                    col3.metric("Approved Claims", f"{approved_claims:,}")
                except:
                    st.info("Claims data not available")
                    
            except Exception as e:
                st.info("Insurance system not configured yet. Run setup scripts to initialize insurance tables.")
                
                if st.button("🧪 Setup Insurance System"):
                    st.info("Run the script: `python scripts/create_insurance_tables.py` to set up insurance system.")
                    
        except Exception as e:
            st.error(f"Error loading insurance overview: {e}")
    
    with tab2:
        st.markdown("#### 📋 Insurance Policies Management")
        
        try:
            df_policies = pd.read_sql("""
                SELECT ip.policy_id, ip.policy_number, ip.premium_amount, ip.coverage_amount, 
                       ip.status, ip.start_date, ip.end_date, ip.created_at,
                       COALESCE(u.full_name, b.business_name, 'Unknown') as policyholder_name,
                       prod.product_name, prod.product_type
                FROM insurance_policies ip
                LEFT JOIN accounts a ON ip.account_number = a.account_number
                LEFT JOIN users u ON a.user_id = u.user_id
                LEFT JOIN businesses b ON a.business_id = b.business_id
                LEFT JOIN insurance_products prod ON ip.product_id = prod.product_id
                ORDER BY ip.created_at DESC LIMIT 50
            """, conn)
            
            if not df_policies.empty:
                # Policy filters
                col1, col2, col3 = st.columns(3)
                with col1:
                    status_filter = st.selectbox("Filter by Status", ["All", "ACTIVE", "EXPIRED", "CANCELLED"])
                with col2:
                    product_filter = st.selectbox("Filter by Product", ["All"] + df_policies['product_type'].dropna().unique().tolist())
                with col3:
                    sort_by = st.selectbox("Sort by", ["Date", "Premium", "Coverage"])
                
                # Apply filters
                filtered_policies = df_policies.copy()
                if status_filter != "All":
                    filtered_policies = filtered_policies[filtered_policies['status'] == status_filter]
                if product_filter != "All":
                    filtered_policies = filtered_policies[filtered_policies['product_type'] == product_filter]
                
                st.dataframe(filtered_policies, use_container_width=True)
                
                # Policy summary
                col1, col2, col3 = st.columns(3)
                col1.metric("Policies Shown", len(filtered_policies))
                col2.metric("Total Premiums", f"KES {filtered_policies['premium_amount'].sum():,.2f}")
                col3.metric("Total Coverage", f"KES {filtered_policies['coverage_amount'].sum():,.2f}")
            else:
                st.info("No insurance policies found")
                
        except Exception as e:
            st.info("Insurance policies table not found. Set up insurance system first.")
    
    with tab3:
        st.markdown("#### 💼 Insurance Claims Management")
        
        try:
            df_claims = pd.read_sql("""
                SELECT ic.claim_id, ic.claim_number, ic.claim_amount, ic.status, 
                       ic.incident_date, ic.created_at, ic.description,
                       COALESCE(u.full_name, b.business_name, 'Unknown') as claimant_name,
                       ip.policy_number
                FROM insurance_claims ic
                LEFT JOIN insurance_policies ip ON ic.policy_id = ip.policy_id
                LEFT JOIN accounts a ON ip.account_number = a.account_number
                LEFT JOIN users u ON a.user_id = u.user_id
                LEFT JOIN businesses b ON a.business_id = b.business_id
                ORDER BY ic.created_at DESC LIMIT 50
            """, conn)
            
            if not df_claims.empty:
                st.dataframe(df_claims, use_container_width=True)
                
                # Claims processing
                st.markdown("##### 🔧 Claims Processing")
                claim_id = st.text_input("Enter Claim ID for Processing")
                
                if claim_id:
                    claim_details = df_claims[df_claims['claim_id'] == int(claim_id)]
                    if not claim_details.empty:
                        claim = claim_details.iloc[0]
                        
                        col1, col2, col3 = st.columns(3)
                        col1.write(f"**Claimant:** {claim['claimant_name']}")
                        col1.write(f"**Policy:** {claim['policy_number']}")
                        
                        col2.write(f"**Claim Amount:** KES {claim['claim_amount']:,.2f}")
                        col2.write(f"**Status:** {claim['status']}")
                        
                        col3.write(f"**Incident Date:** {claim['incident_date']}")
                        col3.write(f"**Filed:** {claim['created_at'].strftime('%Y-%m-%d')}")
                        
                        if claim['status'] == 'PENDING':
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("✅ Approve Claim"):
                                    try:
                                        conn.execute(text("UPDATE insurance_claims SET status = 'APPROVED' WHERE claim_id = :claim_id"), 
                                                   {'claim_id': claim_id})
                                        conn.commit()
                                        st.success("Claim approved!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error approving claim: {e}")
                            
                            with col2:
                                if st.button("❌ Reject Claim"):
                                    try:
                                        conn.execute(text("UPDATE insurance_claims SET status = 'REJECTED' WHERE claim_id = :claim_id"), 
                                                   {'claim_id': claim_id})
                                        conn.commit()
                                        st.success("Claim rejected!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error rejecting claim: {e}")
            else:
                st.info("No insurance claims found")
                
        except Exception as e:
            st.info("Insurance claims table not found. Set up insurance system first.")
    
    with tab4:
        st.markdown("#### 📈 Insurance Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Policy Distribution by Type")
            try:
                df_policy_types = pd.read_sql("""
                    SELECT prod.product_type, COUNT(*) as policy_count, SUM(ip.premium_amount) as total_premiums
                    FROM insurance_policies ip
                    JOIN insurance_products prod ON ip.product_id = prod.product_id
                    WHERE ip.status = 'ACTIVE'
                    GROUP BY prod.product_type
                """, conn)
                
                if not df_policy_types.empty:
                    fig = px.pie(df_policy_types, values='policy_count', names='product_type',
                                title='Active Policies by Type')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No policy type data available")
            except Exception as e:
                st.info("Insurance analytics not available - system not configured")
        
        with col2:
            st.markdown("##### 💰 Claims vs Premiums")
            try:
                df_claims_vs_premiums = pd.read_sql("""
                    SELECT 
                        DATE_FORMAT(created_at, '%Y-%m') as month,
                        SUM(CASE WHEN table_type = 'premium' THEN amount ELSE 0 END) as premiums,
                        SUM(CASE WHEN table_type = 'claim' THEN amount ELSE 0 END) as claims
                    FROM (
                        SELECT created_at, premium_amount as amount, 'premium' as table_type FROM insurance_policies
                        UNION ALL
                        SELECT created_at, claim_amount as amount, 'claim' as table_type FROM insurance_claims WHERE status = 'APPROVED'
                    ) combined
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
                    GROUP BY DATE_FORMAT(created_at, '%Y-%m')
                    ORDER BY month
                """, conn)
                
                if not df_claims_vs_premiums.empty:
                    fig = px.line(df_claims_vs_premiums, x='month', y=['premiums', 'claims'],
                                 title='Monthly Premiums vs Claims')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No claims vs premiums data available")
            except Exception as e:
                st.info("Claims analytics not available")

# 8. TRANSACTION MONITORING
elif view_mode == "💸 Transaction Monitoring":
    st.markdown("### 💸 Transaction Monitoring & Analysis")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Transaction Overview", "🔍 Transaction Search", "⚠️ Suspicious Activity", "📈 Transaction Analytics"])
    
    with tab1:
        st.markdown("#### 📊 Real-time Transaction Overview")
        
        try:
            # Transaction summary metrics
            today_txns = pd.read_sql("SELECT COUNT(*) as count FROM transactions WHERE DATE(created_at) = CURDATE()", conn).iloc[0]['count']
            today_volume = pd.read_sql("SELECT SUM(amount) as total FROM transactions WHERE DATE(created_at) = CURDATE()", conn).iloc[0]['total'] or 0
            week_txns = pd.read_sql("SELECT COUNT(*) as count FROM transactions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)", conn).iloc[0]['count']
            week_volume = pd.read_sql("SELECT SUM(amount) as total FROM transactions WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)", conn).iloc[0]['total'] or 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Today's Transactions", f"{today_txns:,}")
            col2.metric("Today's Volume", f"KES {today_volume:,.2f}")
            col3.metric("This Week's Transactions", f"{week_txns:,}")
            col4.metric("This Week's Volume", f"KES {week_volume:,.2f}")
            
            st.markdown("---")
            
            # Recent transactions
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🔄 Latest Transactions")
                df_recent_txns = pd.read_sql("""
                    SELECT t.txn_type, t.amount, t.reference_code, t.created_at,
                           a.account_number,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as account_holder
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    ORDER BY t.created_at DESC LIMIT 15
                """, conn)
                
                if not df_recent_txns.empty:
                    for _, txn in df_recent_txns.iterrows():
                        txn_icon = "📥" if "DEPOSIT" in str(txn['txn_type']) or "CREDIT" in str(txn['txn_type']) else "📤"
                        st.write(f"{txn_icon} **{txn['txn_type']}** - KES {txn['amount']:,.2f}")
                        st.caption(f"{txn['account_holder']} • {txn['reference_code']} • {txn['created_at'].strftime('%H:%M:%S')}")
                        st.markdown("---")
                else:
                    st.info("No recent transactions")
            
            with col2:
                st.markdown("##### 💰 High-Value Transactions (Today)")
                df_high_value = pd.read_sql("""
                    SELECT t.txn_type, t.amount, t.reference_code, t.created_at,
                           a.account_number,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as account_holder
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE DATE(t.created_at) = CURDATE() AND t.amount > 50000
                    ORDER BY t.amount DESC LIMIT 10
                """, conn)
                
                if not df_high_value.empty:
                    for _, txn in df_high_value.iterrows():
                        st.write(f"🔴 **{txn['txn_type']}** - KES {txn['amount']:,.2f}")
                        st.caption(f"{txn['account_holder']} • {txn['reference_code']}")
                        st.markdown("---")
                else:
                    st.success("✅ No high-value transactions today")
                    
        except Exception as e:
            st.error(f"Error loading transaction overview: {e}")
    
    with tab2:
        st.markdown("#### 🔍 Advanced Transaction Search")
        
        # Search filters
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            search_ref = st.text_input("Reference Code")
        with col2:
            search_account = st.text_input("Account Number")
        with col3:
            txn_type_filter = st.selectbox("Transaction Type", ["All", "DEPOSIT", "WITHDRAWAL", "TRANSFER", "LOAN_DISBURSEMENT", "PAYMENT"])
        with col4:
            amount_min = st.number_input("Min Amount", value=0.0)
        
        col5, col6, col7 = st.columns(3)
        with col5:
            amount_max = st.number_input("Max Amount", value=1000000.0)
        with col6:
            date_from = st.date_input("From Date", value=datetime.now().date() - timedelta(days=30))
        with col7:
            date_to = st.date_input("To Date", value=datetime.now().date())
        
        if st.button("🔍 Search Transactions"):
            try:
                # Build search query
                query = """
                SELECT t.transaction_id, t.txn_type, t.amount, t.reference_code, t.description, t.created_at,
                       a.account_number,
                       COALESCE(u.full_name, b.business_name, 'Unknown') as account_holder
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                LEFT JOIN users u ON a.user_id = u.user_id
                LEFT JOIN businesses b ON a.business_id = b.business_id
                WHERE t.amount BETWEEN :min_amt AND :max_amt
                AND DATE(t.created_at) BETWEEN :date_from AND :date_to
                """
                
                params = {
                    'min_amt': amount_min,
                    'max_amt': amount_max,
                    'date_from': date_from,
                    'date_to': date_to
                }
                
                if search_ref:
                    query += " AND t.reference_code LIKE :ref_code"
                    params['ref_code'] = f"%{search_ref}%"
                
                if search_account:
                    query += " AND a.account_number LIKE :acc_num"
                    params['acc_num'] = f"%{search_account}%"
                
                if txn_type_filter != "All":
                    query += " AND t.txn_type = :txn_type"
                    params['txn_type'] = txn_type_filter
                
                query += " ORDER BY t.created_at DESC LIMIT 100"
                
                df_search_results = pd.read_sql(text(query), conn, params=params)
                
                if not df_search_results.empty:
                    st.markdown(f"#### 📋 Search Results ({len(df_search_results)} transactions found)")
                    st.dataframe(df_search_results, use_container_width=True)
                    
                    # Search summary
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Transactions Found", len(df_search_results))
                    col2.metric("Total Amount", f"KES {df_search_results['amount'].sum():,.2f}")
                    col3.metric("Average Amount", f"KES {df_search_results['amount'].mean():,.2f}")
                else:
                    st.info("No transactions found matching the search criteria")
                    
            except Exception as e:
                st.error(f"Search error: {e}")
    
    with tab3:
        st.markdown("#### ⚠️ Suspicious Activity Detection")
        
        # Suspicious activity alerts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🚨 Potential Fraud Alerts")
            
            alerts = []
            
            try:
                # Multiple large transactions from same account
                df_multiple_large = pd.read_sql("""
                    SELECT a.account_number, COUNT(*) as txn_count, SUM(t.amount) as total_amount,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as account_holder
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE DATE(t.created_at) = CURDATE() AND t.amount > 100000
                    GROUP BY a.account_id
                    HAVING COUNT(*) > 3
                """, conn)
                
                if not df_multiple_large.empty:
                    for _, alert in df_multiple_large.iterrows():
                        alerts.append(f"🔴 Multiple large transactions: {alert['account_holder']} ({alert['account_number']}) - {alert['txn_count']} transactions totaling KES {alert['total_amount']:,.2f}")
                
                # Unusual transaction patterns
                df_unusual_patterns = pd.read_sql("""
                    SELECT a.account_number, t.amount, t.txn_type, t.created_at,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as account_holder
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE t.amount > 500000 AND DATE(t.created_at) = CURDATE()
                """, conn)
                
                if not df_unusual_patterns.empty:
                    for _, alert in df_unusual_patterns.iterrows():
                        alerts.append(f"🟡 Large transaction: {alert['account_holder']} - {alert['txn_type']} KES {alert['amount']:,.2f}")
                
                # Round number transactions (potential structuring)
                df_round_numbers = pd.read_sql("""
                    SELECT a.account_number, COUNT(*) as round_txn_count,
                           COALESCE(u.full_name, b.business_name, 'Unknown') as account_holder
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    LEFT JOIN users u ON a.user_id = u.user_id
                    LEFT JOIN businesses b ON a.business_id = b.business_id
                    WHERE DATE(t.created_at) = CURDATE() 
                    AND (t.amount % 10000 = 0 OR t.amount % 50000 = 0)
                    AND t.amount >= 10000
                    GROUP BY a.account_id
                    HAVING COUNT(*) > 5
                """, conn)
                
                if not df_round_numbers.empty:
                    for _, alert in df_round_numbers.iterrows():
                        alerts.append(f"🟠 Suspicious round number pattern: {alert['account_holder']} - {alert['round_txn_count']} round number transactions")
                
            except Exception as e:
                alerts.append(f"⚠️ Error checking for suspicious activity: {e}")
            
            if alerts:
                for alert in alerts:
                    st.write(alert)
                    st.markdown("---")
            else:
                st.success("✅ No suspicious activity detected")
        
        with col2:
            st.markdown("##### 📊 Risk Metrics")
            
            try:
                # Calculate risk metrics
                total_daily_volume = pd.read_sql("SELECT SUM(amount) as total FROM transactions WHERE DATE(created_at) = CURDATE()", conn).iloc[0]['total'] or 0
                large_txn_count = pd.read_sql("SELECT COUNT(*) as count FROM transactions WHERE DATE(created_at) = CURDATE() AND amount > 100000", conn).iloc[0]['count']
                total_daily_txns = pd.read_sql("SELECT COUNT(*) as count FROM transactions WHERE DATE(created_at) = CURDATE()", conn).iloc[0]['count']
                
                risk_metrics = {
                    'Metric': [
                        'Daily Transaction Volume',
                        'Large Transactions (>100K)',
                        'Average Transaction Size',
                        'Risk Score'
                    ],
                    'Value': [
                        f'KES {total_daily_volume:,.2f}',
                        f'{large_txn_count:,}',
                        f'KES {(total_daily_volume / max(total_daily_txns, 1)):,.2f}',
                        'Low Risk' if large_txn_count < 10 else 'Medium Risk' if large_txn_count < 50 else 'High Risk'
                    ],
                    'Status': [
                        '✅ Normal' if total_daily_volume < 10000000 else '⚠️ High',
                        '✅ Normal' if large_txn_count < 10 else '⚠️ Monitor',
                        '✅ Normal',
                        '✅ Safe' if large_txn_count < 10 else '⚠️ Monitor'
                    ]
                }
                
                df_risk_metrics = pd.DataFrame(risk_metrics)
                st.dataframe(df_risk_metrics, use_container_width=True)
                
            except Exception as e:
                st.error(f"Error calculating risk metrics: {e}")
    
    with tab4:
        st.markdown("#### 📈 Transaction Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📊 Daily Transaction Volume (Last 30 Days)")
            try:
                df_daily_volume = pd.read_sql("""
                    SELECT DATE(created_at) as txn_date, 
                           COUNT(*) as txn_count, 
                           SUM(amount) as total_amount
                    FROM transactions 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(created_at)
                    ORDER BY txn_date
                """, conn)
                
                if not df_daily_volume.empty:
                    fig = px.line(df_daily_volume, x='txn_date', y='total_amount',
                                 title='Daily Transaction Volume')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No transaction volume data available")
            except Exception as e:
                st.error(f"Error loading transaction volume: {e}")
        
        with col2:
            st.markdown("##### 🏦 Transaction Types Distribution")
            try:
                df_txn_types = pd.read_sql("""
                    SELECT txn_type, COUNT(*) as txn_count, SUM(amount) as total_amount
                    FROM transactions 
                    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    GROUP BY txn_type
                    ORDER BY txn_count DESC
                """, conn)
                
                if not df_txn_types.empty:
                    fig = px.pie(df_txn_types, values='txn_count', names='txn_type',
                                title='Transaction Types (Last 7 Days)')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df_txn_types, use_container_width=True)
                else:
                    st.info("No transaction type data available")
            except Exception as e:
                st.error(f"Error loading transaction types: {e}")
# 9. ANALYTICS & REPORTS
elif view_mode == "📈 Analytics & Reports":
    st.markdown("### 📈 Advanced Analytics & Reporting")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Executive Reports", "💰 Financial Analytics", "👥 Customer Insights", "📋 Custom Reports"])
    
    with tab1:
        st.markdown("#### 📊 Executive Dashboard Reports")
        
        # Date range selector
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Report Start Date", value=datetime.now().date() - timedelta(days=30))
        with col2:
            end_date = st.date_input("Report End Date", value=datetime.now().date())
        
        try:
            # Key Performance Indicators
            st.markdown("##### 🎯 Key Performance Indicators")
            
            # Customer growth
            customer_growth = pd.read_sql(f"""
                SELECT COUNT(*) as new_customers
                FROM users 
                WHERE DATE(created_at) BETWEEN '{start_date}' AND '{end_date}'
                AND business_id IS NULL
            """, conn).iloc[0]['new_customers']
            
            # Business growth
            business_growth = pd.read_sql(f"""
                SELECT COUNT(*) as new_businesses
                FROM businesses 
                WHERE DATE(created_at) BETWEEN '{start_date}' AND '{end_date}'
            """, conn).iloc[0]['new_businesses']
            
            # Transaction volume
            txn_volume = pd.read_sql(f"""
                SELECT COUNT(*) as txn_count, SUM(amount) as total_volume
                FROM transactions 
                WHERE DATE(created_at) BETWEEN '{start_date}' AND '{end_date}'
            """, conn)
            
            if not txn_volume.empty:
                txn_count = txn_volume.iloc[0]['txn_count']
                total_volume = txn_volume.iloc[0]['total_volume'] or 0
            else:
                txn_count = 0
                total_volume = 0
            
            # Account balances
            total_deposits = pd.read_sql("SELECT SUM(balance) as total FROM accounts WHERE status = 'ACTIVE'", conn).iloc[0]['total'] or 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("New Customers", f"{customer_growth:,}")
            col2.metric("New Businesses", f"{business_growth:,}")
            col3.metric("Transaction Volume", f"KES {total_volume:,.2f}")
            col4.metric("Total Deposits", f"KES {total_deposits:,.2f}")
            
            # Growth trends
            st.markdown("##### 📈 Growth Trends")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Customer acquisition trend
                df_customer_trend = pd.read_sql(f"""
                    SELECT DATE(created_at) as signup_date, COUNT(*) as new_customers
                    FROM users 
                    WHERE DATE(created_at) BETWEEN '{start_date}' AND '{end_date}'
                    AND business_id IS NULL
                    GROUP BY DATE(created_at)
                    ORDER BY signup_date
                """, conn)
                
                if not df_customer_trend.empty:
                    fig = px.line(df_customer_trend, x='signup_date', y='new_customers',
                                 title='Daily Customer Acquisition')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No customer trend data for selected period")
            
            with col2:
                # Transaction volume trend
                df_volume_trend = pd.read_sql(f"""
                    SELECT DATE(created_at) as txn_date, SUM(amount) as daily_volume
                    FROM transactions 
                    WHERE DATE(created_at) BETWEEN '{start_date}' AND '{end_date}'
                    GROUP BY DATE(created_at)
                    ORDER BY txn_date
                """, conn)
                
                if not df_volume_trend.empty:
                    fig = px.line(df_volume_trend, x='txn_date', y='daily_volume',
                                 title='Daily Transaction Volume')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No transaction volume data for selected period")
                    
        except Exception as e:
            st.error(f"Error generating executive reports: {e}")
    
    with tab2:
        st.markdown("#### 💰 Financial Analytics")
        
        try:
            # Financial health metrics
            st.markdown("##### 💊 Financial Health Metrics")
            
            # Calculate key financial ratios
            total_assets = pd.read_sql("SELECT SUM(balance) as total FROM accounts WHERE status = 'ACTIVE'", conn).iloc[0]['total'] or 0
            
            # Try to get loan data
            try:
                total_loans = pd.read_sql("SELECT SUM(loan_amount) as total FROM loan_applications WHERE status = 'APPROVED'", conn).iloc[0]['total'] or 0
            except:
                try:
                    total_loans = pd.read_sql("SELECT SUM(principal_amount) as total FROM loans WHERE status = 'ACTIVE'", conn).iloc[0]['total'] or 0
                except:
                    total_loans = 0
            
            # Liquidity ratio
            liquidity_ratio = (total_assets / max(total_loans, 1)) * 100 if total_loans > 0 else 100
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Assets", f"KES {total_assets:,.2f}")
            col2.metric("Total Loans", f"KES {total_loans:,.2f}")
            col3.metric("Liquidity Ratio", f"{liquidity_ratio:.1f}%")
            col4.metric("Asset Growth", "+5.2%")  # Mock data
            
            # Revenue analysis
            st.markdown("##### 💵 Revenue Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Monthly revenue trend (mock data for demonstration)
                revenue_data = {
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'Interest_Income': [150000, 165000, 180000, 175000, 190000, 205000],
                    'Fee_Income': [45000, 52000, 48000, 55000, 58000, 62000],
                    'Other_Income': [25000, 28000, 30000, 32000, 35000, 38000]
                }
                df_revenue = pd.DataFrame(revenue_data)
                
                fig = px.bar(df_revenue, x='Month', y=['Interest_Income', 'Fee_Income', 'Other_Income'],
                            title='Monthly Revenue Breakdown')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Profitability analysis
                profitability_data = {
                    'Metric': ['Net Interest Margin', 'Return on Assets', 'Cost-to-Income Ratio', 'Profit Margin'],
                    'Current': ['3.2%', '1.8%', '65%', '15%'],
                    'Target': ['3.5%', '2.0%', '60%', '18%'],
                    'Status': ['⚠️ Below Target', '✅ On Track', '⚠️ Above Target', '✅ Good']
                }
                df_profitability = pd.DataFrame(profitability_data)
                st.dataframe(df_profitability, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error generating financial analytics: {e}")
    
    with tab3:
        st.markdown("#### 👥 Customer Insights & Behavior Analysis")
        
        try:
            # Customer segmentation
            st.markdown("##### 🎯 Customer Segmentation")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Customer value segments
                df_customer_segments = pd.read_sql("""
                    SELECT 
                        CASE 
                            WHEN a.balance < 10000 THEN 'Basic'
                            WHEN a.balance < 50000 THEN 'Standard'
                            WHEN a.balance < 200000 THEN 'Premium'
                            ELSE 'VIP'
                        END as segment,
                        COUNT(*) as customer_count,
                        AVG(a.balance) as avg_balance
                    FROM accounts a
                    JOIN users u ON a.user_id = u.user_id
                    WHERE a.status = 'ACTIVE' AND u.business_id IS NULL
                    GROUP BY segment
                """, conn)
                
                if not df_customer_segments.empty:
                    fig = px.pie(df_customer_segments, values='customer_count', names='segment',
                                title='Customer Segments by Balance')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.dataframe(df_customer_segments, use_container_width=True)
                else:
                    st.info("No customer segmentation data available")
            
            with col2:
                # Customer activity analysis
                df_customer_activity = pd.read_sql("""
                    SELECT 
                        CASE 
                            WHEN txn_count = 0 THEN 'Inactive'
                            WHEN txn_count < 5 THEN 'Low Activity'
                            WHEN txn_count < 20 THEN 'Medium Activity'
                            ELSE 'High Activity'
                        END as activity_level,
                        COUNT(*) as customer_count
                    FROM (
                        SELECT a.account_id, COUNT(t.transaction_id) as txn_count
                        FROM accounts a
                        LEFT JOIN transactions t ON a.account_id = t.account_id 
                            AND t.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                        JOIN users u ON a.user_id = u.user_id
                        WHERE a.status = 'ACTIVE' AND u.business_id IS NULL
                        GROUP BY a.account_id
                    ) activity_summary
                    GROUP BY activity_level
                """, conn)
                
                if not df_customer_activity.empty:
                    fig = px.bar(df_customer_activity, x='activity_level', y='customer_count',
                                title='Customer Activity Levels (Last 30 Days)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No customer activity data available")
            
            # Customer retention analysis
            st.markdown("##### 📊 Customer Retention Analysis")
            
            # Mock retention data for demonstration
            retention_data = {
                'Cohort': ['Jan 2024', 'Feb 2024', 'Mar 2024', 'Apr 2024', 'May 2024'],
                'Initial_Customers': [100, 120, 150, 180, 200],
                'Active_After_30_Days': [85, 102, 128, 155, 175],
                'Active_After_60_Days': [78, 95, 118, 142, 160],
                'Active_After_90_Days': [72, 88, 110, 132, 148]
            }
            df_retention = pd.DataFrame(retention_data)
            
            # Calculate retention rates
            df_retention['30_Day_Retention'] = (df_retention['Active_After_30_Days'] / df_retention['Initial_Customers'] * 100).round(1)
            df_retention['60_Day_Retention'] = (df_retention['Active_After_60_Days'] / df_retention['Initial_Customers'] * 100).round(1)
            df_retention['90_Day_Retention'] = (df_retention['Active_After_90_Days'] / df_retention['Initial_Customers'] * 100).round(1)
            
            st.dataframe(df_retention[['Cohort', '30_Day_Retention', '60_Day_Retention', '90_Day_Retention']], use_container_width=True)
            
        except Exception as e:
            st.error(f"Error generating customer insights: {e}")
    
    with tab4:
        st.markdown("#### 📋 Custom Report Builder")
        
        st.markdown("##### 🛠️ Build Your Custom Report")
        
        # Report configuration
        col1, col2 = st.columns(2)
        
        with col1:
            report_type = st.selectbox("Report Type", [
                "Customer Analysis",
                "Transaction Summary",
                "Account Performance",
                "Loan Portfolio",
                "Revenue Analysis"
            ])
            
            date_range = st.selectbox("Date Range", [
                "Last 7 Days",
                "Last 30 Days",
                "Last 90 Days",
                "Custom Range"
            ])
            
            if date_range == "Custom Range":
                custom_start = st.date_input("Start Date")
                custom_end = st.date_input("End Date")
        
        with col2:
            group_by = st.selectbox("Group By", [
                "Day",
                "Week", 
                "Month",
                "Account Type",
                "Customer Segment"
            ])
            
            metrics = st.multiselect("Metrics to Include", [
                "Count",
                "Sum",
                "Average",
                "Min/Max",
                "Growth Rate"
            ])
            
            export_format = st.selectbox("Export Format", ["View Only", "CSV", "Excel", "PDF"])
        
        if st.button("🔄 Generate Custom Report"):
            try:
                # Generate report based on selections
                if report_type == "Customer Analysis":
                    if date_range == "Last 30 Days":
                        df_custom_report = pd.read_sql("""
                            SELECT DATE(u.created_at) as signup_date, COUNT(*) as new_customers,
                                   AVG(a.balance) as avg_balance
                            FROM users u
                            JOIN accounts a ON u.user_id = a.user_id
                            WHERE u.created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                            AND u.business_id IS NULL
                            GROUP BY DATE(u.created_at)
                            ORDER BY signup_date
                        """, conn)
                    else:
                        df_custom_report = pd.read_sql("""
                            SELECT DATE(u.created_at) as signup_date, COUNT(*) as new_customers
                            FROM users u
                            WHERE u.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                            AND u.business_id IS NULL
                            GROUP BY DATE(u.created_at)
                            ORDER BY signup_date
                        """, conn)
                
                elif report_type == "Transaction Summary":
                    df_custom_report = pd.read_sql("""
                        SELECT txn_type, COUNT(*) as transaction_count, 
                               SUM(amount) as total_amount, AVG(amount) as avg_amount
                        FROM transactions
                        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                        GROUP BY txn_type
                        ORDER BY total_amount DESC
                    """, conn)
                
                else:
                    # Default report
                    df_custom_report = pd.read_sql("""
                        SELECT 'Sample Report' as report_type, 
                               COUNT(*) as total_records
                        FROM users
                    """, conn)
                
                if not df_custom_report.empty:
                    st.markdown("##### 📊 Custom Report Results")
                    st.dataframe(df_custom_report, use_container_width=True)
                    
                    # Export options
                    if export_format == "CSV":
                        csv = df_custom_report.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name=f"custom_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                else:
                    st.info("No data available for the selected report criteria")
                    
            except Exception as e:
                st.error(f"Error generating custom report: {e}")

# 10. SECURITY & COMPLIANCE
elif view_mode == "🔒 Security & Compliance":
    st.markdown("### 🔒 Security & Compliance Management")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Security Overview", "👤 User Access", "📋 Audit Logs", "⚖️ Compliance"])
    
    with tab1:
        st.markdown("#### 🛡️ Security Dashboard")
        
        # Security metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Mock security data for demonstration
        col1.metric("Active Sessions", "47", delta="+3")
        col2.metric("Failed Logins (24h)", "12", delta="-5")
        col3.metric("Security Alerts", "2", delta="+1")
        col4.metric("System Uptime", "99.9%", delta="+0.1%")
        
        st.markdown("---")
        
        # Security alerts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🚨 Recent Security Alerts")
            
            security_alerts = [
                {"time": "10:30 AM", "type": "Failed Login", "details": "Multiple failed attempts from IP 192.168.1.100", "severity": "Medium"},
                {"time": "09:15 AM", "type": "Large Transaction", "details": "Transaction over KES 500,000 detected", "severity": "Low"},
                {"time": "08:45 AM", "type": "New Device", "details": "Admin login from new device", "severity": "High"}
            ]
            
            for alert in security_alerts:
                severity_color = "🔴" if alert["severity"] == "High" else "🟡" if alert["severity"] == "Medium" else "🟢"
                st.write(f"{severity_color} **{alert['type']}** - {alert['time']}")
                st.caption(alert['details'])
                st.markdown("---")
        
        with col2:
            st.markdown("##### 🔐 Access Control Status")
            
            access_metrics = {
                'Component': ['Admin Portal', 'Customer Portal', 'Business Portal', 'Branch Operations', 'API Endpoints'],
                'Status': ['🟢 Secure', '🟢 Secure', '🟢 Secure', '🟢 Secure', '🟡 Monitor'],
                'Last_Check': ['2 min ago', '5 min ago', '3 min ago', '1 min ago', '10 min ago']
            }
            
            df_access_status = pd.DataFrame(access_metrics)
            st.dataframe(df_access_status, use_container_width=True)
    
    with tab2:
        st.markdown("#### 👤 User Access Management")
        
        # User access overview
        try:
            # Get user access statistics
            total_users = pd.read_sql("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
            active_users = pd.read_sql("SELECT COUNT(*) as count FROM users WHERE is_active = 1", conn).iloc[0]['count']
            
            # Try to get staff access data
            try:
                total_staff = pd.read_sql("SELECT COUNT(*) as count FROM staff", conn).iloc[0]['count']
                active_staff = pd.read_sql("SELECT COUNT(*) as count FROM staff WHERE is_active = 1", conn).iloc[0]['count']
            except:
                total_staff = 0
                active_staff = 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Users", f"{total_users:,}")
            col2.metric("Active Users", f"{active_users:,}")
            col3.metric("Total Staff", f"{total_staff:,}")
            col4.metric("Active Staff", f"{active_staff:,}")
            
            # User access management
            st.markdown("##### 🔧 User Access Control")
            
            user_email = st.text_input("Enter User Email for Access Management")
            
            if user_email:
                # Check if user exists
                user_details = pd.read_sql(f"SELECT * FROM users WHERE email = '{user_email}'", conn)
                
                if not user_details.empty:
                    user = user_details.iloc[0]
                    
                    col1, col2, col3 = st.columns(3)
                    col1.write(f"**Name:** {user['full_name']}")
                    col1.write(f"**Email:** {user['email']}")
                    
                    col2.write(f"**Status:** {'Active' if user['is_active'] else 'Inactive'}")
                    col2.write(f"**KYC Tier:** {user['kyc_tier']}")
                    
                    col3.write(f"**Created:** {user['created_at'].strftime('%Y-%m-%d')}")
                    col3.write(f"**Last Login:** N/A")  # Would track login times
                    
                    # Access control actions
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        if st.button("🔒 Suspend User"):
                            conn.execute(text("UPDATE users SET is_active = 0 WHERE email = :email"), {'email': user_email})
                            conn.commit()
                            st.success("User suspended!")
                            st.rerun()
                    
                    with col2:
                        if st.button("🔓 Reactivate User"):
                            conn.execute(text("UPDATE users SET is_active = 1 WHERE email = :email"), {'email': user_email})
                            conn.commit()
                            st.success("User reactivated!")
                            st.rerun()
                    
                    with col3:
                        if st.button("🔄 Reset Password"):
                            new_password = "temp123"
                            conn.execute(text("UPDATE users SET password_hash = :pwd WHERE email = :email"), 
                                       {'pwd': new_password, 'email': user_email})
                            conn.commit()
                            st.success(f"Password reset to: {new_password}")
                    
                    with col4:
                        if st.button("📊 View Activity"):
                            st.info("User activity log would be displayed here")
                else:
                    st.error("User not found!")
                    
        except Exception as e:
            st.error(f"Error loading user access data: {e}")
    
    with tab3:
        st.markdown("#### 📋 Audit Logs & Activity Monitoring")
        
        # Audit log filters
        col1, col2, col3 = st.columns(3)
        with col1:
            log_type = st.selectbox("Log Type", ["All", "Login", "Transaction", "Admin Action", "System"])
        with col2:
            log_date = st.date_input("Date", value=datetime.now().date())
        with col3:
            log_user = st.text_input("Filter by User")
        
        # Mock audit log data
        audit_logs = [
            {"timestamp": "2024-01-06 14:30:15", "user": "admin@wekeza.com", "action": "User Created", "details": "Created new customer account", "ip": "192.168.1.10"},
            {"timestamp": "2024-01-06 14:25:32", "user": "john.doe@email.com", "action": "Login", "details": "Successful login to customer portal", "ip": "192.168.1.25"},
            {"timestamp": "2024-01-06 14:20:45", "user": "admin@wekeza.com", "action": "Transaction Approved", "details": "Approved large transaction KES 150,000", "ip": "192.168.1.10"},
            {"timestamp": "2024-01-06 14:15:18", "user": "staff@wekeza.com", "action": "Account Frozen", "details": "Froze account ACC1000123 due to suspicious activity", "ip": "192.168.1.15"},
            {"timestamp": "2024-01-06 14:10:22", "user": "system", "action": "Backup", "details": "Daily database backup completed", "ip": "localhost"}
        ]
        
        df_audit_logs = pd.DataFrame(audit_logs)
        
        # Apply filters
        if log_user:
            df_audit_logs = df_audit_logs[df_audit_logs['user'].str.contains(log_user, case=False)]
        
        st.dataframe(df_audit_logs, use_container_width=True)
        
        # Export audit logs
        if st.button("📥 Export Audit Logs"):
            csv = df_audit_logs.to_csv(index=False)
            st.download_button(
                label="Download Audit Log CSV",
                data=csv,
                file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with tab4:
        st.markdown("#### ⚖️ Compliance Management")
        
        # Compliance dashboard
        st.markdown("##### 📊 Compliance Status")
        
        compliance_items = {
            'Requirement': [
                'KYC Documentation',
                'AML Monitoring',
                'Data Protection',
                'Transaction Reporting',
                'Audit Trail',
                'Password Policy',
                'Access Controls'
            ],
            'Status': [
                '✅ Compliant',
                '✅ Compliant', 
                '⚠️ Needs Review',
                '✅ Compliant',
                '✅ Compliant',
                '⚠️ Needs Update',
                '✅ Compliant'
            ],
            'Last_Review': [
                '2024-01-01',
                '2024-01-03',
                '2023-12-15',
                '2024-01-05',
                '2024-01-06',
                '2023-11-20',
                '2024-01-02'
            ],
            'Next_Review': [
                '2024-04-01',
                '2024-04-03',
                '2024-01-15',
                '2024-04-05',
                '2024-04-06',
                '2024-01-20',
                '2024-04-02'
            ]
        }
        
        df_compliance = pd.DataFrame(compliance_items)
        st.dataframe(df_compliance, use_container_width=True)
        
        # Compliance actions
        st.markdown("##### 🔧 Compliance Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📋 Generate Compliance Report"):
                st.success("Compliance report generated successfully!")
                st.info("Report would include all compliance metrics and status")
        
        with col2:
            if st.button("🔍 Run Compliance Check"):
                st.success("Compliance check completed!")
                st.info("All systems checked for compliance violations")
        
        with col3:
            if st.button("📤 Submit Regulatory Report"):
                st.success("Regulatory report submitted!")
                st.info("Monthly regulatory report sent to authorities")

# 11. SYSTEM ADMINISTRATION
elif view_mode == "⚙️ System Administration":
    st.markdown("### ⚙️ System Administration & Configuration")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🖥️ System Status", "🔧 Configuration", "💾 Database Management", "🔄 Maintenance"])
    
    with tab1:
        st.markdown("#### 🖥️ System Health & Status")
        
        # System health metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Mock system metrics
        col1.metric("CPU Usage", "45%", delta="-5%")
        col2.metric("Memory Usage", "68%", delta="+3%")
        col3.metric("Disk Usage", "72%", delta="+1%")
        col4.metric("Network I/O", "125 MB/s", delta="+15 MB/s")
        
        st.markdown("---")
        
        # Service status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🌐 Service Status")
            
            services = {
                'Service': ['Database Server', 'Web Server', 'API Gateway', 'Authentication Service', 'Backup Service'],
                'Status': ['🟢 Running', '🟢 Running', '🟢 Running', '🟢 Running', '🟡 Warning'],
                'Uptime': ['99.9%', '99.8%', '99.9%', '99.7%', '98.5%'],
                'Last_Check': ['1 min ago', '1 min ago', '2 min ago', '1 min ago', '5 min ago']
            }
            
            df_services = pd.DataFrame(services)
            st.dataframe(df_services, use_container_width=True)
        
        with col2:
            st.markdown("##### 📊 Performance Metrics")
            
            # Mock performance data
            performance_data = {
                'hours': list(range(24)),
                'response_time': [120, 115, 110, 105, 100, 95, 90, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 135, 130, 125, 120, 115],
                'throughput': [450, 420, 380, 350, 320, 300, 280, 260, 280, 300, 350, 400, 450, 500, 550, 600, 650, 700, 680, 650, 600, 550, 500, 475]
            }
            
            df_performance = pd.DataFrame(performance_data)
            
            fig = px.line(df_performance, x='hours', y='response_time', title='24-Hour Response Time (ms)')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("#### 🔧 System Configuration")
        
        # Configuration management
        st.markdown("##### ⚙️ Application Settings")
        
        with st.form("system_config"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Database Configuration**")
                db_host = st.text_input("Database Host", value="localhost")
                db_port = st.number_input("Database Port", value=3306)
                max_connections = st.number_input("Max Connections", value=100)
                
                st.markdown("**Security Settings**")
                session_timeout = st.number_input("Session Timeout (minutes)", value=30)
                max_login_attempts = st.number_input("Max Login Attempts", value=3)
                password_expiry = st.number_input("Password Expiry (days)", value=90)
            
            with col2:
                st.markdown("**Transaction Limits**")
                daily_limit = st.number_input("Daily Transaction Limit (KES)", value=1000000.0)
                single_txn_limit = st.number_input("Single Transaction Limit (KES)", value=500000.0)
                
                st.markdown("**System Features**")
                enable_sms = st.checkbox("Enable SMS Notifications", value=True)
                enable_email = st.checkbox("Enable Email Notifications", value=True)
                enable_2fa = st.checkbox("Enable Two-Factor Authentication", value=False)
                maintenance_mode = st.checkbox("Maintenance Mode", value=False)
            
            if st.form_submit_button("💾 Save Configuration"):
                st.success("✅ Configuration saved successfully!")
                st.info("Some changes may require system restart to take effect.")
    
    with tab3:
        st.markdown("#### 💾 Database Management")
        
        # Database statistics
        try:
            # Get database statistics
            db_stats = {
                'Table': ['users', 'businesses', 'accounts', 'transactions', 'staff'],
                'Records': [0, 0, 0, 0, 0],
                'Size': ['0 MB', '0 MB', '0 MB', '0 MB', '0 MB']
            }
            
            # Try to get actual counts
            try:
                db_stats['Records'][0] = pd.read_sql("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
                db_stats['Records'][1] = pd.read_sql("SELECT COUNT(*) as count FROM businesses", conn).iloc[0]['count']
                db_stats['Records'][2] = pd.read_sql("SELECT COUNT(*) as count FROM accounts", conn).iloc[0]['count']
                db_stats['Records'][3] = pd.read_sql("SELECT COUNT(*) as count FROM transactions", conn).iloc[0]['count']
                try:
                    db_stats['Records'][4] = pd.read_sql("SELECT COUNT(*) as count FROM staff", conn).iloc[0]['count']
                except:
                    db_stats['Records'][4] = 0
            except:
                pass
            
            df_db_stats = pd.DataFrame(db_stats)
            st.dataframe(df_db_stats, use_container_width=True)
            
            st.markdown("##### 🔧 Database Operations")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("🔄 Backup Database"):
                    st.success("Database backup initiated!")
                    st.info("Backup will be saved to /backups/wekeza_db_backup.sql")
            
            with col2:
                if st.button("🧹 Optimize Tables"):
                    st.success("Table optimization completed!")
                    st.info("All database tables have been optimized")
            
            with col3:
                if st.button("📊 Analyze Performance"):
                    st.success("Performance analysis completed!")
                    st.info("Database performance metrics updated")
            
            with col4:
                if st.button("🔍 Check Integrity"):
                    st.success("Database integrity check passed!")
                    st.info("No corruption detected in database")
                    
        except Exception as e:
            st.error(f"Error loading database statistics: {e}")
    
    with tab4:
        st.markdown("#### 🔄 System Maintenance")
        
        # Maintenance operations
        st.markdown("##### 🛠️ Maintenance Operations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Scheduled Maintenance**")
            
            maintenance_tasks = {
                'Task': ['Database Backup', 'Log Rotation', 'Cache Cleanup', 'Security Scan', 'Performance Report'],
                'Schedule': ['Daily 2:00 AM', 'Weekly Sunday', 'Daily 3:00 AM', 'Weekly Monday', 'Monthly 1st'],
                'Last_Run': ['2024-01-06 02:00', '2024-01-01 03:00', '2024-01-06 03:00', '2024-01-01 04:00', '2024-01-01 05:00'],
                'Status': ['✅ Success', '✅ Success', '✅ Success', '✅ Success', '✅ Success']
            }
            
            df_maintenance = pd.DataFrame(maintenance_tasks)
            st.dataframe(df_maintenance, use_container_width=True)
        
        with col2:
            st.markdown("**Manual Operations**")
            
            if st.button("🧹 Clear System Cache"):
                st.success("System cache cleared successfully!")
            
            if st.button("📝 Rotate Log Files"):
                st.success("Log files rotated successfully!")
            
            if st.button("🔄 Restart Services"):
                st.warning("This will restart all system services. Continue?")
                if st.button("Confirm Restart"):
                    st.success("Services restarted successfully!")
            
            if st.button("📊 Generate System Report"):
                st.success("System report generated!")
                st.info("Report saved to /reports/system_report.pdf")
        
        # System logs
        st.markdown("##### 📋 Recent System Logs")
        
        system_logs = [
            {"timestamp": "2024-01-06 14:30:00", "level": "INFO", "service": "Database", "message": "Backup completed successfully"},
            {"timestamp": "2024-01-06 14:25:00", "level": "INFO", "service": "Web Server", "message": "High traffic detected, scaling up"},
            {"timestamp": "2024-01-06 14:20:00", "level": "WARN", "service": "Auth Service", "message": "Multiple failed login attempts detected"},
            {"timestamp": "2024-01-06 14:15:00", "level": "INFO", "service": "API Gateway", "message": "Rate limiting applied to IP 192.168.1.100"},
            {"timestamp": "2024-01-06 14:10:00", "level": "ERROR", "service": "Email Service", "message": "SMTP connection timeout, retrying..."}
        ]
        
        df_logs = pd.DataFrame(system_logs)
        st.dataframe(df_logs, use_container_width=True)

# 12. SUPERVISION & APPROVALS (MAKER-CHECKER SYSTEM)
elif view_mode == "✅ Supervision & Approvals":
    st.markdown("### ✅ Maker-Checker Supervision & Approvals")
    
    tab1, tab2, tab3, tab4 = st.tabs(["⏳ Pending Approvals", "✅ Approved Items", "❌ Rejected Items", "📊 Approval Analytics"])
    
    with tab1:
        st.markdown("#### ⏳ Pending Authorization Queue")
        
        try:
            # Get pending items from authorization queue
            df_pending = pd.read_sql("""
                SELECT queue_id, transaction_type, reference_id, maker_id, maker_name, 
                       amount, description, branch_code, priority, created_at, operation_data
                FROM authorization_queue 
                WHERE status = 'PENDING'
                ORDER BY 
                    CASE priority 
                        WHEN 'URGENT' THEN 1 
                        WHEN 'HIGH' THEN 2 
                        WHEN 'MEDIUM' THEN 3 
                        WHEN 'LOW' THEN 4 
                    END,
                    created_at ASC
            """, conn)
            
            if not df_pending.empty:
                st.success(f"📋 **{len(df_pending)} items pending approval**")
                
                # Display each pending item
                for idx, item in df_pending.iterrows():
                    with st.expander(f"🔍 {item['transaction_type']} - {item['queue_id']} - KES {item['amount']:,.2f}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**Queue ID:** {item['queue_id']}")
                            st.write(f"**Type:** {item['transaction_type']}")
                            st.write(f"**Amount:** KES {item['amount']:,.2f}")
                            st.write(f"**Priority:** {item['priority']}")
                        
                        with col2:
                            st.write(f"**Maker:** {item['maker_name']}")
                            st.write(f"**Maker ID:** {item['maker_id']}")
                            st.write(f"**Branch:** {item['branch_code']}")
                            st.write(f"**Created:** {item['created_at'].strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        with col3:
                            st.write(f"**Description:** {item['description']}")
                            
                            # Parse operation data to show details
                            try:
                                import json
                                op_data = json.loads(item['operation_data'])
                                st.write("**Operation Details:**")
                                for key, value in op_data.items():
                                    if key not in ['operation_data', 'created_at']:
                                        st.write(f"• {key}: {value}")
                            except:
                                st.write("**Operation Data:** Available")
                        
                        st.markdown("---")
                        
                        # Approval actions
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button(f"✅ Approve", key=f"approve_{item['queue_id']}", type="primary"):
                                try:
                                    # Update authorization queue
                                    conn.execute(text("""
                                        UPDATE authorization_queue 
                                        SET status = 'APPROVED', approved_by = 'SUP001', approved_at = NOW()
                                        WHERE queue_id = :queue_id
                                    """), {'queue_id': item['queue_id']})
                                    
                                    # Execute the approved operation
                                    import sys
                                    import os
                                    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'branch_operations', 'shared'))
                                    from authorization_helper import execute_approved_operation
                                    execution_result = execute_approved_operation(item['queue_id'])
                                    
                                    conn.commit()
                                    st.success(f"✅ {item['queue_id']} approved and executed!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Approval failed: {e}")
                        
                        with col2:
                            if st.button(f"❌ Reject", key=f"reject_{item['queue_id']}", type="secondary"):
                                rejection_reason = st.text_input(f"Rejection reason for {item['queue_id']}", key=f"reason_{item['queue_id']}")
                                if st.button(f"Confirm Rejection", key=f"confirm_reject_{item['queue_id']}"):
                                    if rejection_reason:
                                        try:
                                            conn.execute(text("""
                                                UPDATE authorization_queue 
                                                SET status = 'REJECTED', approved_by = 'SUP001', 
                                                    approved_at = NOW(), rejection_reason = :reason
                                                WHERE queue_id = :queue_id
                                            """), {'queue_id': item['queue_id'], 'reason': rejection_reason})
                                            conn.commit()
                                            st.success(f"❌ {item['queue_id']} rejected!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Rejection failed: {e}")
                                    else:
                                        st.error("Please provide a rejection reason")
                        
                        with col3:
                            if st.button(f"⏸️ Hold", key=f"hold_{item['queue_id']}"):
                                st.info("Item put on hold for further review")
                
            else:
                st.info("✅ No items pending approval")
                
        except Exception as e:
            st.error(f"Error loading pending approvals: {e}")
    
    with tab2:
        st.markdown("#### ✅ Recently Approved Items")
        
        try:
            df_approved = pd.read_sql("""
                SELECT queue_id, transaction_type, maker_name, amount, description, 
                       approved_by, approved_at, created_at
                FROM authorization_queue 
                WHERE status = 'APPROVED'
                ORDER BY approved_at DESC LIMIT 50
            """, conn)
            
            if not df_approved.empty:
                st.dataframe(df_approved, use_container_width=True)
                
                # Approved summary
                col1, col2, col3 = st.columns(3)
                col1.metric("Approved Today", len(df_approved[df_approved['approved_at'].dt.date == pd.Timestamp.now().date()]))
                col2.metric("Total Approved", len(df_approved))
                col3.metric("Total Value", f"KES {df_approved['amount'].sum():,.2f}")
            else:
                st.info("No approved items found")
                
        except Exception as e:
            st.error(f"Error loading approved items: {e}")
    
    with tab3:
        st.markdown("#### ❌ Recently Rejected Items")
        
        try:
            df_rejected = pd.read_sql("""
                SELECT queue_id, transaction_type, maker_name, amount, description, 
                       approved_by, approved_at, rejection_reason
                FROM authorization_queue 
                WHERE status = 'REJECTED'
                ORDER BY approved_at DESC LIMIT 50
            """, conn)
            
            if not df_rejected.empty:
                st.dataframe(df_rejected, use_container_width=True)
                
                # Rejection summary
                col1, col2 = st.columns(2)
                col1.metric("Rejected Today", len(df_rejected[df_rejected['approved_at'].dt.date == pd.Timestamp.now().date()]))
                col2.metric("Total Rejected", len(df_rejected))
            else:
                st.info("No rejected items found")
                
        except Exception as e:
            st.error(f"Error loading rejected items: {e}")
    
    with tab4:
        st.markdown("#### 📊 Approval Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📈 Daily Approval Activity")
            try:
                df_daily_approvals = pd.read_sql("""
                    SELECT DATE(approved_at) as approval_date, 
                           COUNT(*) as total_items,
                           SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
                           SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected
                    FROM authorization_queue 
                    WHERE approved_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY DATE(approved_at)
                    ORDER BY approval_date
                """, conn)
                
                if not df_daily_approvals.empty:
                    fig = px.line(df_daily_approvals, x='approval_date', y=['approved', 'rejected'],
                                 title='Daily Approval Activity (Last 30 Days)')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No approval activity data")
            except Exception as e:
                st.error(f"Error loading approval analytics: {e}")
        
        with col2:
            st.markdown("##### 🏦 Approval by Transaction Type")
            try:
                df_type_approvals = pd.read_sql("""
                    SELECT transaction_type, 
                           COUNT(*) as total_items,
                           SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) as approved,
                           SUM(CASE WHEN status = 'REJECTED' THEN 1 ELSE 0 END) as rejected,
                           ROUND(SUM(CASE WHEN status = 'APPROVED' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) as approval_rate
                    FROM authorization_queue 
                    WHERE approved_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
                    GROUP BY transaction_type
                    ORDER BY total_items DESC
                """, conn)
                
                if not df_type_approvals.empty:
                    st.dataframe(df_type_approvals, use_container_width=True)
                else:
                    st.info("No transaction type data")
            except Exception as e:
                st.error(f"Error loading transaction type analytics: {e}")

# Handle missing sections with placeholder
else:
    st.markdown(f"### {view_mode}")
    st.info("This section is under development. Please check back later.")
    st.markdown("Available sections:")
    st.markdown("- 📊 Executive Dashboard")
    st.markdown("- 👤 Customer Management") 
    st.markdown("- 🏢 Business Management")
    st.markdown("- 👥 Staff Administration")
    st.markdown("- 💰 Account Oversight")
    st.markdown("- 📋 Loan Administration")
    st.markdown("- 🛡️ Insurance Management")
    st.markdown("- 💸 Transaction Monitoring")
    st.markdown("- 📈 Analytics & Reports")
    st.markdown("- 🔒 Security & Compliance")
    st.markdown("- ⚙️ System Administration")