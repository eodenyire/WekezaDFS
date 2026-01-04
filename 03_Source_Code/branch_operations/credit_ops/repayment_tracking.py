import streamlit as st
from datetime import datetime

from .common import format_currency
from .services.api_client import get_request
from .services.permissions import can_perform_action

# -----------------------------------------------------------------------------
# UI RENDER FUNCTION
# -----------------------------------------------------------------------------
def render_repayment_tracking_ui(officer: dict):
    """
    Render the Repayment Tracking UI tab.
    """

    st.subheader("📊 Loan Repayment Tracking")

    # --- CHECK PERMISSIONS ---
    if not can_perform_action(officer["role"], "repayment_tracking"):
        st.error("You are not authorized to view repayment tracking")
        st.stop()

    # --- SEARCH LOAN ---
    st.markdown("**Search Loan by Customer ID or Application Ref**")
    search_customer_id = st.text_input("Customer National ID", placeholder="e.g., 12345678")
    search_application_ref = st.text_input("Loan Application Reference", placeholder="e.g., LOAN-REF-001")
    
    if st.button("Search Repayments"):
        if not search_customer_id.strip() and not search_application_ref.strip():
            st.error("Enter Customer ID or Application Reference to search")
            st.stop()

        try:
            with st.spinner("Fetching repayment data..."):
                # Backend API call
                params = {
                    "customer_id": search_customer_id.strip(),
                    "application_ref": search_application_ref.strip()
                }
                response = get_request("/credit/repayments", params)

                if not response or "repayments" not in response or len(response["repayments"]) == 0:
                    st.info("No repayment records found")
                    st.stop()

                # --- DISPLAY REPAYMENT TABLE ---
                st.markdown("**Repayment Schedule & Status**")
                repayments = response["repayments"]
                table_data = []
                total_principal = 0
                total_interest = 0
                total_overdue = 0

                for r in repayments:
                    principal = r.get("principal_due", 0)
                    interest = r.get("interest_due", 0)
                    overdue = r.get("overdue_amount", 0)
                    total_principal += principal
                    total_interest += interest
                    total_overdue += overdue

                    table_data.append({
                        "Due Date": r.get("due_date"),
                        "Principal Due": format_currency(principal),
                        "Interest Due": format_currency(interest),
                        "Overdue": format_currency(overdue),
                        "Paid": format_currency(r.get("paid_amount", 0))
                    })

                st.table(table_data)

                # --- SUMMARY ---
                st.markdown("**Repayment Summary**")
                st.markdown(f"- Total Principal Due: {format_currency(total_principal)}")
                st.markdown(f"- Total Interest Due: {format_currency(total_interest)}")
                st.markdown(f"- Total Overdue: {format_currency(total_overdue)}")

                # --- ALERTS ---
                if total_overdue > 0:
                    st.warning(f"⚠ Customer has overdue loans totaling {format_currency(total_overdue)}")

        except Exception as e:
            st.error(f"Failed to fetch repayment data: {e}")
