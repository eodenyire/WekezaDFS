import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import os
from datetime import datetime
import uuid

st.set_page_config(page_title="Wekeza HQ | Admin Panel", layout="wide", page_icon="🏦")

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
    st.title("🔐 Admin Panel Login")
    st.markdown("### Wekeza Bank Administration")
    
    username = st.text_input("Username", value="admin")
    password = st.text_input("Password", type="password", value="admin")
    
    if st.button("Login") or (username == "admin" and password == "admin"):
        if username == "admin" and password == "admin":
            st.session_state['admin_logged_in'] = True
            st.rerun()
        else:
            st.error("Invalid credentials! Use: admin / admin")

def admin_logout():
    if st.sidebar.button("🚪 Logout"):
        st.session_state['admin_logged_in'] = False
        st.rerun()

# Check admin authentication
if 'admin_logged_in' not in st.session_state:
    st.session_state['admin_logged_in'] = False

if not st.session_state['admin_logged_in']:
    admin_login()
    st.stop()

# --- ADMIN DASHBOARD ---
admin_logout()

st.sidebar.title("🏦 Admin Panel")
view_mode = st.sidebar.radio("Admin Functions:", [
    "📊 Dashboard", 
    "👤 Manage Users", 
    "🏢 Manage Businesses",
    "🏪 Manage Branches",
    "👥 Manage Staff",
    "💰 Manage Accounts",
    "📋 Manage Loans", 
    "🛡️ Manage Insurance",
    "💸 Transactions",
    "⚙️ System Settings"
])
st.sidebar.markdown("---")
st.sidebar.info("Logged in as: **Admin**")
st.sidebar.markdown("### 🔗 Quick Links")
st.sidebar.markdown("- [Branch Teller](http://localhost:8505) 🏪")
st.sidebar.markdown("- [Customer Portal](http://localhost:8502) 👤")
st.sidebar.markdown("- [Business Portal](http://localhost:8504) 🏢")

# --- MAIN DASHBOARD ---
st.title(f"🏦 Wekeza Bank Admin | {view_mode}")

# 1. DASHBOARD OVERVIEW
if view_mode == "📊 Dashboard":
    # KPIs
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    # Queries
    total_users = pd.read_sql("SELECT COUNT(*) as c FROM users", conn).iloc[0]['c']
    total_accounts = pd.read_sql("SELECT COUNT(*) as c FROM accounts", conn).iloc[0]['c']
    total_balance = pd.read_sql("SELECT SUM(balance) as amt FROM accounts", conn).iloc[0]['amt'] or 0
    total_loans = pd.read_sql("SELECT SUM(principal_amount) as amt FROM loans", conn).iloc[0]['amt'] or 0
    total_branches = pd.read_sql("SELECT COUNT(*) as c FROM branches WHERE is_active = 1", conn).iloc[0]['c']
    total_staff = pd.read_sql("SELECT COUNT(*) as c FROM staff WHERE is_active = 1", conn).iloc[0]['c']

    c1.metric("Total Users", total_users)
    c2.metric("Total Accounts", total_accounts)
    c3.metric("Total Deposits", f"KES {total_balance:,.0f}")
    c4.metric("Total Loans", f"KES {total_loans:,.0f}")
    c5.metric("Active Branches", total_branches)
    c6.metric("Active Staff", total_staff)

    st.markdown("---")
    
    # Recent Activity
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.subheader("📊 Recent Transactions")
        df_txn = pd.read_sql("SELECT created_at, txn_type, amount FROM transactions ORDER BY created_at DESC LIMIT 10", conn)
        if not df_txn.empty:
            st.dataframe(df_txn, use_container_width=True)
        else:
            st.info("No transactions yet")

    with col_b:
        st.subheader("💰 Account Balances")
        df_bal = pd.read_sql("""
            SELECT u.full_name, a.account_number, a.balance 
            FROM users u 
            JOIN accounts a ON u.user_id = a.user_id 
            ORDER BY a.balance DESC LIMIT 10
        """, conn)
        st.dataframe(df_bal, use_container_width=True)
    
    with col_c:
        st.subheader("👥 Staff by Branch")
        df_staff_branch = pd.read_sql("""
            SELECT b.branch_name, COUNT(s.staff_id) as staff_count
            FROM branches b
            LEFT JOIN staff s ON b.branch_id = s.branch_id AND s.is_active = 1
            WHERE b.is_active = 1
            GROUP BY b.branch_id, b.branch_name
            ORDER BY staff_count DESC
        """, conn)
        if not df_staff_branch.empty:
            st.dataframe(df_staff_branch, use_container_width=True)
        else:
            st.info("No staff data yet")

