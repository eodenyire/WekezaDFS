import streamlit as st
import requests
import pandas as pd
import os

# Configure the page
st.set_page_config(page_title="Wekeza Branch Teller", page_icon="🏦", layout="wide")

# Connect to Backend (Docker or Local)
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- SIDEBAR: TELLER AUTH ---
st.sidebar.title("🏦 Branch Ops")
st.sidebar.info("Authorized System Access")
teller_id = st.sidebar.text_input("Teller ID", value="TEL-001")
branch_code = st.sidebar.text_input("Branch Code", value="NBO-HQ")

if not teller_id:
    st.warning("Please enter Teller ID")
    st.stop()

# --- MAIN INTERFACE ---
st.title("💵 Cash Transaction Terminal")
st.markdown(f"**Operator:** {teller_id} | **Branch:** {branch_code}")
st.markdown("---")

# TABS for Teller Functions
tab1, tab2 = st.tabs(["📥 Cash Deposit", "🔍 Customer Lookup"])

# TAB 1: CASH DEPOSIT
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Details")
        national_id = st.text_input("National ID Number", placeholder="e.g. 12345678")
        
        # Verify Customer Button
        if st.button("Verify Customer"):
            # In a real app, this would call GET /users?national_id=...
            # For MVP, we proceed to deposit which validates backend
            st.info("Proceed to enter amount.")

    with col2:
        st.subheader("Transaction")
        amount = st.number_input("Cash Amount (KES)", min_value=50.0, step=100.0, format="%.2f")
        remarks = st.text_input("Remarks", value="Cash Deposit")
        
        if st.button("Process Deposit", type="primary"):
            if not national_id or amount <= 0:
                st.error("Invalid Input: Check ID and Amount")
            else:
                with st.spinner("Processing Transaction..."):
                    payload = {
                        "national_id": national_id,
                        "amount": amount,
                        "teller_id": teller_id
                    }
                    try:
                        # Call the Backend API
                        res = requests.post(f"{API_URL}/branch/deposit", params=payload)
                        
                        if res.status_code == 200:
                            data = res.json()
                            st.balloons()
                            st.success("✅ Transaction Successful")
                            
                            # Receipt View
                            st.markdown("### 🧾 Digital Receipt")
                            st.code(f"""
                            Date: 2026-01-01
                            Ref:  {branch_code}-DEP-{amount}
                            Customer: {data['customer']}
                            Amount: KES {amount:,.2f}
                            New Balance: KES {data['new_balance']:,.2f}
                            Teller: {teller_id}
                            """, language="text")
                        else:
                            st.error(f"❌ Transaction Failed: {res.json()['detail']}")
                    except Exception as e:
                        st.error(f"System Error: Could not connect to Core Banking. {e}")

# TAB 2: CUSTOMER LOOKUP (Simple View)
with tab2:
    st.write("Check Account Status (KYC & Balance)")
    lookup_id = st.text_input("Enter National ID for Lookup")
    if st.button("Search"):
        st.warning("Access Restricted: Requires Manager Approval (Simulation)")