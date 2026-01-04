# bancassurance/reports.py

import streamlit as st
import pandas as pd
from bancassurance.common import format_currency
from bancassurance.services.api_client import get_request
from bancassurance.services.permissions import can_view_reports

# --- REPORTS UI ---
def render_reports_ui(officer):
    """
    Render the Reports tab UI for Bancassurance Officers.

    Args:
        officer (dict): Officer session information (officer_id, name, role, branch_code)
    """

    st.info("Generate and view reports for policy sales, premium collections, and claims")

    if not can_view_reports(officer["role"]):
        st.warning("Access Denied: Insufficient permissions to view reports")
        return

    # --- Report Selection ---
    report_type = st.selectbox(
        "Select Report Type",
        ["Policy Sales", "Premium Collections", "Claims"]
    )

    # --- Filters ---
    st.subheader("Filters")
    date_from = st.date_input("From Date")
    date_to = st.date_input("To Date")

    # Optionally filter by customer or policy
    customer_id = st.text_input("Filter by Customer ID (Optional)")
    policy_number = st.text_input("Filter by Policy Number (Optional)")

    # --- Fetch & Display Report ---
    if st.button("Generate Report"):
        st.info("Fetching report from backend...")

        # Prepare query parameters
        params = {
            "branch_code": officer["branch_code"],
            "report_type": report_type.lower().replace(" ", "_"),
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "customer_id": customer_id or None,
            "policy_number": policy_number or None
        }

        try:
            response = get_request("/bancassurance/reports", params=params)

            if response.get("status") != "success" or not response.get("data"):
                st.warning("No records found for the selected criteria.")
                return

            # Convert data to DataFrame for display
            df = pd.DataFrame(response["data"])

            # Format currency columns if present
            for col in df.columns:
                if "amount" in col.lower() or "premium" in col.lower():
                    df[col] = df[col].apply(format_currency)

            st.subheader(f"{report_type} Report")
            st.dataframe(df)

            # Export options
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"{report_type.replace(' ', '_')}_report.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"System Error: Could not fetch report from backend. {e}")