# 2. USER MANAGEMENT
elif view_mode == "👤 Manage Users":
    st.subheader("👤 User Management")
    
    tab1, tab2, tab3 = st.tabs(["Create User", "View Users", "User Actions"])
    
    with tab1:
        st.markdown("### Create New User")
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name *")
                email = st.text_input("Email *")
                phone = st.text_input("Phone Number *")
            
            with col2:
                national_id = st.text_input("National ID *")
                password = st.text_input("Password *", type="password", help="User will login with this password")
                initial_balance = st.number_input("Initial Balance (KES)", min_value=0.0, value=10000.0)
                kyc_tier = st.selectbox("KYC Tier", ["TIER_1", "TIER_2", "TIER_3"])
            
            submitted = st.form_submit_button("Create User", type="primary")
            
            if submitted and all([full_name, email, phone, national_id, password]):
                try:
                    # Insert user with actual password
                    user_query = text("""
                    INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, created_at)
                    VALUES (:full_name, :email, :phone, :national_id, :password_hash, :kyc_tier, :is_active, :created_at)
                    """)
                    
                    conn.execute(user_query, {
                        'full_name': full_name,
                        'email': email,
                        'phone': phone,
                        'national_id': national_id,
                        'password_hash': password,  # Store password directly (no hashing as requested)
                        'kyc_tier': kyc_tier,
                        'is_active': 1,
                        'created_at': datetime.now()
                    })
                    
                    # Get user ID
                    user_id_result = pd.read_sql(f"SELECT user_id FROM users WHERE email = '{email}'", conn)
                    user_id = int(user_id_result.iloc[0]['user_id'])  # Convert to Python int
                    
                    # Create account
                    account_number = f"ACC{1000000 + user_id}"
                    account_query = text("""
                    INSERT INTO accounts (user_id, account_number, balance, currency, status, created_at)
                    VALUES (:user_id, :account_number, :balance, :currency, :status, :created_at)
                    """)
                    
                    conn.execute(account_query, {
                        'user_id': user_id,
                        'account_number': account_number,
                        'balance': float(initial_balance),  # Convert to Python float
                        'currency': 'KES',
                        'status': 'ACTIVE',
                        'created_at': datetime.now()
                    })
                    
                    conn.commit()
                    st.success(f"✅ User created! Account: {account_number}")
                    st.info(f"🔑 Login credentials: {email} / {password}")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with tab2:
        st.markdown("### All Users")
        df_users = pd.read_sql("""
        SELECT u.user_id, u.full_name, u.email, u.phone_number, a.account_number, a.balance, u.is_active
        FROM users u 
        LEFT JOIN accounts a ON u.user_id = a.user_id 
        ORDER BY u.created_at DESC
        """, conn)
        st.dataframe(df_users, use_container_width=True)
    
    with tab3:
        st.markdown("### User Actions")
        user_email = st.text_input("User Email")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Activate User"):
                if user_email:
                    conn.execute(text("UPDATE users SET is_active = 1 WHERE email = :email"), {'email': user_email})
                    conn.commit()
                    st.success("User activated!")
        
        with col2:
            if st.button("Deactivate User"):
                if user_email:
                    conn.execute(text("UPDATE users SET is_active = 0 WHERE email = :email"), {'email': user_email})
                    conn.commit()
                    st.success("User deactivated!")
        
        with col3:
            if st.button("Delete User"):
                if user_email:
                    conn.execute(text("DELETE FROM users WHERE email = :email"), {'email': user_email})
                    conn.commit()
                    st.success("User deleted!")

