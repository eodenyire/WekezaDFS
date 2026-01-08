import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
import os

st.set_page_config(page_title="Wekeza Risk Admin", layout="wide")

# Connect to DB inside Docker
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_URL = f"mysql+mysqlconnector://root:root@{DB_HOST}/wekeza_dfs_db"

@st.cache_resource
def get_db():
    return create_engine(DB_URL)

try:
    engine = get_db()
    conn = engine.connect()
except:
    st.error("Database Connection Failed. Ensure Docker is running.")
    st.stop()

# --- SIDEBAR ---
st.sidebar.title("👮 Risk Ops")
st.sidebar.info("Wekeza Admin Console")

# --- KPI METRICS ---
st.title("🏦 Wekeza Bank | Executive View")

col1, col2, col3, col4 = st.columns(4)
total_users = pd.read_sql("SELECT COUNT(*) as c FROM users", conn).iloc[0]['c']
total_loans = pd.read_sql("SELECT SUM(principal_amount) as c FROM loans", conn).iloc[0]['c']
active_loans = pd.read_sql("SELECT COUNT(*) as c FROM loans WHERE status='ACTIVE'", conn).iloc[0]['c']
insurance_sold = pd.read_sql("SELECT COUNT(*) as c FROM user_policies", conn).iloc[0]['c']

col1.metric("Total Customers", total_users)
col2.metric("Total Disbursed", f"KES {total_loans:,.0f}" if total_loans else "0")
col3.metric("Active Loans", active_loans)
col4.metric("Policies Sold", insurance_sold)

st.markdown("---")

# --- TABS ---
t1, t2, t3 = st.tabs(["📊 Risk Analysis", "📜 Audit Logs", "🛡️ Insurance"])

with t1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Credit Scores")
        df = pd.read_sql("SELECT credit_score, decision FROM risk_scores", conn)
        if not df.empty:
            fig = px.histogram(df, x="credit_score", color="decision", color_discrete_map={"APPROVED":"green", "REJECTED":"red"})
            st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.subheader("Loan Status")
        df_l = pd.read_sql("SELECT status, COUNT(*) as c FROM loans GROUP BY status", conn)
        if not df_l.empty:
            st.plotly_chart(px.pie(df_l, values='c', names='status', hole=0.4), use_container_width=True)

with t2:
    st.subheader("Live Transaction Feed")
    df_txn = pd.read_sql("SELECT created_at, txn_type, amount, description FROM transactions ORDER BY created_at DESC LIMIT 50", conn)
    st.dataframe(df_txn, use_container_width=True)

with t3:
    st.subheader("Active Policies")
    df_pol = pd.read_sql("SELECT policy_number, status, start_date FROM user_policies", conn)
    st.dataframe(df_pol, use_container_width=True)