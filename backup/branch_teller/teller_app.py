import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import uuid

st.set_page_config(page_title="Wekeza Branch Teller", layout="wide", page_icon="🏪")

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

if 'teller_data' not in st.session_state: 
    st.session_state['teller_data'] = None

def teller_login():
    st.title("🏪 Wekeza Branch Teller System")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Teller Login")
        teller_id = st.text_input("Teller ID", value="TELLER001")
        password = st.text_input("Password", type="password", value="teller123")
        
        if st.button("Login", type="primary"):
            # Simple teller authentication
            if teller_id and password == "teller123":
                st.session_state['teller_data'] = {
                    'teller_id': teller_id,
                    'name': f"Teller {teller_id}",
                    'branch': 'Main Branch'
                }
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid teller credentials")
    
    with col2:
        st.info("""
        **Branch Teller System**
        
        **Default Login:**
        - Teller ID: TELLER001
        - Password: teller123
        
        **Features:**
        - Cash deposits and withdrawals
        - Account inquiries
        - Customer registration
        - Transaction history
        - Daily cash management
        """)

def teller_dashboard():
    teller_data = st.session_state['teller_data']
    
    # Add sidebar information
    st.sidebar.title("🏪 Branch Teller")
    st.sidebar.success(f"Logged in: {teller_data['teller_id']}")
    st.sidebar.markdown("### 🔗 Quick Links")
    st.sidebar.markdown("- [Admin Panel](http://localhost:8503) 🏦")
    st.sidebar.markdown("- [Customer Portal](http://localhost:8502) 👤")
    st.sidebar.markdown("- [Business Portal](http://localhost:8504) 🏢")
    
    if st.sidebar.button("🚪 Logout"):
        st.session_state['teller_data'] = None
        st.rerun()
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🏪 Branch Teller Dashboard")
    with col2:
        st.metric("Teller", teller_data['teller_id'])
    
    st.markdown("---")
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "💰 Cash Operations", 
        "👤 Customer Lookup", 
        "📊 Account Inquiry", 
        "📝 New Customer", 
        "📈 Reports"
    ])
    
    with tab1:
        cash_operations()
    
    with tab2:
        customer_lookup()
    
    with tab3:
        account_inquiry()
    
    with tab4:
        new_customer_registration()
    
    with tab5:
        teller_reports()

def cash_operations():
    st.subheader("💰 Cash Deposit & Withdrawal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💵 Cash Deposit")
        with st.form("deposit_form"):
            deposit_method = st.radio("Customer Identification", ["National ID", "Account Number", "Phone Number"])
            
            if deposit_method == "National ID":
                customer_id = st.text_input("National ID")
            elif deposit_method == "Account Number":
                customer_id = st.text_input("Account Number")
            else:
                customer_id = st.text_input("Phone Number")
            
            deposit_amount = st.number_input("Deposit Amount (KES)", min_value=1.0, step=100.0)
            deposit_notes = st.text_area("Notes (Optional)")
            
            if st.form_submit_button("Process Deposit", type="primary"):
                if customer_id and deposit_amount > 0:
                    process_deposit(customer_id, deposit_amount, deposit_method, deposit_notes)
    
    with col2:
        st.markdown("### 💸 Cash Withdrawal")
        with st.form("withdrawal_form"):
            withdrawal_method = st.radio("Customer Identification", ["National ID", "Account Number", "Phone Number"], key="withdrawal_method")
            
            if withdrawal_method == "National ID":
                customer_id_w = st.text_input("National ID", key="withdrawal_id")
            elif withdrawal_method == "Account Number":
                customer_id_w = st.text_input("Account Number", key="withdrawal_acc")
            else:
                customer_id_w = st.text_input("Phone Number", key="withdrawal_phone")
            
            withdrawal_amount = st.number_input("Withdrawal Amount (KES)", min_value=1.0, step=100.0)
            withdrawal_notes = st.text_area("Notes (Optional)", key="withdrawal_notes")
            
            if st.form_submit_button("Process Withdrawal", type="primary"):
                if customer_id_w and withdrawal_amount > 0:
                    process_withdrawal(customer_id_w, withdrawal_amount, withdrawal_method, withdrawal_notes)

