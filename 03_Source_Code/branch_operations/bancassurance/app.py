# bancassurance/app.py

import streamlit as st
import os
from bancassurance import policy_sales, premium_collection, claims_tracking, reports
from bancassurance.common import get_bancassurance_officer_info, check_permissions

def render_bancassurance_ui(staff_info):
    """
    Main render function for the bancassurance module.
    This function is called by the main branch system.
    
    Args:
        staff_info (dict): Staff information from the main system
    """
    # Configure Streamlit page
    st.set_page_config(
        page_title="Wekeza Bancassurance Portal",
        page_icon="🛡️",
        layout="wide"
    )

    # --- SIDEBAR: OFFICER AUTH ---
    st.sidebar.title("🛡️ Bancassurance Portal")
    st.sidebar.info("Authorized System Access Only")

    # Use staff info from main system
    officer_id = staff_info.get('staff_code', 'BA-001')
    branch_code = staff_info.get('branch_code', 'NBO-HQ')
    
    # Create officer info compatible with bancassurance system
    officer = {
        "officer_id": officer_id,
        "name": staff_info.get('full_name', f"Officer {officer_id}"),
        "role": staff_info.get('role', 'bancassurance_officer'),
        "branch_code": branch_code
    }

    st.title("🛡️ Bancassurance Operations Portal")
    st.markdown(f"**Officer:** {officer['name']} | **Branch:** {branch_code}")
    st.markdown("---")

    # --- MAIN TABS ---
    tab_policy, tab_premium, tab_claims, tab_reports = st.tabs([
        "📄 Policy Sales",
        "💰 Premium Collection", 
        "📊 Claims Tracking",
        "📑 Reports"
    ])

    # TAB 1: POLICY SALES
    with tab_policy:
        if not check_permissions(officer["role"], "policy_sales"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Policy Sales")
            policy_sales.render_policy_sales_ui(officer)

    # TAB 2: PREMIUM COLLECTION
    with tab_premium:
        if not check_permissions(officer["role"], "premium_collection"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Premium Collection")
            premium_collection.render_premium_collection_ui(officer)

    # TAB 3: CLAIMS TRACKING
    with tab_claims:
        if not check_permissions(officer["role"], "claims_tracking"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Claims Tracking")
            claims_tracking.render_claims_tracking_ui(officer)

    # TAB 4: REPORTS
    with tab_reports:
        if not check_permissions(officer["role"], "reports"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Reports")
            reports.render_reports_ui(officer)


# Legacy function for standalone usage
def main():
    """
    Legacy main function for standalone usage.
    """
    # --- SIDEBAR: OFFICER AUTH ---
    st.sidebar.title("🛡️ Bancassurance Portal")
    st.sidebar.info("Authorized System Access Only")

    officer_id = st.sidebar.text_input("Officer ID", value="BA-001")
    branch_code = st.sidebar.text_input("Branch Code", value="NBO-HQ")

    if not officer_id:
        st.warning("Please enter Officer ID")
        st.stop()

    # Retrieve officer session info
    officer = get_bancassurance_officer_info(officer_id, branch_code)

    st.title("🛡️ Bancassurance Operations Portal")
    st.markdown(f"**Officer:** {officer['name']} | **Branch:** {branch_code}")
    st.markdown("---")

    # --- MAIN TABS ---
    tab_policy, tab_premium, tab_claims, tab_reports = st.tabs([
        "📄 Policy Sales",
        "💰 Premium Collection",
        "📊 Claims Tracking",
        "📑 Reports"
    ])

    # TAB 1: POLICY SALES
    with tab_policy:
        if not check_permissions(officer["role"], "policy_sales"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Policy Sales")
            policy_sales.render_policy_sales_ui(officer)

    # TAB 2: PREMIUM COLLECTION
    with tab_premium:
        if not check_permissions(officer["role"], "premium_collection"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Premium Collection")
            premium_collection.render_premium_collection_ui(officer)

    # TAB 3: CLAIMS TRACKING
    with tab_claims:
        if not check_permissions(officer["role"], "claims_tracking"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Claims Tracking")
            claims_tracking.render_claims_tracking_ui(officer)

    # TAB 4: REPORTS
    with tab_reports:
        if not check_permissions(officer["role"], "reports"):
            st.warning("Access Denied: Insufficient permissions")
        else:
            st.subheader("Reports")
            reports.render_reports_ui(officer)


if __name__ == "__main__":
    main()
