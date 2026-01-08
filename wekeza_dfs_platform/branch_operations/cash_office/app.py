import streamlit as st
import os

# Import Cash Office module UI functions
from vault_open_close import open_vault_ui, close_vault_ui
from teller_cash_issue import issue_cash_ui
from teller_cash_receive import receive_cash_ui
from atm_cash_loading import load_atm_ui
from atm_cash_offloading import offload_atm_ui
from cash_reconciliation import reconcile_cash_ui
from common import get_cash_officer_info

# Configure Streamlit page
st.set_page_config(
    page_title="Wekeza Branch Cash Office",
    page_icon="💰",
    layout="wide"
)

# --- SIDEBAR: Cash Officer Authentication ---
st.sidebar.title("💵 Branch Cash Office")
st.sidebar.info("Authorized System Access Only")

# Inputs for officer credentials
officer_id = st.sidebar.text_input("Officer ID", value="COF-001")
branch_code = st.sidebar.text_input("Branch Code", value="NBO-HQ")

# Validate login
if not officer_id or not branch_code:
    st.warning("Please enter Officer ID and Branch Code to continue.")
    st.stop()

# Store logged-in officer info
officer_info = get_cash_officer_info(officer_id, branch_code)

st.title("💰 Branch Cash Office Terminal")
st.markdown(f"**Operator:** {officer_info['officer_id']} | **Branch:** {officer_info['branch_code']}")
st.markdown("---")

# --- TABS for Cash Office Operations ---
tab_vault, tab_issue, tab_receive, tab_atm_load, tab_atm_offload, tab_reconcile = st.tabs([
    "🏦 Vault Open/Close",
    "💵 Teller Cash Issue",
    "💳 Teller Cash Receive",
    "🏧 ATM Cash Loading",
    "🏧 ATM Cash Offloading",
    "📊 Cash Reconciliation"
])

# --- Vault Management ---
with tab_vault:
    st.subheader("Vault Management")
    st.info("Open or Close Vault, record opening/closing balances, and track denominations.")
    open_vault_ui(officer_info)
    close_vault_ui(officer_info)

# --- Teller Cash Issue ---
with tab_issue:
    st.subheader("Issue Cash to Tellers")
    st.info("Issue cash to tellers while respecting teller limits and branch vault availability.")
    issue_cash_ui(officer_info)

# --- Teller Cash Receive ---
with tab_receive:
    st.subheader("Receive Cash from Tellers")
    st.info("Receive cash from tellers at end-of-day or mid-day deposits.")
    receive_cash_ui(officer_info)

# --- ATM Cash Loading ---
with tab_atm_load:
    st.subheader("ATM Cash Loading")
    st.info("Load ATMs with cash while ensuring denomination correctness and ATM limits.")
    load_atm_ui(officer_info)

# --- ATM Cash Offloading ---
with tab_atm_offload:
    st.subheader("ATM Cash Offloading")
    st.info("Offload cash from ATMs back to the vault and update balances.")
    offload_atm_ui(officer_info)

# --- Cash Reconciliation ---
with tab_reconcile:
    st.subheader("Cash Reconciliation")
    st.info("Reconcile vault, teller, and ATM cash balances at end-of-day for auditing.")
    reconcile_cash_ui(officer_info)
