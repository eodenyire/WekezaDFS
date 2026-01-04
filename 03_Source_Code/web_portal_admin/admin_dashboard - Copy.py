import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from sqlalchemy import create_engine
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Wekeza Risk Admin", layout="wide")
#API_URL = "http://127.0.0.1:8000"
DB_URL = "mysql+mysqlconnector://root:root@localhost/wekeza_dfs_db"

# If running in Docker, use 'http://backend:8000', else 'http://127.0.0.1:8000'
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- DATABASE CONNECTION ---
@st.cache_resource
def get_db_connection():
    return create_engine(DB_URL)

engine = get_db_connection()

# --- SIDEBAR: RISK CONTROLS ---
st.sidebar.title("👮 Risk HQ")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2344/2344147.png", width=100)
risk_threshold = st.sidebar.slider("Global Risk Score Threshold", 0, 1000, 600)
st.sidebar.markdown("---")
st.sidebar.info(f"System rejects loans below score: **{risk_threshold}**")

# --- MAIN DASHBOARD ---
st.title("🏦 Wekeza Bank | Digital Risk Cockpit")

# 1. KPI METRICS (Real-Time)
col1, col2, col3, col4 = st.columns(4)

with engine.connect() as conn:
    # Total Users
    total_users = pd.read_sql("SELECT COUNT(*) as count FROM users", conn).iloc[0]['count']
    # Total Disbursed
    total_loans = pd.read_sql("SELECT SUM(principal_amount) as amt FROM loans", conn).iloc[0]['amt']
    # Active Loans
    active_count = pd.read_sql("SELECT COUNT(*) as count FROM loans WHERE status='ACTIVE'", conn).iloc[0]['count']
    # NPL (Simulated as Defaulted)
    npl_count = pd.read_sql("SELECT COUNT(*) as count FROM loans WHERE status='DEFAULTED'", conn).iloc[0]['count']

col1.metric("Total Customers", f"{total_users}")
col2.metric("Total Disbursed", f"KES {total_loans:,.0f}" if total_loans else "KES 0")
col3.metric("Active Loans", f"{active_count}")
col4.metric("NPL Ratio", f"{round((npl_count/active_count * 100), 2)}%" if active_count > 0 else "0%")

st.markdown("---")

# 2. RISK MODEL PERFORMANCE (The "Alpha Model" View)
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Risk Score Distribution")
    df_scores = pd.read_sql("SELECT credit_score, decision FROM risk_scores", conn)
    if not df_scores.empty:
        fig = px.histogram(df_scores, x="credit_score", color="decision", nbins=20, 
                           color_discrete_map={"APPROVED": "green", "REJECTED": "red"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No scoring data yet.")

with c2:
    st.subheader("📉 Loan Status Breakdown")
    df_loans = pd.read_sql("SELECT status, COUNT(*) as count FROM loans GROUP BY status", conn)
    if not df_loans.empty:
        fig2 = px.pie(df_loans, values='count', names='status', hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No loan data yet.")

# 3. LIVE TRANSACTIONS TABLE
st.subheader("🔍 Recent Loan Applications")
df_recent = pd.read_sql("""
    SELECT l.loan_id, u.full_name, l.principal_amount, l.status, l.created_at 
    FROM loans l 
    JOIN users u ON l.user_id = u.user_id 
    ORDER BY l.created_at DESC LIMIT 10
""", conn)
st.dataframe(df_recent, use_container_width=True)

# 4. MANUAL OVERRIDE (For "Sarah the Credit Officer")
with st.expander("🚨 Manual Loan Override"):
    st.write("Use this to force-approve a rejected loan (Audit Log will be created).")
    loan_id_input = st.number_input("Enter Loan ID", min_value=1)
    if st.button("Force Approve"):
        st.success(f"Loan {loan_id_input} moved to REVIEW queue.")