import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import uuid
import json
import hashlib

st.set_page_config(page_title="Wekeza Corporate Banking", layout="wide", page_icon="🏢")

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

if 'biz_user_data' not in st.session_state: 
    st.session_state['biz_user_data'] = None

def login_register_screen():
    st.title("🏢 Corporate Banking")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register Business", "Admin"])
    
    with tab1:
        st.subheader("Director Login")
        email = st.text_input("Director Email", key="biz_login_email")
        password = st.text_input("Password", type="password", key="biz_login_password")
        
        if st.button("Login", key="biz_login_btn"):
            if email and password:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor(dictionary=True)
                    
                    # Check user credentials (must be business user)
                    cursor.execute("""
                        SELECT user_id, full_name, email, business_id 
                        FROM users 
                        WHERE email = %s AND password_hash = %s AND is_active = 1 AND business_id IS NOT NULL
                    """, (email, password))
                    
                    user = cursor.fetchone()
                    conn.close()
                    
                    if user:
                        st.session_state['biz_user_data'] = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or not a business account")
                        
                except Exception as e:
                    st.error(f"Login failed: {e}")
    
    with tab2:
        st.subheader("Register New Business")
        
        with st.form("register_business_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                biz_name = st.text_input("Business Name *")
                reg_no = st.text_input("Registration Number *")
                kra_pin = st.text_input("KRA PIN *")
                sector = st.selectbox("Sector", ["Technology", "Agriculture", "Retail", "Manufacturing", "Services"])
            
            with col2:
                dir_name = st.text_input("Director Name *")
                dir_email = st.text_input("Director Email *")
                dir_password = st.text_input("Director Password *", type="password")
                dir_confirm = st.text_input("Confirm Password *", type="password")
            
            submitted = st.form_submit_button("Register Business", type="primary")
            
            if submitted and all([biz_name, reg_no, kra_pin, dir_name, dir_email, dir_password]):
                if dir_password != dir_confirm:
                    st.error("Passwords don't match!")
                else:
                    try:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        
                        # Check if business already exists
                        cursor.execute("SELECT registration_no FROM businesses WHERE registration_no = %s", (reg_no,))
                        if cursor.fetchone():
                            st.error("Business already registered! Please visit a branch for assistance.")
                        else:
                            # Create business
                            cursor.execute("""
                                INSERT INTO businesses (business_name, registration_no, kra_pin, sector, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (biz_name, reg_no, kra_pin, sector, datetime.now()))
                            
                            business_id = cursor.lastrowid
                            
                            # Create director user
                            cursor.execute("""
                                INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, business_id, created_at)
                                VALUES (%s, %s, %s, %s, %s, %s, 1, %s, %s)
                            """, (dir_name, dir_email, '0700000000', f"DIR{reg_no}", dir_password, 'TIER_3', business_id, datetime.now()))
                            
                            # Create business account
                            account_number = f"BIZ{1000000 + business_id}"
                            cursor.execute("""
                                INSERT INTO accounts (business_id, account_number, balance, currency, status, created_at)
                                VALUES (%s, %s, 50000.00, 'KES', 'ACTIVE', %s)
                            """, (business_id, account_number, datetime.now()))
                            
                            conn.commit()
                            conn.close()
                            
                            st.success(f"✅ Business registered successfully!")
                            st.info(f"🏢 Business: {biz_name}")
                            st.info(f"🏦 Account: {account_number}")
                            st.info(f"💰 Initial Balance: KES 50,000")
                            st.info(f"🔑 Director login: {dir_email}")
                            
                    except Exception as e:
                        st.error(f"Registration failed: {e}")
    
    with tab3:
        st.subheader("Admin Access")
        admin_user = st.text_input("Username", value="admin", key="biz_admin_user")
        admin_pass = st.text_input("Password", type="password", value="admin", key="biz_admin_pass")
        
        if st.button("Admin Login", key="biz_admin_btn"):
            if admin_user == "admin" and admin_pass == "admin":
                st.session_state['biz_user_data'] = {
                    'user_id': 0,
                    'full_name': 'Administrator',
                    'email': 'admin',
                    'is_admin': True
                }
                st.success("Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")

def dashboard():
    user_data = st.session_state['biz_user_data']
    
    # Admin dashboard
    if user_data.get('is_admin'):
        st.title("🔧 Admin Quick Access")
        st.info("For full admin features, visit: http://localhost:8503")
        
        if st.button("Logout"): 
            st.session_state['biz_user_data'] = None
            st.rerun()
        return
    
    # Business dashboard
    st.sidebar.title("🏢 Corporate Banking")
    st.sidebar.success("KYC Verified")
    
    user_id = user_data['user_id']
    business_id = user_data['business_id']
    
    # Fetch business account data
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get business account
        cursor.execute("""
            SELECT a.account_number, a.balance, a.status, b.business_name
            FROM accounts a
            JOIN businesses b ON a.business_id = b.business_id
            WHERE a.business_id = %s
        """, (business_id,))
        
        account_data = cursor.fetchone()
        conn.close()
        
        if not account_data:
            st.error("Business account not found")
            return
            
    except Exception as e:
        st.error(f"Database error: {e}")
        return
    
    st.title("Corporate Command Center")
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    c1.metric("Operating Account", f"KES {account_data['balance']:,.2f}")
    c2.metric("Account Status", account_data['status'])
    c3.metric("Director", user_data['full_name'])

    # Main Business Banking Tabs - Finacle-aligned
    tab_accounts, tab_payments, tab_credit, tab_insure, tab_settings = st.tabs([
        "🏦 Accounts & Cash", "💸 Payments & Transfers", "💰 Credit & Lending", "🛡️ Insurance", "⚙️ Settings"
    ])

    with tab_accounts:
        # Import and use comprehensive account management
        from business_portal_sections import render_accounts_section
        render_accounts_section(user_data)

    with tab_payments:
        # Import and use comprehensive payments section
        from business_portal_sections import render_payments_section
        render_payments_section(user_data)

    with tab_credit:
        # Import and use comprehensive credit section
        from business_portal_sections import render_credit_section
        render_credit_section(user_data)

    with tab_insure:
        # Import and use comprehensive insurance section
        from business_insurance_sections import render_insurance_section
        render_insurance_section(user_data)

    with tab_settings:
        # Import and use comprehensive settings section
        from business_settings_sections import render_settings_section
        render_settings_section(user_data)
    
    if st.sidebar.button("Logout"):
        st.session_state['biz_user_data'] = None
        st.rerun()

if st.session_state.get('biz_user_data'): 
    dashboard()
else: 
    login_register_screen()