import streamlit as st
import requests

st.set_page_config(page_title="Wekeza Branch Ops", layout="wide")
API_URL = "http://127.0.0.1:8000"

# Sidebar for Teller Login (Simulated)
st.sidebar.title("🏦 Branch Ops")
teller_id = st.sidebar.text_input("Teller ID", value="TEL-001")

st.title("Branch Cash Deposit Terminal")

# The Deposit Form
with st.container():
    st.markdown("### 📥 Cash Deposit")
    
    col1, col2 = st.columns(2)
    with col1:
        national_id = st.text_input("Customer National ID")
    with col2:
        amount = st.number_input("Amount (Cash)", min_value=100.0, step=100.0)
        
    if st.button("Process Deposit"):
        if national_id and amount > 0:
            payload = {
                "national_id": national_id,
                "amount": amount,
                "teller_id": teller_id
            }
            
            try:
                # Call the specific Branch Endpoint
                res = requests.post(f"{API_URL}/branch/deposit", params=payload)
                
                if res.status_code == 200:
                    data = res.json()
                    st.balloons()
                    st.success(f"✅ Deposit Successful!")
                    st.info(f"Customer: {data['customer']}")
                    st.info(f"New Balance: KES {data['new_balance']:,.2f}")
                else:
                    st.error(f"❌ Failed: {res.json()['detail']}")
            except Exception as e:
                st.error(f"System Error: {e}")
        else:
            st.warning("Please enter details.")

st.divider()
st.markdown("#### recent_transactions_log (Local Session)")
# You could add a local log here for the teller