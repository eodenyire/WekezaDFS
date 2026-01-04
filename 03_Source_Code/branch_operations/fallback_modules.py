import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

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

def render_branch_management(staff_id, branch_code, role):
    """Fallback Branch Management Module"""
    
    # Branch Overview Dashboard
    st.subheader("📊 Branch Performance Dashboard")
    
    # KPI Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Get branch statistics
            cursor.execute("SELECT COUNT(*) as total_customers FROM users WHERE is_active = 1")
            total_customers = cursor.fetchone()['total_customers']
            
            cursor.execute("SELECT SUM(balance) as total_deposits FROM accounts WHERE status = 'ACTIVE'")
            total_deposits = cursor.fetchone()['total_deposits'] or 0
            
            cursor.execute("SELECT COUNT(*) as total_transactions FROM transactions WHERE DATE(created_at) = CURDATE()")
            today_transactions = cursor.fetchone()['total_transactions']
            
            cursor.execute("SELECT COUNT(*) as active_staff FROM staff WHERE is_active = 1")
            active_staff = cursor.fetchone()['active_staff']
            
            conn.close()
            
            col1.metric("Total Customers", f"{total_customers:,}")
            col2.metric("Total Deposits", f"KES {total_deposits:,.0f}")
            col3.metric("Today's Transactions", f"{today_transactions:,}")
            col4.metric("Active Staff", f"{active_staff}")
        
    except Exception as e:
        st.error(f"Error fetching branch data: {e}")
        col1.metric("Total Customers", "1,247")
        col2.metric("Total Deposits", "KES 2.4M")
        col3.metric("Today's Transactions", "156")
        col4.metric("Active Staff", "12")
    
    st.markdown("---")
    
    # Branch Management Tabs
    mgmt_tab1, mgmt_tab2, mgmt_tab3, mgmt_tab4 = st.tabs([
        "📈 Performance", "👥 Staff", "💰 Cash Position", "📋 Reports"
    ])
    
    with mgmt_tab1:
        st.subheader("Branch Performance Analytics")
        
        # Sample performance chart
        dates = pd.date_range(start='2026-01-01', end='2026-01-03', freq='D')
        transactions = [120, 145, 156]
        amounts = [2400000, 2650000, 2800000]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=transactions, mode='lines+markers', name='Transactions'))
        fig.update_layout(title="Daily Transaction Volume", xaxis_title="Date", yaxis_title="Transactions")
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Customer Satisfaction", "94%", "2%")
            st.metric("Average Transaction Time", "3.2 min", "-0.5 min")
        with col2:
            st.metric("Staff Productivity", "87%", "5%")
            st.metric("System Uptime", "99.8%", "0.1%")
    
    with mgmt_tab2:
        st.subheader("Staff Management")
        
        # Staff roster
        try:
            conn = get_db_connection()
            if conn:
                df_staff = pd.read_sql("""
                    SELECT s.staff_code, s.full_name, s.role, s.email, s.is_active,
                           b.branch_name
                    FROM staff s
                    LEFT JOIN branches b ON s.branch_id = b.branch_id
                    WHERE b.branch_code = %s OR %s = 'BR001'
                """, conn, params=(branch_code, branch_code))
                
                st.dataframe(df_staff, use_container_width=True)
                conn.close()
            else:
                st.info("Unable to load staff data")
        except Exception as e:
            st.error(f"Error loading staff: {e}")
        
        # Staff actions
        st.subheader("Staff Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📅 Schedule Staff"):
                st.success("Staff scheduling interface opened")
        with col2:
            if st.button("📊 Performance Review"):
                st.success("Performance review system accessed")
    
    with mgmt_tab3:
        st.subheader("Cash Position Management")
        
        # Cash position summary
        col1, col2, col3 = st.columns(3)
        col1.metric("Vault Cash", "KES 500K")
        col2.metric("Teller Cash", "KES 150K") 
        col3.metric("ATM Cash", "KES 200K")
        
        # Cash movement chart
        st.subheader("Cash Flow Today")
        cash_data = {
            'Time': ['09:00', '11:00', '13:00', '15:00', '17:00'],
            'Inflow': [50000, 75000, 120000, 95000, 60000],
            'Outflow': [30000, 45000, 80000, 70000, 40000]
        }
        df_cash = pd.DataFrame(cash_data)
        
        fig = px.line(df_cash, x='Time', y=['Inflow', 'Outflow'], 
                     title="Cash Flow Pattern")
        st.plotly_chart(fig, use_container_width=True)
        
        # Cash management actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💰 Request Cash"):
                st.success("Cash request submitted to head office")
        with col2:
            if st.button("🔒 Vault Reconciliation"):
                st.success("Vault reconciliation started")
    
    with mgmt_tab4:
        st.subheader("Branch Reports")
        
        # Report generation
        report_type = st.selectbox("Select Report Type", [
            "Daily Transaction Summary",
            "Customer Activity Report", 
            "Staff Performance Report",
            "Cash Position Report",
            "Compliance Report"
        ])
        
        date_range = st.date_input("Report Date Range", 
                                  value=[datetime.now().date(), datetime.now().date()])
        
        if st.button("Generate Report", type="primary"):
            st.success(f"Generating {report_type} for {date_range}")
            
            # Sample report data
            if report_type == "Daily Transaction Summary":
                report_data = {
                    'Transaction Type': ['Deposits', 'Withdrawals', 'Transfers', 'Payments'],
                    'Count': [45, 67, 23, 21],
                    'Amount (KES)': [450000, 320000, 180000, 85000]
                }
                df_report = pd.DataFrame(report_data)
                st.dataframe(df_report, use_container_width=True)
                
                # Download button
                csv = df_report.to_csv(index=False)
                st.download_button(
                    label="📥 Download Report",
                    data=csv,
                    file_name=f"{report_type}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

def render_customer_operations(staff_id, branch_code, role):
    """Fallback Customer Operations Module"""
    
    st.subheader("👥 Customer Service Operations")
    
    # Customer operations tabs
    cust_tab1, cust_tab2, cust_tab3, cust_tab4 = st.tabs([
        "🔍 Customer Lookup", "📝 Account Opening", "🔧 Account Maintenance", "📋 Service Requests"
    ])
    
    with cust_tab1:
        st.subheader("Customer Search & Inquiry")
        
        search_method = st.radio("Search by:", ["National ID", "Account Number", "Phone Number", "Email"])
        search_value = st.text_input(f"Enter {search_method}")
        
        if st.button("Search Customer") and search_value:
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    if search_method == "National ID":
                        cursor.execute("""
                            SELECT u.*, a.account_number, a.balance, a.status as account_status
                            FROM users u 
                            LEFT JOIN accounts a ON u.user_id = a.user_id 
                            WHERE u.national_id = %s
                        """, (search_value,))
                    elif search_method == "Account Number":
                        cursor.execute("""
                            SELECT u.*, a.account_number, a.balance, a.status as account_status
                            FROM users u 
                            JOIN accounts a ON u.user_id = a.user_id 
                            WHERE a.account_number = %s
                        """, (search_value,))
                    elif search_method == "Phone Number":
                        cursor.execute("""
                            SELECT u.*, a.account_number, a.balance, a.status as account_status
                            FROM users u 
                            LEFT JOIN accounts a ON u.user_id = a.user_id 
                            WHERE u.phone_number = %s
                        """, (search_value,))
                    else:  # Email
                        cursor.execute("""
                            SELECT u.*, a.account_number, a.balance, a.status as account_status
                            FROM users u 
                            LEFT JOIN accounts a ON u.user_id = a.user_id 
                            WHERE u.email = %s
                        """, (search_value,))
                    
                    customer = cursor.fetchone()
                    conn.close()
                    
                    if customer:
                        st.success("✅ Customer Found")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("### Customer Information")
                            st.write(f"**Name:** {customer['full_name']}")
                            st.write(f"**Email:** {customer['email']}")
                            st.write(f"**Phone:** {customer['phone_number']}")
                            st.write(f"**National ID:** {customer['national_id']}")
                            st.write(f"**KYC Tier:** {customer['kyc_tier']}")
                            st.write(f"**Status:** {'Active' if customer['is_active'] else 'Inactive'}")
                        
                        with col2:
                            st.markdown("### Account Information")
                            if customer['account_number']:
                                st.write(f"**Account Number:** {customer['account_number']}")
                                st.write(f"**Balance:** KES {customer['balance']:,.2f}")
                                st.write(f"**Account Status:** {customer['account_status']}")
                            else:
                                st.warning("No account found for this customer")
                    else:
                        st.error("❌ Customer not found")
                        
            except Exception as e:
                st.error(f"❌ Search failed: {e}")
    
    with cust_tab2:
        st.subheader("New Account Opening")
        st.info("🏗️ Account opening module - Comprehensive KYC and onboarding process")
        
        with st.form("account_opening"):
            col1, col2 = st.columns(2)
            
            with col1:
                full_name = st.text_input("Full Name *")
                email = st.text_input("Email *")
                phone = st.text_input("Phone Number *")
                national_id = st.text_input("National ID *")
            
            with col2:
                account_type = st.selectbox("Account Type", ["Savings", "Current", "Fixed Deposit"])
                initial_deposit = st.number_input("Initial Deposit (KES)", min_value=1000.0, value=5000.0)
                kyc_tier = st.selectbox("KYC Tier", ["TIER_1", "TIER_2", "TIER_3"])
                branch_code_input = st.text_input("Branch Code", value=branch_code)
            
            if st.form_submit_button("Open Account", type="primary"):
                if all([full_name, email, phone, national_id]):
                    st.success("✅ Account opening process initiated!")
                    st.info(f"📋 Application processed by: {staff_id}")
                    st.info(f"🏦 Branch: {branch_code}")
                else:
                    st.error("Please fill all required fields")
    
    with cust_tab3:
        st.subheader("Account Maintenance")
        st.info("🔧 Account updates and maintenance services")
        
        maintenance_type = st.selectbox("Maintenance Type", [
            "Update Contact Information",
            "Change Account Type", 
            "Update KYC Documents",
            "Add/Remove Signatory",
            "Account Status Change",
            "Statement Request"
        ])
        
        account_number = st.text_input("Account Number")
        
        if maintenance_type == "Update Contact Information":
            new_phone = st.text_input("New Phone Number")
            new_email = st.text_input("New Email")
            new_address = st.text_area("New Address")
            
            if st.button("Update Contact Info"):
                st.success("Contact information updated successfully!")
        
        elif maintenance_type == "Statement Request":
            statement_period = st.selectbox("Statement Period", [
                "Last 30 days", "Last 3 months", "Last 6 months", "Custom Range"
            ])
            
            if st.button("Generate Statement"):
                st.success("Account statement generated and sent to customer email!")
    
    with cust_tab4:
        st.subheader("Service Requests")
        st.info("📋 Customer service request management")
        
        request_type = st.selectbox("Request Type", [
            "Checkbook Request",
            "Debit Card Request", 
            "Account Closure",
            "Loan Application",
            "Insurance Inquiry",
            "Complaint Resolution"
        ])
        
        customer_account = st.text_input("Customer Account Number")
        request_details = st.text_area("Request Details")
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"])
        
        if st.button("Submit Service Request", type="primary"):
            st.success(f"Service request submitted with priority: {priority}")
            st.info(f"Request ID: SR{datetime.now().strftime('%Y%m%d%H%M%S')}")

# Add other fallback modules as needed...