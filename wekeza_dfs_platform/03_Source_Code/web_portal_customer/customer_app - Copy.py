import streamlit as st
import requests
import time
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Wekeza Mobile Web", layout="centered")
#API_URL = "http://127.0.0.1:8000"

# If running in Docker, use 'http://backend:8000', else 'http://127.0.0.1:8000'
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- LOGIN SIMULATION ---
if 'user_id' not in st.session_state:
    st.session_state['user_id'] = None

#def login():
#    st.title("🔐 Wekeza Login")
#    user_id = st.number_input("Enter your National ID (Simulated as User ID)", min_value=1, step=1)
#    if st.button("Login"):
#        # Call API to check if user exists
#        try:
#            res = requests.get(f"{API_URL}/users/{user_id}")
#            if res.status_code == 200:
#                st.session_state['user_id'] = user_id
#                st.session_state['user_name'] = res.json()['full_name']
#                st.rerun()
#            else:
#                st.error("User not found!")
#        except:
#            st.error("System Offline. Check API.")
            
def login():
    st.title("🔐 Wekeza Login")
    email = st.text_input("Email Address")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        try:
            # Send Form Data (OAuth2 standard)
            payload = {"username": email, "password": password}
            res = requests.post(f"{API_URL}/token", data=payload)
            
            if res.status_code == 200:
                token_data = res.json()
                st.session_state['token'] = token_data['access_token']
                
                # Fetch User Profile using the Token
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                profile_res = requests.get(f"{API_URL}/users/me", headers=headers) # You'll need to add a /users/me endpoint or decode token
                
                # For now, let's just assume login success
                st.session_state['user_id'] = email # Store email or decode ID
                st.success("Login Successful!")
                st.rerun()
            else:
                st.error("Invalid Credentials")
        except Exception as e:
            st.error(f"Error: {e}")

# ... Inside dashboard() ...
# When applying for loan, add headers:
# headers = {"Authorization": f"Bearer {st.session_state['token']}"}
# requests.post(..., headers=headers)             

def dashboard():
    st.image("https://cdn-icons-png.flaticon.com/512/2534/2534204.png", width=80)
    st.title(f"Jambo, {st.session_state['user_name']} 👋")
    
    # ... inside dashboard() ...
tab1, tab2, tab3 = st.tabs(["💰 My Wallet (Save)", "📉 Loans (Borrow)", "💸 Transfers (Move)"])

with tab1:
    st.metric("Current Balance", f"KES {balance}")
    if st.button("Deposit Funds (Simulate)"):
        # Call /accounts/deposit
        pass

with tab2:
    # Call /loans/active
    # If Active Loan exists:
    st.info(f"Active Loan: KES {loan_balance} remaining")
    repay_amt = st.number_input("Amount to Repay")
    if st.button("Repay Now"):
        # Call /loans/repay
        pass
    # If No active loan:
    # Show "Apply for Loan" form

with tab3: # The Insurance Tab
    st.subheader("Wekeza Salama Insurance")
    
    # Display Products
    st.info("Personal Accident Cover - KES 100/month (Cover: KES 100,000)")
    
    if st.button("Buy Personal Accident Cover"):
        # Call API /insurance/buy
        payload = {"product_code": "PA-001"}
        # ... request logic ...
        st.success("Policy POL-X1234 Generated! Download Certificate.")
        
    st.markdown("---")
    st.subheader("My Policies")
    # Fetch from /insurance/my-policies
    st.table(policies_data)

