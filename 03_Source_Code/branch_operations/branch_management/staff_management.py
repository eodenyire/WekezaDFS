# branch_management/staff_management.py
import streamlit as st
import pandas as pd
from services.api_client import get_request, post_request
from branch_management.common import validate_staff_id, format_date

def render_staff_management_ui(manager: dict, api_url: str):
    """
    Render the Staff Management UI for branch managers.

    Args:
        manager (dict): Manager session info (manager_id, name, branch_code, role)
        api_url (str): Base URL of backend API
    """
    st.info("Manage branch staff: add, update, assign roles, and monitor performance.")

    # --- Tabs for Staff Management ---
    tab1, tab2 = st.tabs(["👥 Staff Directory", "➕ Add/Update Staff"])

    # TAB 1: Staff Directory
    with tab1:
        st.subheader("Current Branch Staff")
        try:
            response = get_request(f"{api_url}/branch/staff", params={"branch_code": manager["branch_code"]})
            if response.status_code != 200:
                st.error(f"Error fetching staff: {response.json().get('detail', 'Unknown error')}")
                return

            staff_list = response.json().get("staff", [])
            if not staff_list:
                st.info("No staff registered in this branch.")
                return

            df_staff = pd.DataFrame(staff_list)
            df_staff["date_joined"] = df_staff["date_joined"].apply(format_date)
            st.dataframe(df_staff)

        except Exception as e:
            st.error(f"System Error: Could not fetch staff data. {e}")

    # TAB 2: Add/Update Staff
    with tab2:
        st.subheader("Add or Update Staff Member")

        staff_id = st.text_input("Staff ID", placeholder="e.g. TEL-001")
        name = st.text_input("Full Name")
        role = st.selectbox("Role", ["Teller", "LoanOfficer", "RelationshipOfficer", "CashOfficer"])
        status = st.selectbox("Status", ["Active", "Inactive"])

        if st.button("Submit"):
            # --- Validation ---
            if not staff_id or not name:
                st.error("Staff ID and Name are required.")
                return
            if not validate_staff_id(staff_id):
                st.error("Invalid Staff ID format.")
                return

            payload = {
                "staff_id": staff_id,
                "name": name.strip(),
                "role": role,
                "status": status,
                "branch_code": manager["branch_code"],
                "updated_by": manager["manager_id"]
            }

            try:
                response = post_request(f"{api_url}/branch/staff", payload)
                if response.status_code == 200:
                    st.success(f"✅ Staff {staff_id} successfully added/updated.")
                else:
                    st.error(f"❌ Failed to add/update staff: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"System Error: Could not connect to backend. {e}")
