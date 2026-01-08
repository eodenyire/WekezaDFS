import streamlit as st
import os

# -------------------------------
# App & Session Imports
# -------------------------------
from app import initialize_teller_session, get_logged_in_teller

from deposit import render_cash_deposit_ui
from withdrawal import render_cash_withdrawal_ui
from cheque_deposit import render_cheque_deposit_ui
from balance_enquiry import render_balance_enquiry_ui
from statement_view import render_statement_view_ui
from cash_position import render_cash_position_ui
from eod_balance import render_eod_balance_ui

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Wekeza Bank | Teller Terminal",
    page_icon="🏦",
    layout="wide"
)

# -------------------------------
# Environment
# -------------------------------
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# -------------------------------
# Sidebar – Authentication
# -------------------------------
st.sidebar.title("🏦 Wekeza Bank")
st.sidebar.caption("Branch Teller Terminal")

teller_id = st.sidebar.text_input("Teller ID", value="TEL-001")
branch_code = st.sidebar.text_input("Branch Code", value="NBO-HQ")

login_btn = st.sidebar.button("🔐 Login")

if login_btn:
    initialize_teller_session(
        teller_id=teller_id,
        branch_code=branch_code,
        api_url=API_URL
    )

# -------------------------------
# Load Teller Session
# -------------------------------
teller = get_logged_in_teller()

if not teller:
    st.warning("Please login to access teller services.")
    st.stop()

# -------------------------------
# Header
# -------------------------------
st.title("💵 Teller Operations Console")
st.markdown(
    f"""
    **Teller:** `{teller['teller_id']}`  
    **Branch:** `{teller['branch_code']}`  
    **Cash Limit:** KES {teller['cash_limit']:,.2f}
    """
)

st.divider()

# -------------------------------
# Teller Navigation Tabs
# -------------------------------
tabs = st.tabs([
    "💰 Cash Deposit",
    "💸 Cash Withdrawal",
    "🧾 Cheque Deposit",
    "🔍 Balance Enquiry",
    "📄 Statement View",
    "📊 Cash Position",
    "📦 End of Day"
])

# -------------------------------
# TAB 1: CASH DEPOSIT
# -------------------------------
with tabs[0]:
    render_cash_deposit_ui(teller)

# -------------------------------
# TAB 2: CASH WITHDRAWAL
# -------------------------------
with tabs[1]:
    render_cash_withdrawal_ui(teller)

# -------------------------------
# TAB 3: CHEQUE DEPOSIT
# -------------------------------
with tabs[2]:
    render_cheque_deposit_ui(teller)

# -------------------------------
# TAB 4: BALANCE ENQUIRY
# -------------------------------
with tabs[3]:
    render_balance_enquiry_ui(teller)

# -------------------------------
# TAB 5: STATEMENT VIEW
# -------------------------------
with tabs[4]:
    render_statement_view_ui(teller)

# -------------------------------
# TAB 6: CASH POSITION
# -------------------------------
with tabs[5]:
    render_cash_position_ui(teller)

# -------------------------------
# TAB 7: END OF DAY
# -------------------------------
with tabs[6]:
    render_eod_balance_ui(teller)

# -------------------------------
# Footer
# -------------------------------
st.divider()
st.caption(
    "Wekeza Bank Core Banking System | Teller Module | "
    "All actions are logged and subject to audit."
)
