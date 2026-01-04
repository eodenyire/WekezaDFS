import streamlit as st
from datetime import datetime
import mysql.connector

def render_credit_ops_ui(staff_info):
    """
    Main render function for the credit operations module.
    This function is called by the main branch system.
    
    Args:
        staff_info (dict): Staff information from the main system
    """
    # -----------------------------------------------------------------------------
    # Check Credit Operations Access
    # -----------------------------------------------------------------------------
    def check_credit_access():
        """Verify user has credit operations access"""
        allowed_roles = ['RELATIONSHIP_MANAGER', 'SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
        
        if staff_info['role'] not in allowed_roles:
            st.error(f"❌ Access Denied: Role '{staff_info['role']}' is not authorized for credit operations.")
            st.stop()
        
        return staff_info

    # Database connection
    def get_db_connection():
        try:
            return mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='wekeza_dfs_db'
            )
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    # Check access first
    staff = check_credit_access()

    st.title("💳 Credit Operations System")
    st.markdown(f"**Officer:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
    st.markdown("---")

    # Add basic credit operations interface
    st.info("Credit Operations module loaded successfully!")
    
    # Credit Operations Tabs
    tab_application, tab_setup, tab_disbursement, tab_tracking, tab_restructuring = st.tabs([
        "📝 Loan Application",
        "⚙️ Loan Setup", 
        "💰 Disbursement",
        "📊 Repayment Tracking",
        "🔄 Restructuring"
    ])

    with tab_application:
        st.subheader("Loan Application")
        st.write("Loan application functionality will be implemented here.")
    
    with tab_setup:
        st.subheader("Loan Setup")
        st.write("Loan setup functionality will be implemented here.")
    
    with tab_disbursement:
        st.subheader("Disbursement")
        st.write("Disbursement functionality will be implemented here.")
    
    with tab_tracking:
        st.subheader("Repayment Tracking")
        st.write("Repayment tracking functionality will be implemented here.")
    
    with tab_restructuring:
        st.subheader("Restructuring")
        st.write("Restructuring functionality will be implemented here.")


# Legacy function for standalone usage
def main():
    """
    Legacy main function for standalone usage.
    """
    # -----------------------------------------------------------------------------
    # Get Current Staff from Main System
    # -----------------------------------------------------------------------------
    def get_current_staff():
        """Get the currently logged-in staff from main system session"""
        if 'current_staff' not in st.session_state:
            st.error("❌ No active staff session. Please login through the main system.")
            st.stop()
        return st.session_state.current_staff

    # -----------------------------------------------------------------------------
    # Check Credit Operations Access
    # -----------------------------------------------------------------------------
    def check_credit_access():
        """Verify user has credit operations access"""
        staff = get_current_staff()
        allowed_roles = ['RELATIONSHIP_MANAGER', 'SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
        
        if staff['role'] not in allowed_roles:
            st.error(f"❌ Access Denied: Role '{staff['role']}' is not authorized for credit operations.")
            st.stop()
        
        return staff

    # Database connection
    def get_db_connection():
        try:
            return mysql.connector.connect(
                host='localhost',
                user='root',
                password='root',
                database='wekeza_dfs_db'
            )
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None

    # Check access first
    staff = check_credit_access()

    st.title("💳 Credit Operations System")
    st.markdown(f"**Officer:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
    st.markdown("---")


if __name__ == "__main__":
    main()
