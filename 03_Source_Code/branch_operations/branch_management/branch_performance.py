# branch_management/branch_performance.py
import streamlit as st
import pandas as pd
from services.api_client import get_request
from branch_management.common import format_currency, format_date

def render_branch_performance_ui(manager: dict, api_url: str):
    """
    Render branch performance dashboard, KPIs, transactions, and teller stats.

    Args:
        manager (dict): Manager session info (manager_id, name, branch_code, role)
        api_url (str): Base URL of backend API
    """
    st.info("View branch KPIs, transaction volumes, and teller performance metrics.")

    # --- Fetch KPIs from backend ---
    try:
        response = get_request(f"{api_url}/branch/performance", params={"branch_code": manager["branch_code"]})
        if response.status_code != 200:
            st.error(f"Error fetching branch performance data: {response.json().get('detail', 'Unknown error')}")
            return

        data = response.json()
    except Exception as e:
        st.error(f"System Error: Could not fetch performance data. {e}")
        return

    # --- Display KPIs ---
    st.subheader("📊 Key Performance Indicators (KPIs)")
    st.markdown(f"- Total Transactions Today: {data.get('total_transactions', 0)}")
    st.markdown(f"- Total Deposit Amount: KES {format_currency(data.get('total_deposits', 0))}")
    st.markdown(f"- Total Withdrawal Amount: KES {format_currency(data.get('total_withdrawals', 0))}")
    st.markdown(f"- Total Cheques Processed: {data.get('total_cheques', 0)}")

    # --- Teller Performance ---
    st.subheader("👥 Teller Performance")
    tellers = data.get("teller_performance", [])
    if tellers:
        df_tellers = pd.DataFrame(tellers)
        # Formatting
        df_tellers["Total Transactions"] = df_tellers["transactions"]
        df_tellers["Total Amount"] = df_tellers["amount"].apply(format_currency)
        df_tellers = df_tellers[["teller_id", "Total Transactions", "Total Amount"]]
        st.table(df_tellers)
    else:
        st.info("No teller performance data available.")

    # --- Transaction Trends ---
    st.subheader("📈 Transaction Trends (Last 7 Days)")
    trends = data.get("transaction_trends", [])
    if trends:
        df_trends = pd.DataFrame(trends)
        df_trends["date"] = df_trends["date"].apply(format_date)
        st.line_chart(df_trends.set_index("date")[["deposits", "withdrawals"]])
    else:
        st.info("No transaction trends data available.")
