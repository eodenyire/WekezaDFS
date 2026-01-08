import streamlit as st
import requests

st.set_page_config(page_title="Wekeza Branch Ops", layout="wide")
API_URL = "http://backend:8000"

st.sidebar.title("🏦 Wekeza Branch")
st.sidebar.info("Authorized Teller Access Only")
teller_id = st.sidebar.text_input("Teller ID", "TEL-001")

st.title("Cash Deposit Terminal")

col1, col2 = st.columns(2)
with col1:
    nid = st.text_input("Customer National ID")
with col2:
    amt = st.number_input("Deposit Amount (KES)", min_value=50.0)

if st.button("Process Deposit"):
    if not nid: st.error("Enter National ID")
    else:
        try:
            res = requests.post(f"{API_URL}/branch/deposit", params={"national_id": nid, "amount": amt, "teller_id": teller_id})
            if res.status_code == 200:
                data = res.json()
                st.success(f"✅ Deposit of KES {amt} successful!")
                st.info(f"Customer Name: {data['customer']}")
                st.info(f"New Balance: KES {data['new_balance']}")
            else:
                st.error(f"Failed: {res.json()['detail']}")
        except:
            st.error("System Connection Error")