def process_deposit(customer_id, amount, method, notes):
    """Process cash deposit"""
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor(dictionary=True)
        
        # Find customer account
        if method == "National ID":
            cursor.execute("""
                SELECT u.user_id, u.full_name, u.national_id, a.account_id, a.account_number, a.balance, a.status
                FROM users u 
                JOIN accounts a ON u.user_id = a.user_id 
                WHERE u.national_id = %s AND u.is_active = 1
            """, (customer_id,))
        elif method == "Account Number":
            cursor.execute("""
                SELECT u.user_id, u.full_name, u.national_id, a.account_id, a.account_number, a.balance, a.status
                FROM users u 
                JOIN accounts a ON u.user_id = a.user_id 
                WHERE a.account_number = %s AND u.is_active = 1
            """, (customer_id,))
        else:  # Phone Number
            cursor.execute("""
                SELECT u.user_id, u.full_name, u.national_id, a.account_id, a.account_number, a.balance, a.status
                FROM users u 
                JOIN accounts a ON u.user_id = a.user_id 
                WHERE u.phone_number = %s AND u.is_active = 1
            """, (customer_id,))
        
        account = cursor.fetchone()
        
        if not account:
            st.error("❌ Customer not found or account inactive")
            conn.close()
            return
        
        if account['status'] != 'ACTIVE':
            st.error(f"❌ Account is {account['status']}. Cannot process deposit.")
            conn.close()
            return
        
        # Update account balance
        new_balance = float(account['balance']) + amount
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, account['account_id']))
        
        # Record transaction
        ref_code = f"DEP{uuid.uuid4().hex[:8].upper()}"
        teller_id = st.session_state['teller_data']['teller_id']
        
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, 'DEPOSIT', %s, %s, %s, %s)
        """, (account['account_id'], amount, ref_code, f"Cash deposit by {teller_id}. {notes}", datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Success message
        st.success(f"✅ Deposit Successful!")
        st.info(f"""
        **Transaction Details:**
        - Customer: {account['full_name']}
        - Account: {account['account_number']}
        - Amount: KES {amount:,.2f}
        - New Balance: KES {new_balance:,.2f}
        - Reference: {ref_code}
        """)
        
    except Exception as e:
        st.error(f"❌ Deposit failed: {e}")

def process_withdrawal(customer_id, amount, method, notes):
    """Process cash withdrawal"""
    try:
        conn = get_db_connection()
        if not conn:
            return
        
        cursor = conn.cursor(dictionary=True)
        
        # Find customer account
        if method == "National ID":
            cursor.execute("""
                SELECT u.user_id, u.full_name, u.national_id, a.account_id, a.account_number, a.balance, a.status
                FROM users u 
                JOIN accounts a ON u.user_id = a.user_id 
                WHERE u.national_id = %s AND u.is_active = 1
            """, (customer_id,))
        elif method == "Account Number":
            cursor.execute("""
                SELECT u.user_id, u.full_name, u.national_id, a.account_id, a.account_number, a.balance, a.status
                FROM users u 
                JOIN accounts a ON u.user_id = a.user_id 
                WHERE a.account_number = %s AND u.is_active = 1
            """, (customer_id,))
        else:  # Phone Number
            cursor.execute("""
                SELECT u.user_id, u.full_name, u.national_id, a.account_id, a.account_number, a.balance, a.status
                FROM users u 
                JOIN accounts a ON u.user_id = a.user_id 
                WHERE u.phone_number = %s AND u.is_active = 1
            """, (customer_id,))
        
        account = cursor.fetchone()
        
        if not account:
            st.error("❌ Customer not found or account inactive")
            conn.close()
            return
        
        if account['status'] != 'ACTIVE':
            st.error(f"❌ Account is {account['status']}. Cannot process withdrawal.")
            conn.close()
            return
        
        if float(account['balance']) < amount:
            st.error(f"❌ Insufficient funds. Available: KES {account['balance']:,.2f}")
            conn.close()
            return
        
        # Update account balance
        new_balance = float(account['balance']) - amount
        cursor.execute("""
            UPDATE accounts SET balance = %s WHERE account_id = %s
        """, (new_balance, account['account_id']))
        
        # Record transaction
        ref_code = f"WDL{uuid.uuid4().hex[:8].upper()}"
        teller_id = st.session_state['teller_data']['teller_id']
        
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            VALUES (%s, 'WITHDRAWAL', %s, %s, %s, %s)
        """, (account['account_id'], amount, ref_code, f"Cash withdrawal by {teller_id}. {notes}", datetime.now()))
        
        conn.commit()
        conn.close()
        
        # Success message
        st.success(f"✅ Withdrawal Successful!")
        st.info(f"""
        **Transaction Details:**
        - Customer: {account['full_name']}
        - Account: {account['account_number']}
        - Amount: KES {amount:,.2f}
        - New Balance: KES {new_balance:,.2f}
        - Reference: {ref_code}
        """)
        
    except Exception as e:
        st.error(f"❌ Withdrawal failed: {e}")

