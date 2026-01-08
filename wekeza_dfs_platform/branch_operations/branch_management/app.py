# branch_management/app.py
import streamlit as st
import os
from branch_management.common import get_branch_manager_info
from branch_management.branch_overview import render_branch_overview_ui
from branch_management.staff_management import render_staff_management_ui
from branch_management.reporting import render_reporting_ui

# Configure Streamlit page
st.set_page_config(
    page_title="Wekeza Branch Management",
    page_icon="🏢",
    layout="wide"
)

# Backend API URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- SIDEBAR: MANAGER AUTH ---
st.sidebar.title("🏢 Branch Manager Portal")
st.sidebar.info("Authorized Manager Access")

manager_id = st.sidebar.text_input("Manager ID", value="MGR-001")
branch_code = st.sidebar.text_input("Branch Code", value="NBO-HQ")

if not manager_id:
    st.warning("Please enter Manager ID")
    st.stop()

# Fetch branch manager session info
manager = get_branch_manager_info(manager_id, branch_code)

st.title("🏢 Branch Management Terminal")
st.markdown(f"**Manager:** {manager['name']} | **Branch:** {branch_code}")
st.markdown("---")

# --- TABS for Branch Manager Functions ---
tab1, tab2, tab3 = st.tabs([
    "📊 Branch Overview",
    "👥 Staff Management",
    "📝 Reporting"
])

# TAB 1: Branch Overview
with tab1:
    st.subheader("Branch Performance & KPIs")
    render_branch_overview_ui(manager, API_URL)

# TAB 2: Staff Management
with tab2:
    st.subheader("Manage Branch Staff")
    render_staff_management_ui(manager, API_URL)

# TAB 3: Reporting
with tab3:
    st.subheader("Branch Reports & Analytics")
    render_reporting_ui(manager, API_URL)

# --- FOOTER ---
st.markdown("---")
st.markdown("Wekeza Bank DFS System | Branch Management Module | 2026")
