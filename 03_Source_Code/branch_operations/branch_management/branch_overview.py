# branch_management/branch_overview.py
import streamlit as st
import os
from branch_management.common import get_branch_manager_info
from branch_management.branch_cash_position import render_branch_cash_position_ui
from branch_management.branch_performance import render_branch_performance_ui
from branch_management.branch_reporting import render_reporting_ui
from branch_management.staff_management import render_staff_management_ui
from branch_management.end_of_day_approval import render_eod_approval_ui
from branch_management.overrides import render_overrides_ui

# -----------------------------
# Configure Streamlit Page
# -----------------------------
st.set_page_config(
    page_title="Wekeza Branch Overview",
    page_icon="🏦",
    layout="wide"
)

# -----------------------------
# Backend API URL
# -----------------------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# -----------------------------
# Sidebar: Manager Auth
# -----------------------------
st.sidebar.title("🏦 Branch Management")
st.sidebar.info("Authorized Manager Access")

manager_id = st.sidebar.text_input("Manager ID", value="MAN-001")
branch_code = st.sidebar.text_input("Branch Code", value="NBO-HQ")

if not manager_id:
    st.warning("Please enter Manager ID")
    st.stop()

# -----------------------------
# Fetch Manager Session Info
# -----------------------------
manager = get_branch_manager_info(manager_id, branch_code)
st.title("🏦 Branch Overview Dashboard")
st.markdown(f"**Manager:** {manager['name']} | **Branch:** {branch_code}")
st.markdown("---")

# -----------------------------
# Streamlit Tabs for Branch Overview
# -----------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "💰 Cash Position",
    "📊 Branch Performance",
    "📑 Reports",
    "👥 Staff Management",
    "✅ End-of-Day Approval",
    "🛠️ Manager Overrides"
])

# -----------------------------
# TAB 1: Branch Cash Position
# -----------------------------
with tab1:
    st.subheader("Branch Cash Position")
    render_branch_cash_position_ui(manager, API_URL)

# -----------------------------
# TAB 2: Branch Performance
# -----------------------------
with tab2:
    st.subheader("Branch Performance and KPIs")
    render_branch_performance_ui(manager, API_URL)

# -----------------------------
# TAB 3: Reports
# -----------------------------
with tab3:
    st.subheader("Branch Reports")
    render_reporting_ui(manager, API_URL)

# -----------------------------
# TAB 4: Staff Management
# -----------------------------
with tab4:
    st.subheader("Staff Management")
    render_staff_management_ui(manager, API_URL)

# -----------------------------
# TAB 5: End-of-Day Approval
# -----------------------------
with tab5:
    st.subheader("End-of-Day Approval")
    render_eod_approval_ui(manager, API_URL)

# -----------------------------
# TAB 6: Manager Overrides
# -----------------------------
with tab6:
    st.subheader("Manager Overrides")
    render_overrides_ui(manager, API_URL)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.markdown("Wekeza Bank DFS System | Branch Management Module | 2026")