# 3. BUSINESS MANAGEMENT
elif view_mode == "🏢 Manage Businesses":
    st.subheader("🏢 Business Management")
    
    tab1, tab2 = st.tabs(["Create Business", "View Businesses"])
    
    with tab1:
        st.markdown("### Register New Business")
        with st.form("create_business_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                business_name = st.text_input("Business Name *")
                registration_no = st.text_input("Registration Number *")
                kra_pin = st.text_input("KRA PIN *")
            
            with col2:
                sector = st.selectbox("Sector", ["Technology", "Agriculture", "Retail", "Manufacturing", "Services"])
                director_name = st.text_input("Director Name *")
                director_email = st.text_input("Director Email *")
                director_password = st.text_input("Director Password *", type="password", help="Director will login with this password")
            
            submitted = st.form_submit_button("Register Business", type="primary")
            
            if submitted and all([business_name, registration_no, kra_pin, director_name, director_email, director_password]):
                try:
                    # Use raw MySQL connection to avoid SQLAlchemy transaction issues
                    import mysql.connector
                    raw_conn = mysql.connector.connect(
                        host='localhost',
                        user='root',
                        password='root',
                        database='wekeza_dfs_db'
                    )
                    cursor = raw_conn.cursor()
                    
                    # Insert business
                    cursor.execute("""
                    INSERT INTO businesses (business_name, registration_no, kra_pin, sector, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                    """, (business_name, registration_no, kra_pin, sector, datetime.now()))
                    
                    business_id = cursor.lastrowid
                    
                    # Create director user
                    cursor.execute("""
                    INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, business_id, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (director_name, director_email, '0700000000', f"DIR{registration_no}", 
                          director_password, 'TIER_3', 1, business_id, datetime.now()))
                    
                    # Create business account
                    account_number = f"BIZ{1000000 + business_id}"
                    cursor.execute("""
                    INSERT INTO accounts (business_id, account_number, balance, currency, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """, (business_id, account_number, 50000.0, 'KES', 'ACTIVE', datetime.now()))
                    
                    raw_conn.commit()
                    raw_conn.close()
                    
                    st.success(f"✅ Business registered! Account: {account_number}")
                    st.info(f"🔑 Director login: {director_email} / {director_password}")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
                    try:
                        raw_conn.rollback()
                        raw_conn.close()
                    except:
                        pass
    
    with tab2:
        st.markdown("### All Businesses")
        df_businesses = pd.read_sql("SELECT * FROM businesses ORDER BY created_at DESC", conn)
        st.dataframe(df_businesses, use_container_width=True)

# 4. BRANCH MANAGEMENT
elif view_mode == "🏪 Manage Branches":
    st.subheader("🏪 Branch Management")
    
    tab1, tab2, tab3 = st.tabs(["Create Branch", "View Branches", "Branch Actions"])
    
    with tab1:
        st.markdown("### Create New Branch")
        with st.form("create_branch_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                branch_code = st.text_input("Branch Code *", help="e.g., BR002")
                branch_name = st.text_input("Branch Name *", help="e.g., Westlands Branch")
                location = st.text_input("Location *", help="e.g., Westlands, Nairobi")
            
            with col2:
                phone_number = st.text_input("Phone Number", help="e.g., +254700000000")
                email = st.text_input("Email", help="e.g., westlands@wekeza.co.ke")
                
                # Get available managers
                df_managers = pd.read_sql("""
                    SELECT staff_id, full_name, staff_code 
                    FROM staff 
                    WHERE role IN ('BRANCH_MANAGER', 'SUPERVISOR') AND is_active = 1
                """, conn)
                
                if not df_managers.empty:
                    manager_options = ["None"] + [f"{row['full_name']} ({row['staff_code']})" for _, row in df_managers.iterrows()]
                    selected_manager = st.selectbox("Branch Manager", manager_options)
                else:
                    selected_manager = "None"
                    st.info("No available managers. Create staff first.")
            
            submitted = st.form_submit_button("Create Branch", type="primary")
            
            if submitted and all([branch_code, branch_name, location]):
                try:
                    manager_id = None
                    if selected_manager != "None":
                        # Extract staff_id from selection
                        selected_staff_code = selected_manager.split("(")[1].split(")")[0]
                        manager_row = df_managers[df_managers['staff_code'] == selected_staff_code]
                        if not manager_row.empty:
                            manager_id = int(manager_row.iloc[0]['staff_id'])
                    
                    conn.execute(text("""
                    INSERT INTO branches (branch_code, branch_name, location, phone_number, email, manager_id, is_active)
                    VALUES (:branch_code, :branch_name, :location, :phone_number, :email, :manager_id, :is_active)
                    """), {
                        'branch_code': branch_code,
                        'branch_name': branch_name,
                        'location': location,
                        'phone_number': phone_number or None,
                        'email': email or None,
                        'manager_id': manager_id,
                        'is_active': 1
                    })
                    
                    conn.commit()
                    st.success(f"✅ Branch {branch_code} created successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with tab2:
        st.markdown("### All Branches")
        df_branches = pd.read_sql("""
        SELECT b.branch_id, b.branch_code, b.branch_name, b.location, b.phone_number, b.email,
               s.full_name as manager_name, s.staff_code as manager_code, b.is_active, b.created_at
        FROM branches b
        LEFT JOIN staff s ON b.manager_id = s.staff_id
        ORDER BY b.created_at DESC
        """, conn)
        st.dataframe(df_branches, use_container_width=True)
    
    with tab3:
        st.markdown("### Branch Actions")
        branch_code = st.text_input("Branch Code")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Activate Branch"):
                if branch_code:
                    conn.execute(text("UPDATE branches SET is_active = 1 WHERE branch_code = :code"), {'code': branch_code})
                    conn.commit()
                    st.success("Branch activated!")
        
        with col2:
            if st.button("Deactivate Branch"):
                if branch_code:
                    conn.execute(text("UPDATE branches SET is_active = 0 WHERE branch_code = :code"), {'code': branch_code})
                    conn.commit()
                    st.success("Branch deactivated!")
        
        with col3:
            if st.button("Delete Branch"):
                if branch_code:
                    conn.execute(text("DELETE FROM branches WHERE branch_code = :code"), {'code': branch_code})
                    conn.commit()
                    st.success("Branch deleted!")

# 5. STAFF MANAGEMENT
elif view_mode == "👥 Manage Staff":
    st.subheader("👥 Staff Management")
    
    tab1, tab2, tab3 = st.tabs(["Create Staff", "View Staff", "Staff Actions"])
    
    with tab1:
        st.markdown("### Create New Staff Member")
        with st.form("create_staff_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                staff_code = st.text_input("Staff Code *", help="e.g., TELLER002")
                full_name = st.text_input("Full Name *")
                email = st.text_input("Email *")
                phone_number = st.text_input("Phone Number")
            
            with col2:
                national_id = st.text_input("National ID")
                role = st.selectbox("Role", ["TELLER", "RELATIONSHIP_MANAGER", "SUPERVISOR", "BRANCH_MANAGER", "ADMIN"])
                password = st.text_input("Password *", type="password", help="Staff login password")
                hire_date = st.date_input("Hire Date", value=datetime.now().date())
                
                # Get available branches
                df_branches = pd.read_sql("SELECT branch_id, branch_name, branch_code FROM branches WHERE is_active = 1", conn)
                if not df_branches.empty:
                    branch_options = [f"{row['branch_name']} ({row['branch_code']})" for _, row in df_branches.iterrows()]
                    selected_branch = st.selectbox("Branch", branch_options)
                else:
                    selected_branch = None
                    st.error("No active branches available!")
            
            submitted = st.form_submit_button("Create Staff", type="primary")
            
            if submitted and all([staff_code, full_name, email, password]) and selected_branch:
                try:
                    # Extract branch_id from selection
                    selected_branch_code = selected_branch.split("(")[1].split(")")[0]
                    branch_row = df_branches[df_branches['branch_code'] == selected_branch_code]
                    branch_id = int(branch_row.iloc[0]['branch_id'])
                    
                    conn.execute(text("""
                    INSERT INTO staff (staff_code, full_name, email, phone_number, national_id, role, branch_id, password_hash, hire_date, is_active)
                    VALUES (:staff_code, :full_name, :email, :phone_number, :national_id, :role, :branch_id, :password_hash, :hire_date, :is_active)
                    """), {
                        'staff_code': staff_code,
                        'full_name': full_name,
                        'email': email,
                        'phone_number': phone_number or None,
                        'national_id': national_id or None,
                        'role': role,
                        'branch_id': branch_id,
                        'password_hash': password,
                        'hire_date': hire_date,
                        'is_active': 1
                    })
                    
                    conn.commit()
                    st.success(f"✅ Staff member {staff_code} created successfully!")
                    st.info(f"🔑 Login credentials: {email} / {password}")
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    with tab2:
        st.markdown("### All Staff Members")
        df_staff = pd.read_sql("""
        SELECT s.staff_id, s.staff_code, s.full_name, s.email, s.phone_number, s.role,
               b.branch_name, b.branch_code, s.is_active, s.hire_date, s.created_at
        FROM staff s
        LEFT JOIN branches b ON s.branch_id = b.branch_id
        ORDER BY s.created_at DESC
        """, conn)
        st.dataframe(df_staff, use_container_width=True)
    
    with tab3:
        st.markdown("### Staff Actions")
        staff_code = st.text_input("Staff Code")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("Activate Staff"):
                if staff_code:
                    conn.execute(text("UPDATE staff SET is_active = 1 WHERE staff_code = :code"), {'code': staff_code})
                    conn.commit()
                    st.success("Staff activated!")
        
        with col2:
            if st.button("Deactivate Staff"):
                if staff_code:
                    conn.execute(text("UPDATE staff SET is_active = 0 WHERE staff_code = :code"), {'code': staff_code})
                    conn.commit()
                    st.success("Staff deactivated!")
        
        with col3:
            if st.button("Reset Password"):
                if staff_code:
                    new_password = "password123"
                    conn.execute(text("UPDATE staff SET password_hash = :pwd WHERE staff_code = :code"), 
                               {'pwd': new_password, 'code': staff_code})
                    conn.commit()
                    st.success(f"Password reset to: {new_password}")
        
        with col4:
            if st.button("Delete Staff"):
                if staff_code:
                    conn.execute(text("DELETE FROM staff WHERE staff_code = :code"), {'code': staff_code})
                    conn.commit()
                    st.success("Staff deleted!")

# 6. ACCOUNT MANAGEMENT
elif view_mode == "💰 Manage Accounts":
    st.subheader("💰 Account Management")
    
    tab1, tab2, tab3 = st.tabs(["View Accounts", "Account Actions", "Balance Adjustments"])
    
    with tab1:
        st.markdown("### All Accounts")
        df_accounts = pd.read_sql("""
        SELECT a.account_id, u.full_name, a.account_number, a.balance, a.currency, a.status, a.created_at
        FROM accounts a 
        JOIN users u ON a.user_id = u.user_id 
        ORDER BY a.balance DESC
        """, conn)
        st.dataframe(df_accounts, use_container_width=True)
    
    with tab2:
        st.markdown("### Account Actions")
        account_number = st.text_input("Account Number")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Freeze Account"):
                if account_number:
                    conn.execute(text("UPDATE accounts SET status = 'FROZEN' WHERE account_number = :acc"), {'acc': account_number})
                    conn.commit()
                    st.success("Account frozen!")
        
        with col2:
            if st.button("Activate Account"):
                if account_number:
                    conn.execute(text("UPDATE accounts SET status = 'ACTIVE' WHERE account_number = :acc"), {'acc': account_number})
                    conn.commit()
                    st.success("Account activated!")
        
        with col3:
            if st.button("Close Account"):
                if account_number:
                    conn.execute(text("UPDATE accounts SET status = 'DORMANT' WHERE account_number = :acc"), {'acc': account_number})
                    conn.commit()
                    st.success("Account closed!")
    
    with tab3:
        st.markdown("### Balance Adjustments")
        with st.form("balance_adjustment"):
            account_number = st.text_input("Account Number")
            adjustment_type = st.selectbox("Adjustment Type", ["Credit", "Debit"])
            amount = st.number_input("Amount (KES)", min_value=0.0)
            reason = st.text_input("Reason")
            
            if st.form_submit_button("Apply Adjustment"):
                if account_number and amount > 0:
                    try:
                        if adjustment_type == "Credit":
                            conn.execute(text("UPDATE accounts SET balance = balance + :amount WHERE account_number = :acc"), 
                                       {'amount': amount, 'acc': account_number})
                        else:
                            conn.execute(text("UPDATE accounts SET balance = balance - :amount WHERE account_number = :acc"), 
                                       {'amount': amount, 'acc': account_number})
                        
                        # Log transaction
                        conn.execute(text("""
                        INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                        SELECT account_id, :txn_type, :amount, :ref_code, :description, :created_at
                        FROM accounts WHERE account_number = :acc
                        """), {
                            'txn_type': f'ADMIN_{adjustment_type.upper()}',
                            'amount': amount,
                            'ref_code': f'ADJ{uuid.uuid4().hex[:8].upper()}',
                            'description': reason,
                            'created_at': datetime.now(),
                            'acc': account_number
                        })
                        
                        conn.commit()
                        st.success(f"✅ {adjustment_type} of KES {amount:,.2f} applied!")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# 7. LOAN MANAGEMENT
elif view_mode == "📋 Manage Loans":
    st.subheader("📋 Loan Management")
    
    tab1, tab2, tab3 = st.tabs(["View Loans", "Approve/Reject", "Manual Loan Creation"])
    
    with tab1:
        st.markdown("### All Loans")
        df_loans = pd.read_sql("""
        SELECT l.loan_id, u.full_name, l.principal_amount, l.total_due_amount, l.balance_remaining, l.status, l.created_at
        FROM loans l 
        JOIN users u ON l.user_id = u.user_id 
        ORDER BY l.created_at DESC
        """, conn)
        st.dataframe(df_loans, use_container_width=True)
    
    with tab2:
        st.markdown("### Loan Actions")
        
        # Show pending loans for approval
        st.subheader("⏳ Pending Loan Applications")
        df_pending = pd.read_sql("""
        SELECT l.loan_id, u.full_name, u.email, l.principal_amount, l.interest_rate, 
               l.total_due_amount, l.due_date, l.created_at
        FROM loans l 
        JOIN users u ON l.user_id = u.user_id 
        WHERE l.status = 'PENDING'
        ORDER BY l.created_at ASC
        """, conn)
        
        if not df_pending.empty:
            st.dataframe(df_pending, use_container_width=True)
            
            # Loan approval section
            st.markdown("### 🔍 Loan Approval")
            loan_id = st.number_input("Loan ID to Review", min_value=1)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Approve Loan"):
                    if loan_id:
                        try:
                            # Update loan status and set disbursement date
                            conn.execute(text("""
                                UPDATE loans SET status = 'ACTIVE', disbursement_date = %s 
                                WHERE loan_id = %s AND status = 'PENDING'
                            """), (datetime.now(), loan_id))
                            
                            # Get loan details for disbursement
                            loan_details = pd.read_sql(f"""
                                SELECT l.*, u.user_id FROM loans l 
                                JOIN users u ON l.user_id = u.user_id 
                                WHERE l.loan_id = {loan_id}
                            """, conn)
                            
                            if not loan_details.empty:
                                loan = loan_details.iloc[0]
                                
                                # Disburse funds to user account
                                conn.execute(text("""
                                    UPDATE accounts SET balance = balance + %s 
                                    WHERE user_id = %s
                                """), (float(loan['principal_amount']), int(loan['user_id'])))
                                
                                # Record disbursement transaction
                                ref_code = f"LDB{uuid.uuid4().hex[:8].upper()}"
                                conn.execute(text("""
                                    INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                                    SELECT account_id, 'LOAN_DISBURSEMENT', %s, %s, %s, %s
                                    FROM accounts WHERE user_id = %s
                                """), (float(loan['principal_amount']), ref_code, 
                                      f"Loan disbursement for Loan #{loan_id}", datetime.now(), int(loan['user_id'])))
                                
                                conn.commit()
                                st.success(f"✅ Loan {loan_id} approved and funds disbursed!")
                                st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Approval failed: {e}")
            
            with col2:
                if st.button("❌ Reject Loan"):
                    if loan_id:
                        conn.execute(text("UPDATE loans SET status = 'REJECTED' WHERE loan_id = %s"), (loan_id,))
                        conn.commit()
                        st.success(f"❌ Loan {loan_id} rejected!")
                        st.rerun()
            
            with col3:
                if st.button("🔍 View Details"):
                    if loan_id:
                        loan_detail = pd.read_sql(f"""
                            SELECT l.*, u.full_name, u.email, u.phone_number 
                            FROM loans l 
                            JOIN users u ON l.user_id = u.user_id 
                            WHERE l.loan_id = {loan_id}
                        """, conn)
                        if not loan_detail.empty:
                            st.json(loan_detail.iloc[0].to_dict())
        else:
            st.info("No pending loan applications")
        
        # Bulk actions
        st.markdown("### 🔄 Bulk Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve All Pending (Auto)"):
                try:
                    # Get all pending loans
                    pending_loans = pd.read_sql("SELECT * FROM loans WHERE status = 'PENDING'", conn)
                    
                    for _, loan in pending_loans.iterrows():
                        # Approve loan
                        conn.execute(text("""
                            UPDATE loans SET status = 'ACTIVE', disbursement_date = %s 
                            WHERE loan_id = %s
                        """), (datetime.now(), loan['loan_id']))
                        
                        # Disburse funds
                        conn.execute(text("""
                            UPDATE accounts SET balance = balance + %s 
                            WHERE user_id = %s
                        """), (float(loan['principal_amount']), int(loan['user_id'])))
                        
                        # Record transaction
                        ref_code = f"LDB{uuid.uuid4().hex[:8].upper()}"
                        conn.execute(text("""
                            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                            SELECT account_id, 'LOAN_DISBURSEMENT', %s, %s, %s, %s
                            FROM accounts WHERE user_id = %s
                        """), (float(loan['principal_amount']), ref_code, 
                              f"Auto-approved loan disbursement #{loan['loan_id']}", datetime.now(), int(loan['user_id'])))
                    
                    conn.commit()
                    st.success(f"✅ {len(pending_loans)} loans auto-approved!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Bulk approval failed: {e}")
        
        with col2:
            if st.button("❌ Reject All Pending"):
                conn.execute(text("UPDATE loans SET status = 'REJECTED' WHERE status = 'PENDING'"))
                conn.commit()
                st.success("❌ All pending loans rejected!")
                st.rerun()
        
        loan_id = st.number_input("Loan ID", min_value=1)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Approve Loan"):
                if loan_id:
                    conn.execute(text("UPDATE loans SET status = 'APPROVED' WHERE loan_id = :id"), {'id': loan_id})
                    conn.commit()
                    st.success("Loan approved!")
        
        with col2:
            if st.button("Reject Loan"):
                if loan_id:
                    conn.execute(text("UPDATE loans SET status = 'REJECTED' WHERE loan_id = :id"), {'id': loan_id})
                    conn.commit()
                    st.success("Loan rejected!")
        
        with col3:
            if st.button("Mark as Defaulted"):
                if loan_id:
                    conn.execute(text("UPDATE loans SET status = 'DEFAULTED' WHERE loan_id = :id"), {'id': loan_id})
                    conn.commit()
                    st.success("Loan marked as defaulted!")
    
    with tab3:
        st.markdown("### Create Manual Loan")
        with st.form("manual_loan"):
            user_email = st.text_input("User Email")
            loan_amount = st.number_input("Loan Amount (KES)", min_value=1000.0)
            tenure_days = st.number_input("Tenure (Days)", min_value=30, value=30)
            interest_rate = st.number_input("Interest Rate (%)", min_value=0.0, value=15.0)
            
            if st.form_submit_button("Create Loan"):
                if user_email and loan_amount > 0:
                    try:
                        # Get user ID
                        user_result = pd.read_sql(f"SELECT user_id FROM users WHERE email = '{user_email}'", conn)
                        if user_result.empty:
                            st.error("User not found!")
                        else:
                            user_id = user_result.iloc[0]['user_id']
                            total_due = loan_amount * (1 + interest_rate/100)
                            
                            conn.execute(text("""
                            INSERT INTO loans (user_id, principal_amount, total_due_amount, balance_remaining, status, created_at)
                            VALUES (:user_id, :principal, :total_due, :balance, :status, :created_at)
                            """), {
                                'user_id': user_id,
                                'principal': loan_amount,
                                'total_due': total_due,
                                'balance': total_due,
                                'status': 'APPROVED',
                                'created_at': datetime.now()
                            })
                            
                            conn.commit()
                            st.success(f"✅ Loan of KES {loan_amount:,.2f} created for {user_email}")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")

# 8. INSURANCE MANAGEMENT
elif view_mode == "🛡️ Manage Insurance":
    st.subheader("🛡️ Insurance Management")
    
    tab1, tab2 = st.tabs(["View Policies", "Create Policy"])
    
    with tab1:
        st.markdown("### All Insurance Policies")
        df_policies = pd.read_sql("""
        SELECT p.policy_id, u.full_name, ip.product_name, p.policy_number, p.status, p.cover_amount, p.premium_paid, p.created_at
        FROM user_policies p 
        LEFT JOIN users u ON p.user_id = u.user_id 
        LEFT JOIN insurance_products ip ON p.product_id = ip.product_id
        ORDER BY p.created_at DESC
        """, conn)
        if not df_policies.empty:
            st.dataframe(df_policies, use_container_width=True)
        else:
            st.info("No insurance policies found")
    
    with tab2:
        st.markdown("### Insurance Claims Management")
        
        # Show pending claims
        st.subheader("⏳ Pending Claims")
        df_pending_claims = pd.read_sql("""
        SELECT c.claim_id, c.claim_reference, u.full_name, ip.product_name, p.policy_number,
               c.claim_type, c.claim_amount, c.description, c.created_at
        FROM insurance_claims c
        JOIN user_policies p ON c.policy_id = p.policy_id
        JOIN users u ON p.user_id = u.user_id
        JOIN insurance_products ip ON p.product_id = ip.product_id
        WHERE c.status = 'SUBMITTED'
        ORDER BY c.created_at ASC
        """, conn)
        
        if not df_pending_claims.empty:
            st.dataframe(df_pending_claims, use_container_width=True)
            
            # Claim processing
            st.markdown("### 🔍 Process Claims")
            claim_id = st.number_input("Claim ID to Process", min_value=1)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("✅ Approve Claim"):
                    if claim_id:
                        try:
                            # Get claim details
                            claim_details = pd.read_sql(f"""
                                SELECT c.*, p.user_id, c.claim_amount
                                FROM insurance_claims c
                                JOIN user_policies p ON c.policy_id = p.policy_id
                                WHERE c.claim_id = {claim_id}
                            """, conn)
                            
                            if not claim_details.empty:
                                claim = claim_details.iloc[0]
                                
                                # Approve claim
                                conn.execute(text("UPDATE insurance_claims SET status = 'APPROVED' WHERE claim_id = %s"), (claim_id,))
                                
                                # Credit claim amount to user account
                                conn.execute(text("""
                                    UPDATE accounts SET balance = balance + %s 
                                    WHERE user_id = %s
                                """), (float(claim['claim_amount']), int(claim['user_id'])))
                                
                                # Record transaction
                                ref_code = f"ICL{uuid.uuid4().hex[:8].upper()}"
                                conn.execute(text("""
                                    INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                                    SELECT account_id, 'INSURANCE_CLAIM', %s, %s, %s, %s
                                    FROM accounts WHERE user_id = %s
                                """), (float(claim['claim_amount']), ref_code, 
                                      f"Insurance claim payout - {claim['claim_reference']}", datetime.now(), int(claim['user_id'])))
                                
                                conn.commit()
                                st.success(f"✅ Claim {claim_id} approved and amount credited!")
                                st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Claim approval failed: {e}")
            
            with col2:
                if st.button("❌ Reject Claim"):
                    if claim_id:
                        conn.execute(text("UPDATE insurance_claims SET status = 'REJECTED' WHERE claim_id = %s"), (claim_id,))
                        conn.commit()
                        st.success(f"❌ Claim {claim_id} rejected!")
                        st.rerun()
            
            with col3:
                if st.button("🔍 View Claim Details"):
                    if claim_id:
                        claim_detail = pd.read_sql(f"""
                            SELECT c.*, u.full_name, u.email, u.phone_number, ip.product_name, p.policy_number
                            FROM insurance_claims c
                            JOIN user_policies p ON c.policy_id = p.policy_id
                            JOIN users u ON p.user_id = u.user_id
                            JOIN insurance_products ip ON p.product_id = ip.product_id
                            WHERE c.claim_id = {claim_id}
                        """, conn)
                        if not claim_detail.empty:
                            st.json(claim_detail.iloc[0].to_dict())
        else:
            st.info("No pending claims")
        
        # All claims overview
        st.markdown("### 📊 All Claims")
        df_all_claims = pd.read_sql("""
        SELECT c.claim_id, c.claim_reference, u.full_name, ip.product_name, 
               c.claim_type, c.claim_amount, c.status, c.created_at
        FROM insurance_claims c
        JOIN user_policies p ON c.policy_id = p.policy_id
        JOIN users u ON p.user_id = u.user_id
        JOIN insurance_products ip ON p.product_id = ip.product_id
        ORDER BY c.created_at DESC
        LIMIT 50
        """, conn)
        
        if not df_all_claims.empty:
            st.dataframe(df_all_claims, use_container_width=True)
    
    with tab3:
        st.markdown("### Create Insurance Policy")
        with st.form("create_policy"):
            user_email = st.text_input("User Email")
            
            # Get available products
            df_products = pd.read_sql("SELECT * FROM insurance_products WHERE is_active = 1", conn)
            if not df_products.empty:
                product_options = [(row['product_id'], f"{row['product_name']} - KES {row['premium_amount']}/month") 
                                 for _, row in df_products.iterrows()]
                selected_product = st.selectbox("Insurance Product", product_options, format_func=lambda x: x[1])
                
                coverage_amount = st.number_input("Coverage Amount (KES)", min_value=10000.0, value=500000.0)
                premium_amount = st.number_input("Premium Amount (KES)", min_value=50.0, value=150.0)
                
                if st.form_submit_button("Create Policy"):
                    if user_email:
                        try:
                            user_result = pd.read_sql(f"SELECT user_id FROM users WHERE email = '{user_email}'", conn)
                            if user_result.empty:
                                st.error("User not found!")
                            else:
                                user_id = user_result.iloc[0]['user_id']
                                policy_number = f"POL{uuid.uuid4().hex[:8].upper()}"
                                
                                # Calculate dates
                                start_date = datetime.now().date()
                                end_date = datetime(start_date.year + 1, start_date.month, start_date.day).date()
                                
                                conn.execute(text("""
                                INSERT INTO user_policies (user_id, product_id, policy_number, start_date, end_date,
                                                          status, premium_paid, cover_amount, created_at)
                                VALUES (%s, %s, %s, %s, %s, 'ACTIVE', %s, %s, %s)
                                """), (user_id, selected_product[0], policy_number, start_date, end_date,
                                      premium_amount, coverage_amount, datetime.now()))
                                
                                conn.commit()
                                st.success(f"✅ Policy {policy_number} created for {user_email}")
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
            else:
                st.error("No insurance products available!")

# 9. TRANSACTION MONITORING
elif view_mode == "💸 Transactions":
    st.subheader("💸 Transaction Monitoring")
    
    # Transaction filters
    col1, col2, col3 = st.columns(3)
    with col1:
        txn_type_filter = st.selectbox("Transaction Type", ["All", "DEPOSIT", "WITHDRAWAL", "TRANSFER", "LOAN", "ADMIN_CREDIT", "ADMIN_DEBIT"])
    with col2:
        date_filter = st.date_input("From Date")
    with col3:
        amount_filter = st.number_input("Min Amount", min_value=0.0)
    
    # Build query
    query = """
    SELECT t.transaction_id, u.full_name, a.account_number, t.txn_type, t.amount, t.reference_code, t.description, t.created_at
    FROM transactions t 
    JOIN accounts a ON t.account_id = a.account_id 
    JOIN users u ON a.user_id = u.user_id 
    WHERE 1=1
    """
    
    if txn_type_filter != "All":
        query += f" AND t.txn_type = '{txn_type_filter}'"
    if amount_filter > 0:
        query += f" AND t.amount >= {amount_filter}"
    
    query += " ORDER BY t.created_at DESC LIMIT 100"
    
    df_transactions = pd.read_sql(query, conn)
    st.dataframe(df_transactions, use_container_width=True)
    
    # Transaction summary
    if not df_transactions.empty:
        st.markdown("### Transaction Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Transactions", len(df_transactions))
        col2.metric("Total Amount", f"KES {df_transactions['amount'].sum():,.2f}")
        col3.metric("Average Amount", f"KES {df_transactions['amount'].mean():,.2f}")

# 10. SYSTEM SETTINGS
elif view_mode == "⚙️ System Settings":
    st.subheader("⚙️ System Settings")
    
    tab1, tab2 = st.tabs(["Database Stats", "System Actions"])
    
    with tab1:
        st.markdown("### Database Statistics")
        
        # Table counts
        tables = ['users', 'accounts', 'businesses', 'branches', 'staff', 'loans', 'transactions', 'user_policies']
        stats_data = []
        
        for table in tables:
            try:
                count = pd.read_sql(f"SELECT COUNT(*) as count FROM {table}", conn).iloc[0]['count']
                stats_data.append({'Table': table.title(), 'Records': count})
            except:
                stats_data.append({'Table': table.title(), 'Records': 'Error'})
        
        df_stats = pd.DataFrame(stats_data)
        st.dataframe(df_stats, use_container_width=True)
    
    with tab2:
        st.markdown("### System Actions")
        st.warning("⚠️ These actions are irreversible!")
        
        if st.button("🗑️ Clear All Transactions", type="secondary"):
            conn.execute(text("DELETE FROM transactions"))
            conn.commit()
            st.success("All transactions cleared!")
        
        if st.button("🗑️ Clear All Loans", type="secondary"):
            conn.execute(text("DELETE FROM loans"))
            conn.commit()
            st.success("All loans cleared!")
        
        if st.button("🔄 Reset All Account Balances to 10,000", type="secondary"):
            conn.execute(text("UPDATE accounts SET balance = 10000"))
            conn.commit()
            st.success("All account balances reset!")