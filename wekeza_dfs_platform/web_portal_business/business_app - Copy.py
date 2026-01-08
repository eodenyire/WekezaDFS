import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Wekeza Corporate Banking", layout="wide", page_icon="🏢")
API_URL = "http://backend:8000"

if 'biz_token' not in st.session_state: st.session_state['biz_token'] = None

def business_login():
    st.title("🏢 Wekeza Corporate Banking")
    st.info("Secure Gateway for SMEs & Enterprises")
    
    c1, c2 = st.columns(2)
    with c1:
        email = st.text_input("Director Email")
        password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        # Login logic (Reuse /token endpoint)
        res = requests.post(f"{API_URL}/token", data={"username": email, "password": password})
        if res.status_code == 200:
            st.session_state['biz_token'] = res.json()['access_token']
            st.rerun()
        else:
            st.error("Access Denied")

def corporate_dashboard():
    headers = {"Authorization": f"Bearer {st.session_state['biz_token']}"}
    st.sidebar.title("🏢 My Business")
    st.sidebar.info("Wekeza Hardware Supplies Ltd") # Placeholder
    
    st.title("Corporate Dashboard")
    
    # 1. METRICS
    c1, c2, c3 = st.columns(3)
    c1.metric("Operating Account", "KES 1,250,000.00", "Active")
    c2.metric("Working Capital Loan", "KES 500,000.00", "-15 Days to Due")
    c3.metric("Payroll Status", "Pending Approval")

    # 2. BIMS TABS
    tab_borrow, tab_pay, tab_admin = st.tabs(["📉 SME Loans (Borrow)", "💸 Bulk Pay (Move)", "⚙️ Admin (Save)"])

    with tab_borrow:
        st.subheader("Working Capital Financing")
        st.write("Based on your turnover of **KES 8.5M**, you qualify for:")
        st.info("Limit: KES 1,700,000")
        
        c_a, c_b = st.columns(2)
        with c_a:
            amt = st.number_input("Amount Required", min_value=50000)
            sector = st.selectbox("Sector", ["Retail", "Agriculture", "Tech"])
        with c_b:
            st.write("Term: 3 Months (Fixed)")
            if st.button("Request Financing"):
                # Call /business/loans/apply (We need to add this endpoint)
                st.success("Application Submitted to Credit Committee")

    with tab_pay:
        st.subheader("Bulk Payments (Payroll/Suppliers)")
        st.write("Upload CSV for Salary Processing")
        uploaded_file = st.file_uploader("Choose CSV File")
        if uploaded_file:
            st.success("File Verified: 15 Employees, Total KES 450,000")
            if st.button("Initiate Payment Batch"):
                st.info("Batch #9921 Created. Waiting for Checker Approval.")

    with tab_admin:
        st.subheader("Account Governance")
        st.dataframe(pd.DataFrame({
            "User": ["Director A", "Accountant B"],
            "Role": ["Signatory", "Maker"],
            "Status": ["Active", "Active"]
        }))
        if st.button("Download Monthly Statement"):
            st.toast("Statement PDF Downloading...")

    if st.sidebar.button("Logout"):
        st.session_state['biz_token'] = None
        st.rerun()

if st.session_state['biz_token']:
    corporate_dashboard()
else:
    business_login()