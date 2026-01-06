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
    "📈 Analytics & Reports",
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