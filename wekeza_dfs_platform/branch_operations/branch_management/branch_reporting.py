# branch_management/branch_reporting.py
import streamlit as st
import pandas as pd
from services.api_client import get_request
from branch_management.common import format_currency, format_date

def render_reporting_ui(manager: dict, api_url: str):
    """
    Render branch-level reports and analytics for branch managers.

    Args:
        manager (dict): Manager session info (manager_id, name, branch_code, role)
        api_url (str): Base URL of backend API
    """
    st.info("Generate branch reports: daily, weekly, monthly, or custom date range.")

    # --- Select Report Type ---
    report_type = st.selectbox(
        "Select Report Type",
        ["Daily", "Weekly", "Monthly", "Custom Range"]
    )

    start_date = end_date = None
    if report_type == "Custom Range":
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        if start_date > end_date:
            st.error("Start Date cannot be after End Date")
            return

    # --- Fetch report from backend ---
    params = {
        "branch_code": manager["branch_code"],
        "report_type": report_type,
    }
    if start_date and end_date:
        params["start_date"] = start_date.isoformat()
        params["end_date"] = end_date.isoformat()

    try:
        response = get_request(f"{api_url}/branch/reports", params=params)
        if response.status_code != 200:
            st.error(f"Error fetching report: {response.json().get('detail', 'Unknown error')}")
            return

        report_data = response.json().get("report_data", [])
        if not report_data:
            st.warning("No data available for the selected report.")
            return
    except Exception as e:
        st.error(f"System Error: Could not fetch report. {e}")
        return

    # --- Display Report ---
    st.subheader(f"📑 {report_type} Report")
    df = pd.DataFrame(report_data)

    # Format columns if available
    if "amount" in df.columns:
        df["amount"] = df["amount"].apply(format_currency)
    if "date" in df.columns:
        df["date"] = df["date"].apply(format_date)

    st.dataframe(df)

    # --- Export Options ---
    st.markdown("**Export Report**")
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"{manager['branch_code']}_{report_type}_report.csv",
        mime="text/csv"
    )