def customer_lookup():
    st.subheader("👤 Customer Lookup")
    
    search_method = st.radio("Search by:", ["National ID", "Account Number", "Phone Number", "Email"])
    search_value = st.text_input(f"Enter {search_method}")
    
    if st.button("Search Customer") and search_value:
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            if search_method == "National ID":
                cursor.execute("""
                    SELECT u.*, a.account_number, a.balance, a.status as account_status
                    FROM users u 
                    LEFT JOIN accounts a ON u.user_id = a.user_id 
                    WHERE u.national_id = %s
                """, (search_value,))
            elif search_method == "Account Number":
                cursor.execute("""
                    SELECT u.*, a.account_number, a.balance, a.status as account_status
                    FROM users u 
                    JOIN accounts a ON u.user_id = a.user_id 
                    WHERE a.account_number = %s
                """, (search_value,))
            elif search_method == "Phone Number":
                cursor.execute("""
                    SELECT u.*, a.account_number, a.balance, a.status as account_status
                    FROM users u 
                    LEFT JOIN accounts a ON u.user_id = a.user_id 
                    WHERE u.phone_number = %s
                """, (search_value,))
            else:  # Email
                cursor.execute("""
                    SELECT u.*, a.account_number, a.balance, a.status as account_status
                    FROM users u 
                    LEFT JOIN accounts a ON u.user_id = a.user_id 
                    WHERE u.email = %s
                """, (search_value,))
            
            customer = cursor.fetchone()
            conn.close()
            
            if customer:
                st.success("✅ Customer Found")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Customer Information")
                    st.write(f"**Name:** {customer['full_name']}")
                    st.write(f"**Email:** {customer['email']}")
                    st.write(f"**Phone:** {customer['phone_number']}")
                    st.write(f"**National ID:** {customer['national_id']}")
                    st.write(f"**KYC Tier:** {customer['kyc_tier']}")
                    st.write(f"**Status:** {'Active' if customer['is_active'] else 'Inactive'}")
                
                with col2:
                    st.markdown("### Account Information")
                    if customer['account_number']:
                        st.write(f"**Account Number:** {customer['account_number']}")
                        st.write(f"**Balance:** KES {customer['balance']:,.2f}")
                        st.write(f"**Account Status:** {customer['account_status']}")
                    else:
                        st.warning("No account found for this customer")
            else:
                st.error("❌ Customer not found")
                
        except Exception as e:
            st.error(f"❌ Search failed: {e}")

def account_inquiry():
    st.subheader("📊 Account Inquiry & Transaction History")
    
    account_number = st.text_input("Account Number")
    
    if st.button("Get Account Details") and account_number:
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            # Get account details
            cursor.execute("""
                SELECT u.full_name, u.email, u.phone_number, a.*
                FROM accounts a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.account_number = %s
            """, (account_number,))
            
            account = cursor.fetchone()
            
            if not account:
                st.error("❌ Account not found")
                conn.close()
                return
            
            # Display account info
            col1, col2, col3 = st.columns(3)
            col1.metric("Account Balance", f"KES {account['balance']:,.2f}")
            col2.metric("Account Status", account['status'])
            col3.metric("Currency", account['currency'])
            
            st.markdown("### Customer Details")
            st.write(f"**Name:** {account['full_name']}")
            st.write(f"**Email:** {account['email']}")
            st.write(f"**Phone:** {account['phone_number']}")
            
            # Get recent transactions
            cursor.execute("""
                SELECT * FROM transactions 
                WHERE account_id = %s 
                ORDER BY created_at DESC 
                LIMIT 20
            """, (account['account_id'],))
            
            transactions = cursor.fetchall()
            conn.close()
            
            if transactions:
                st.markdown("### Recent Transactions")
                df = pd.DataFrame(transactions)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df[['created_at', 'txn_type', 'amount', 'reference_code', 'description']], use_container_width=True)
            else:
                st.info("No transactions found")
                
        except Exception as e:
            st.error(f"❌ Inquiry failed: {e}")