def dashboard():
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2534/2534204.png", width=50)
    st.sidebar.title(f"{st.session_state['user_name']}")
    st.sidebar.write(f"Account Status: **ACTIVE**") # Fetch real status in prod
    
    # --- HEADER METRICS ---
    # Fetch Data
    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    try:
        # Get Balance
        # Assuming you implemented GET /accounts/me
        # ... fetch logic ...
        balance = 50000.00 # Placeholder for demo
    except:
        balance = 0.00

    st.metric(label="Total Savings Balance", value=f"KES {balance:,.2f}", delta="Active")

    # --- BIMS TABS ---
    tab_borrow, tab_insure, tab_move, tab_save, tab_settings = st.tabs([
        "📉 Borrow (Loans)", 
        "🛡️ Insure (Cover)", 
        "💸 Move (Transfer)", 
        "💰 Save (Statements)",
        "⚙️ Settings"
    ])

    # --- 1. BORROW TAB ---
    with tab_borrow:
        st.subheader("Personal Loan Management")
        col1, col2 = st.columns(2)
        with col1:
            st.info("Limit: KES 15,000")
            st.write("Status: **No Active Loan**")
        with col2:
            with st.form("loan_apply"):
                amt = st.number_input("Amount", 1000, 15000)
                st.form_submit_button("Apply Now")
        
        st.divider()
        st.write("Active Loan Details:")
        st.dataframe(pd.DataFrame({"Principal": [0], "Interest": [0], "Balance": [0]})) # Placeholder

    # --- 2. INSURE TAB ---
    with tab_insure:
        st.subheader("My Insurance Policies")
        st.success("Wekeza Salama: You are NOT covered.")
        if st.button("Activate Personal Accident (KES 100/mo)"):
             # Call /insurance/buy
             st.toast("Policy Activated!")

    # --- 3. MOVE TAB ---
    with tab_move:
        st.subheader("Internal Transfers")
        target_acc = st.text_input("Beneficiary Account Number")
        amount_move = st.number_input("Amount to Transfer", min_value=100)
        if st.button("Send Money"):
            # Call /transfers/internal
            st.success("Money Sent!")

    # --- 4. SAVE (STATEMENTS) TAB ---
    with tab_save:
        st.subheader("Account Statements")
        if st.button("Refresh Statement"):
            res = requests.get(f"{API_URL}/accounts/statement", headers=headers)
            if res.status_code == 200:
                df = pd.DataFrame(res.json())
                st.dataframe(df[['created_at', 'txn_type', 'amount', 'description']])
            else:
                st.error("Could not fetch statement")

    # --- 5. SETTINGS (LIFECYCLE) TAB ---
    with tab_settings:
        st.subheader("Account Control")
        st.warning("Danger Zone")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("❄️ Freeze Account"):
                # Call /accounts/status -> FREEZE
                st.info("Account Frozen.")
        with c2:
            if st.button("🚫 Disable Account"):
                # Call /accounts/status -> DISABLE
                st.error("Account Disabled.")
    
    # 1. WALLET CARD
    st.markdown("""
    <div style="padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-bottom: 20px;">
        <h3>💰 Wallet Balance</h3>
        <h1 style="color: green;">KES 0.00</h1>
        <small>Limit: KES 15,000</small>
    </div>
    """, unsafe_allow_html=True)
    
    # 2. APPLY FOR LOAN
    st.subheader("⚡ Get a Quick Loan")
    
    with st.form("loan_form"):
        amount = st.slider("Amount (KES)", 500, 15000, 5000, step=500)
        tenure = st.selectbox("Repayment Period", [7, 14, 30])
        
        submitted = st.form_submit_button("Request Cash Now")
        
        if submitted:
            payload = {
                "user_id": st.session_state['user_id'],
                "amount": amount,
                "tenure_days": tenure
            }
            
            with st.spinner("Analyzing your Credit Score..."):
                time.sleep(1) # Fake loading for effect
                try:
                    res = requests.post(f"{API_URL}/loans/apply", json=payload)
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.balloons()
                        st.success(f"✅ APPROVED! Loan ID: {data['loan_id']}")
                        st.info(f"Please repay KES {data['total_due_amount']} in {tenure} days.")
                    else:
                        st.error(f"❌ REJECTED: {res.json()['detail']}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    # 3. LOGOUT
    if st.button("Log Out"):
        st.session_state['user_id'] = None
        st.rerun()

# --- APP ROUTER ---
if st.session_state['user_id'] is None:
    login()
else:
    dashboard()
    
   