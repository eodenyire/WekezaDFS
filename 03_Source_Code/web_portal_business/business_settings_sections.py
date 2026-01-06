import streamlit as st
import pandas as pd
from datetime import datetime

def render_settings_section(user_data):
    """Render the business settings section"""
    st.subheader("⚙️ Business Settings & Administration")
    
    # Settings tabs
    settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs([
        "🏢 Business Profile", "👥 User Management", "🔒 Security Settings", "🔔 Notifications"
    ])
    
    with settings_tab1:
        render_business_profile_section(user_data)
    
    with settings_tab2:
        render_user_management_section(user_data)
    
    with settings_tab3:
        render_business_security_section(user_data)
    
    with settings_tab4:
        render_business_notifications_section(user_data)

def render_business_profile_section(user_data):
    """Render business profile section"""
    st.markdown("### 🏢 Business Profile Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Business Information")
        
        with st.form("business_profile_form"):
            business_name = st.text_input("Business Name", value="Sample Business Ltd")
            registration_no = st.text_input("Registration Number", value="PVT-123456", disabled=True)
            kra_pin = st.text_input("KRA PIN", value="P051234567A")
            
            sector = st.selectbox("Business Sector", [
                "Technology", "Agriculture", "Retail", "Manufacturing", "Services"
            ])
            
            business_description = st.text_area("Business Description")
            
            if st.form_submit_button("💾 Update Business Profile"):
                st.success("✅ Business profile updated successfully!")
    
    with col2:
        st.markdown("#### Director Information")
        
        with st.form("director_profile_form"):
            director_name = st.text_input("Director Name", value=user_data['full_name'])
            director_email = st.text_input("Director Email", value=user_data['email'])
            director_phone = st.text_input("Director Phone", value="+254 700 123 456")
            
            if st.form_submit_button("💾 Update Director Profile"):
                st.success("✅ Director profile updated successfully!")

def render_user_management_section(user_data):
    """Render user management section"""
    st.markdown("### 👥 Business User Management")
    
    # Current users
    business_users = [
        {
            "name": user_data['full_name'],
            "email": user_data['email'],
            "role": "Managing Director",
            "status": "Active"
        }
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Current Business Users")
        
        for user in business_users:
            status_color = "🟢" if user['status'] == 'Active' else "🔴"
            
            with st.expander(f"{status_color} {user['name']} - {user['role']}"):
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Role:** {user['role']}")
                st.write(f"**Status:** {user['status']}")
    
    with col2:
        st.markdown("#### Add New Business User")
        
        with st.form("add_business_user"):
            new_user_name = st.text_input("Full Name")
            new_user_email = st.text_input("Email Address")
            
            user_role = st.selectbox("User Role", [
                "Finance Manager", "Operations Manager", "Accounts Officer"
            ])
            
            if st.form_submit_button("👥 Add Business User"):
                if new_user_name and new_user_email:
                    st.success("✅ Business user added successfully!")

def render_business_security_section(user_data):
    """Render business security section"""
    st.markdown("### 🔒 Business Security Settings")
    
    with st.form("security_settings"):
        st.markdown("**Access Control**")
        
        require_2fa = st.checkbox("Require Two-Factor Authentication", value=True)
        session_timeout = st.selectbox("Session Timeout", ["30 minutes", "1 hour", "2 hours"])
        
        st.markdown("**Transaction Security**")
        dual_authorization_limit = st.number_input("Dual Authorization Limit (KES)", value=100000.0)
        
        if st.form_submit_button("🔒 Update Security Settings"):
            st.success("✅ Security settings updated!")

def render_business_notifications_section(user_data):
    """Render business notifications section"""
    st.markdown("### 🔔 Business Notification Settings")
    
    with st.form("business_notification_settings"):
        st.markdown("**Email Notifications**")
        email_payments = st.checkbox("Payment Confirmations", value=True)
        email_statements = st.checkbox("Monthly Statements", value=True)
        
        st.markdown("**SMS Notifications**")
        sms_large_payments = st.checkbox("Large Payments (>KES 100,000)", value=True)
        sms_security_alerts = st.checkbox("Security Alerts", value=True)
        
        if st.form_submit_button("🔔 Save Notification Settings"):
            st.success("✅ Notification settings updated!")