def new_customer_registration():
    st.subheader("📝 New Customer Registration")
    
    with st.form("new_customer_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email *")
            phone = st.text_input("Phone Number *")
        
        with col2:
            national_id = st.text_input("National ID *")
            initial_deposit = st.number_input("Initial Deposit (KES)", min_value=0.0, value=1000.0)
            kyc_tier = st.selectbox("KYC Tier", ["TIER_1", "TIER_2", "TIER_3"])
        
        password = st.text_input("Initial Password *", type="password", help="Customer will use this to login online")
        
        if st.form_submit_button("Register Customer", type="primary"):
            if all([full_name, email, phone, national_id, password]):
                try:
                    conn = get_db_connection()
                    if not conn:
                        return
                    
                    cursor = conn.cursor()
                    
                    # Check if customer already exists
                    cursor.execute("SELECT email FROM users WHERE email = %s OR national_id = %s", (email, national_id))
                    if cursor.fetchone():
                        st.error("❌ Customer already exists with this email or National ID")
                        conn.close()
                        return
                    
                    # Create customer
                    cursor.execute("""
                        INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, 1, %s)
                    """, (full_name, email, phone, national_id, password, kyc_tier, datetime.now()))
                    
                    user_id = cursor.lastrowid
                    
                    # Create account
                    account_number = f"ACC{1000000 + user_id}"
                    cursor.execute("""
                        INSERT INTO accounts (user_id, account_number, balance, currency, status, created_at)
                        VALUES (%s, %s, %s, 'KES', 'ACTIVE', %s)
                    """, (user_id, account_number, initial_deposit, datetime.now()))
                    
                    account_id = cursor.lastrowid
                    
                    # Record initial deposit transaction if > 0
                    if initial_deposit > 0:
                        ref_code = f"DEP{uuid.uuid4().hex[:8].upper()}"
                        teller_id = st.session_state['teller_data']['teller_id']
                        
                        cursor.execute("""
                            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
                            VALUES (%s, 'DEPOSIT', %s, %s, %s, %s)
                        """, (account_id, initial_deposit, ref_code, f"Initial deposit by {teller_id}", datetime.now()))
                    
                    conn.commit()
                    conn.close()
                    
                    st.success("✅ Customer registered successfully!")
                    st.info(f"""
                    **Customer Details:**
                    - Name: {full_name}
                    - Account: {account_number}
                    - Initial Balance: KES {initial_deposit:,.2f}
                    - Login: {email} / {password}
                    """)
                    
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")

def teller_reports():
    st.subheader("📈 Teller Reports")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Today's Summary")
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor(dictionary=True)
            
            # Today's transactions
            cursor.execute("""
                SELECT 
                    txn_type,
                    COUNT(*) as count,
                    SUM(amount) as total
                FROM transactions 
                WHERE DATE(created_at) = CURDATE()
                GROUP BY txn_type
            """)
            
            today_stats = cursor.fetchall()
            
            if today_stats:
                df = pd.DataFrame(today_stats)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No transactions today")
            
            conn.close()
            
        except Exception as e:
            st.error(f"❌ Report failed: {e}")
    
    with col2:
        st.markdown("### Quick Stats")
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Total customers
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
            total_customers = cursor.fetchone()[0]
            
            # Total accounts
            cursor.execute("SELECT COUNT(*) FROM accounts WHERE status = 'ACTIVE'")
            total_accounts = cursor.fetchone()[0]
            
            # Total deposits
            cursor.execute("SELECT SUM(balance) FROM accounts WHERE status = 'ACTIVE'")
            total_deposits = cursor.fetchone()[0] or 0
            
            conn.close()
            
            st.metric("Active Customers", total_customers)
            st.metric("Active Accounts", total_accounts)
            st.metric("Total Deposits", f"KES {total_deposits:,.2f}")
            
        except Exception as e:
            st.error(f"❌ Stats failed: {e}")

# Main app logic
if st.session_state['teller_data']:
    teller_dashboard()
else:
    teller_login()