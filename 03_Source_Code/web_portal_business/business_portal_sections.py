import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import uuid
import json

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

def render_accounts_section(user_data):
    """Render the accounts management section"""
    st.subheader("🏦 Account Management & Cash Operations")
    
    # Account tabs
    acc_tab1, acc_tab2, acc_tab3, acc_tab4 = st.tabs([
        "💰 Account Overview", "📊 Account Statements", "💳 Cash Management", "📈 Account Analytics"
    ])
    
    with acc_tab1:
        render_account_overview_section(user_data)
    
    with acc_tab2:
        render_business_statements_section(user_data)
    
    with acc_tab3:
        render_cash_management_section(user_data)
    
    with acc_tab4:
        render_account_analytics_section(user_data)

def render_account_overview_section(user_data):
    """Render account overview section"""
    st.markdown("### 💰 Business Account Overview")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        business_id = user_data['business_id']
        
        # Get all business accounts
        cursor.execute("""
            SELECT a.*, b.business_name, b.registration_no
            FROM accounts a
            JOIN businesses b ON a.business_id = b.business_id
            WHERE a.business_id = %s
            ORDER BY a.created_at
        """, (business_id,))
        
        accounts = cursor.fetchall()
        
        # Get today's transactions summary
        cursor.execute("""
            SELECT 
                COUNT(*) as txn_count,
                SUM(CASE WHEN txn_type LIKE '%IN%' OR txn_type = 'DEPOSIT' THEN amount ELSE 0 END) as credits,
                SUM(CASE WHEN txn_type LIKE '%OUT%' OR txn_type LIKE '%PAYMENT%' OR txn_type LIKE '%TRANSFER%' THEN amount ELSE 0 END) as debits
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.business_id = %s AND DATE(t.created_at) = CURDATE()
        """, (business_id,))
        
        today_summary = cursor.fetchone()
        
        conn.close()
        
        if accounts:
            # Business summary metrics
            total_balance = sum(acc['balance'] for acc in accounts)
            active_accounts = len([acc for acc in accounts if acc['status'] == 'ACTIVE'])
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Balance", f"KES {total_balance:,.2f}")
            col2.metric("Active Accounts", active_accounts)
            col3.metric("Today's Transactions", today_summary['txn_count'] or 0)
            col4.metric("Net Flow Today", f"KES {(today_summary['credits'] or 0) - (today_summary['debits'] or 0):,.2f}")
            
            st.markdown("---")
            
            # Account details
            for account in accounts:
                account_type = "Operating Account" if account == accounts[0] else f"Account {account['account_id']}"
                
                with st.expander(f"🏦 {account_type} - {account['account_number']} ({account['status']})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Current Balance", f"KES {account['balance']:,.2f}")
                        st.write(f"**Currency:** {account['currency']}")
                        st.write(f"**Status:** {account['status']}")
                    
                    with col2:
                        st.write(f"**Account Number:** {account['account_number']}")
                        st.write(f"**Opened:** {account['created_at'].strftime('%Y-%m-%d')}")
                        st.write(f"**Business:** {account['business_name']}")
                    
                    with col3:
                        # Quick actions
                        if st.button(f"📧 Email Statement", key=f"email_{account['account_id']}"):
                            st.success("Statement sent to registered email!")
                        
                        if st.button(f"📱 SMS Balance", key=f"sms_{account['account_id']}"):
                            st.success("Balance sent via SMS!")
                        
                        if st.button(f"🔄 Refresh", key=f"refresh_{account['account_id']}"):
                            st.rerun()
        else:
            st.error("No business accounts found")
            
    except Exception as e:
        st.error(f"Error loading account information: {e}")

def render_business_statements_section(user_data):
    """Render business statements section"""
    st.markdown("### 📊 Business Account Statements")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Generate Business Statement")
        
        # Statement options for businesses
        statement_type = st.selectbox("Statement Type", [
            "Account Statement", "Transaction Summary", "Cash Flow Statement",
            "Regulatory Report", "Tax Statement", "Audit Trail"
        ])
        
        statement_period = st.selectbox("Period", [
            "Last 7 days", "Last 30 days", "Last 3 months", 
            "Last 6 months", "Last 12 months", "Custom Range", "Financial Year"
        ])
        
        if statement_period == "Custom Range":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        elif statement_period == "Financial Year":
            fy_year = st.selectbox("Financial Year", ["2025-2026", "2024-2025", "2023-2024"])
        
        statement_format = st.selectbox("Format", ["PDF", "Excel", "CSV", "XML (for accounting software)"])
        
        # Business-specific options
        include_details = st.checkbox("Include transaction details", value=True)
        include_attachments = st.checkbox("Include supporting documents")
        
        if st.button("📊 Generate Business Statement", type="primary"):
            generate_business_statement(user_data, statement_type, statement_period, statement_format)
    
    with col2:
        st.markdown("#### Recent Business Transactions")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT t.*, a.account_number
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.business_id = %s
                ORDER BY t.created_at DESC
                LIMIT 15
            """, (user_data['business_id'],))
            
            recent_txns = cursor.fetchall()
            conn.close()
            
            if recent_txns:
                for txn in recent_txns:
                    # Business transaction display
                    if 'IN' in txn['txn_type'] or txn['txn_type'] == 'DEPOSIT':
                        icon = "📥"
                        color = "success"
                    else:
                        icon = "📤"
                        color = "info"
                    
                    st.write(f"{icon} **{txn['txn_type'].replace('_', ' ').title()}**")
                    st.write(f"KES {txn['amount']:,.2f} - {txn['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"Ref: {txn['reference_code']}")
                    if txn.get('description'):
                        st.write(f"Note: {txn['description']}")
                    st.markdown("---")
            else:
                st.info("No recent transactions")
                
        except Exception as e:
            st.error(f"Error loading transactions: {e}")

def generate_business_statement(user_data, statement_type, period, format_type):
    """Generate business statement"""
    try:
        st.success(f"✅ {statement_type} ({format_type}) generated successfully!")
        st.info(f"📧 Business statement for {period} will be sent to registered email within 5 minutes")
        st.info(f"📱 SMS notification sent to all authorized signatories")
        
        # Create downloadable content
        statement_content = f"""
WEKEZA BANK BUSINESS STATEMENT
Business Name: {user_data.get('business_name', 'N/A')}
Statement Type: {statement_type}
Period: {period}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generated By: {user_data['full_name']}

This is a sample business statement. The actual statement will be sent to your registered email.
        """
        
        st.download_button(
            label=f"📥 Download {statement_type}",
            data=statement_content,
            file_name=f"business_statement_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Statement generation failed: {e}")

def render_cash_management_section(user_data):
    """Render cash management section"""
    st.markdown("### 💳 Business Cash Management")
    
    cash_tab1, cash_tab2, cash_tab3 = st.tabs([
        "💰 Cash Deposits", "💸 Cash Withdrawals", "📊 Cash Limits & Controls"
    ])
    
    with cash_tab1:
        st.markdown("#### 💰 Business Cash Deposits")
        
        with st.form("business_cash_deposit"):
            col1, col2 = st.columns(2)
            
            with col1:
                deposit_amount = st.number_input("Deposit Amount (KES)", min_value=100.0, step=100.0)
                deposit_source = st.selectbox("Deposit Source", [
                    "Daily Sales Collection", "Customer Payments", "Cash Sales",
                    "Petty Cash Surplus", "Branch Collection", "Other Business Income"
                ])
                deposit_branch = st.selectbox("Deposit Branch", [
                    "Head Office", "Westlands Branch", "CBD Branch", "Eastleigh Branch"
                ])
            
            with col2:
                deposit_reference = st.text_input("Reference/Invoice Number")
                deposit_notes = st.text_area("Additional Notes")
                depositor_name = st.text_input("Depositor Name", value=user_data['full_name'])
            
            st.info("💡 **Business Cash Deposit Information**")
            st.write("• Large cash deposits (>KES 100,000) require 24-hour notice")
            st.write("• All deposits are subject to source verification")
            st.write("• Funds available immediately after verification")
            
            if st.form_submit_button("💰 Schedule Cash Deposit", type="primary"):
                if deposit_amount > 0:
                    schedule_business_cash_deposit(user_data, deposit_amount, deposit_source, deposit_reference)

    with cash_tab2:
        st.markdown("#### 💸 Business Cash Withdrawals")
        
        with st.form("business_cash_withdrawal"):
            col1, col2 = st.columns(2)
            
            with col1:
                withdrawal_amount = st.number_input("Withdrawal Amount (KES)", min_value=100.0, step=100.0)
                withdrawal_purpose = st.selectbox("Withdrawal Purpose", [
                    "Petty Cash Replenishment", "Supplier Payments", "Staff Salaries",
                    "Operating Expenses", "Emergency Funds", "Business Operations"
                ])
                withdrawal_branch = st.selectbox("Withdrawal Branch", [
                    "Head Office", "Westlands Branch", "CBD Branch", "Eastleigh Branch"
                ])
            
            with col2:
                withdrawal_reference = st.text_input("Reference/Voucher Number")
                withdrawal_notes = st.text_area("Purpose Details")
                withdrawer_name = st.text_input("Authorized Withdrawer", value=user_data['full_name'])
            
            # Business withdrawal limits and approvals
            st.info("💡 **Business Cash Withdrawal Limits**")
            st.write("• Daily limit: KES 500,000 per signatory")
            st.write("• Amounts >KES 100,000 require dual authorization")
            st.write("• Amounts >KES 500,000 require board resolution")
            
            if st.form_submit_button("💸 Request Cash Withdrawal", type="primary"):
                if withdrawal_amount > 0:
                    request_business_cash_withdrawal(user_data, withdrawal_amount, withdrawal_purpose, withdrawal_reference)

    with cash_tab3:
        st.markdown("#### 📊 Cash Limits & Controls")
        
        # Display current limits
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Business Limits**")
            st.write("• Daily Cash Deposit Limit: KES 2,000,000")
            st.write("• Daily Cash Withdrawal Limit: KES 500,000")
            st.write("• Monthly Cash Transaction Limit: KES 10,000,000")
            st.write("• Single Transaction Limit: KES 1,000,000")
            
            st.markdown("**Approval Requirements**")
            st.write("• >KES 100,000: Dual Authorization")
            st.write("• >KES 500,000: Board Resolution")
            st.write("• >KES 1,000,000: Central Bank Notification")
        
        with col2:
            st.markdown("**Request Limit Increase**")
            
            with st.form("limit_increase_request"):
                limit_type = st.selectbox("Limit Type", [
                    "Daily Cash Deposit", "Daily Cash Withdrawal", 
                    "Monthly Transaction", "Single Transaction"
                ])
                
                current_limit = st.number_input("Current Limit (KES)", value=500000.0, disabled=True)
                requested_limit = st.number_input("Requested Limit (KES)", min_value=current_limit)
                business_justification = st.text_area("Business Justification")
                
                if st.form_submit_button("📝 Submit Limit Increase Request"):
                    if requested_limit > current_limit and business_justification:
                        st.success("✅ Limit increase request submitted!")
                        st.info("🔄 Request will be reviewed within 2-3 business days")
                        st.info("📧 You will be notified via email of the decision")

def schedule_business_cash_deposit(user_data, amount, source, reference):
    """Schedule a business cash deposit"""
    try:
        st.success(f"✅ Business cash deposit scheduled successfully!")
        st.info(f"💰 Amount: KES {amount:,.2f}")
        st.info(f"📋 Source: {source}")
        st.info(f"📝 Reference: {reference}")
        st.info("🏦 Visit the selected branch with:")
        st.info("• Valid business registration documents")
        st.info("• Authorized signatory ID")
        st.info("• Cash deposit slip (available at branch)")
        
        if amount > 100000:
            st.warning("⚠️ Large deposit detected - please call ahead to ensure cash handling capacity")
        
    except Exception as e:
        st.error(f"❌ Cash deposit scheduling failed: {e}")

def request_business_cash_withdrawal(user_data, amount, purpose, reference):
    """Request a business cash withdrawal"""
    try:
        # Check if approval is needed
        needs_approval = amount > 100000
        
        st.success(f"✅ Business cash withdrawal request submitted!")
        st.info(f"💸 Amount: KES {amount:,.2f}")
        st.info(f"📋 Purpose: {purpose}")
        st.info(f"📝 Reference: {reference}")
        
        if needs_approval:
            st.warning("⚠️ This withdrawal requires dual authorization")
            st.info("🔄 Request sent to other authorized signatories for approval")
            st.info("📧 You will be notified once approved")
        else:
            st.info("🏦 Visit the selected branch with:")
            st.info("• Valid business registration documents")
            st.info("• Authorized signatory ID")
            st.info("• Withdrawal voucher (pre-filled)")
        
    except Exception as e:
        st.error(f"❌ Cash withdrawal request failed: {e}")

def render_account_analytics_section(user_data):
    """Render account analytics section"""
    st.markdown("### 📈 Business Account Analytics")
    
    # Mock analytics data
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Cash Flow Trends (Last 6 Months)")
        
        # Sample data for demonstration
        months = ['Aug 2025', 'Sep 2025', 'Oct 2025', 'Nov 2025', 'Dec 2025', 'Jan 2026']
        inflows = [450000, 520000, 480000, 610000, 580000, 650000]
        outflows = [380000, 420000, 450000, 480000, 520000, 580000]
        
        df = pd.DataFrame({
            'Month': months,
            'Cash Inflows': inflows,
            'Cash Outflows': outflows,
            'Net Flow': [i - o for i, o in zip(inflows, outflows)]
        })
        
        st.line_chart(df.set_index('Month')[['Cash Inflows', 'Cash Outflows']])
        
        # Key metrics
        avg_inflow = sum(inflows) / len(inflows)
        avg_outflow = sum(outflows) / len(outflows)
        
        st.metric("Average Monthly Inflow", f"KES {avg_inflow:,.2f}")
        st.metric("Average Monthly Outflow", f"KES {avg_outflow:,.2f}")
        st.metric("Average Net Flow", f"KES {avg_inflow - avg_outflow:,.2f}")
    
    with col2:
        st.markdown("#### Transaction Analysis")
        
        # Transaction type breakdown
        txn_types = ['Deposits', 'Transfers Out', 'Loan Payments', 'Insurance', 'Fees']
        txn_amounts = [45, 25, 15, 10, 5]
        
        df_txn = pd.DataFrame({
            'Transaction Type': txn_types,
            'Percentage': txn_amounts
        })
        
        st.bar_chart(df_txn.set_index('Transaction Type'))
        
        # Business insights
        st.markdown("#### Business Insights")
        st.success("📈 Cash flow is trending upward")
        st.info("💡 Consider fixed deposit for excess cash")
        st.warning("⚠️ High outflow in December - seasonal pattern?")

def render_payments_section(user_data):
    """Render the payments and transfers section"""
    st.subheader("💸 Payments & Transfers")
    
    # Payment tabs
    pay_tab1, pay_tab2, pay_tab3, pay_tab4, pay_tab5 = st.tabs([
        "💳 Single Payments", "📊 Bulk Payments", "🔄 Standing Orders", "📋 Payment History", "⚙️ Payment Settings"
    ])
    
    with pay_tab1:
        render_single_payments_section(user_data)
    
    with pay_tab2:
        render_bulk_payments_section(user_data)
    
    with pay_tab3:
        render_standing_orders_section(user_data)
    
    with pay_tab4:
        render_payment_history_section(user_data)
    
    with pay_tab5:
        render_payment_settings_section(user_data)

def render_single_payments_section(user_data):
    """Render single payments section"""
    st.markdown("### 💳 Single Business Payments")
    
    payment_type = st.selectbox("Payment Type", [
        "Internal Transfer (Same Bank)", "External Transfer (Other Banks)", 
        "RTGS Transfer", "EFT Transfer", "Mobile Money Transfer", "International Transfer (SWIFT)"
    ])
    
    with st.form("single_payment_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Payment Details**")
            
            if payment_type == "Internal Transfer (Same Bank)":
                recipient_account = st.text_input("Recipient Account Number")
                recipient_name = st.text_input("Recipient Name")
            elif payment_type in ["External Transfer (Other Banks)", "RTGS Transfer", "EFT Transfer"]:
                recipient_bank = st.selectbox("Recipient Bank", [
                    "Equity Bank", "KCB Bank", "Cooperative Bank", "NCBA Bank",
                    "Absa Bank", "Standard Chartered", "DTB Bank", "Family Bank"
                ])
                recipient_account = st.text_input("Recipient Account Number")
                recipient_name = st.text_input("Recipient Name")
            elif payment_type == "Mobile Money Transfer":
                mobile_network = st.selectbox("Mobile Network", ["M-Pesa", "Airtel Money", "T-Kash"])
                recipient_phone = st.text_input("Recipient Phone Number")
                recipient_name = st.text_input("Recipient Name")
            else:  # International Transfer
                recipient_bank = st.text_input("Recipient Bank Name")
                swift_code = st.text_input("SWIFT Code")
                recipient_account = st.text_input("Recipient Account/IBAN")
                recipient_name = st.text_input("Recipient Name")
                recipient_country = st.selectbox("Recipient Country", ["USA", "UK", "UAE", "South Africa", "Uganda"])
            
            payment_amount = st.number_input("Payment Amount (KES)", min_value=1.0, step=1.0)
            
        with col2:
            st.markdown("**Business Information**")
            
            payment_purpose = st.selectbox("Payment Purpose", [
                "Supplier Payment", "Contractor Payment", "Salary Payment", "Utility Payment",
                "Loan Repayment", "Tax Payment", "Insurance Premium", "Rent Payment",
                "Equipment Purchase", "Service Payment", "Other Business Expense"
            ])
            
            payment_reference = st.text_input("Payment Reference/Invoice")
            payment_description = st.text_area("Payment Description")
            
            # Business approval workflow
            requires_approval = payment_amount > 50000
            if requires_approval:
                st.warning("⚠️ This payment requires approval from another signatory")
                approver = st.selectbox("Select Approver", ["John Doe (Director)", "Jane Smith (Finance Manager)"])
            
            # Payment timing
            payment_timing = st.selectbox("Payment Timing", ["Immediate", "Schedule for Later"])
            if payment_timing == "Schedule for Later":
                payment_date = st.date_input("Payment Date")
                payment_time = st.time_input("Payment Time")
        
        # Payment fees and limits
        st.markdown("**Payment Information**")
        
        if payment_type == "Internal Transfer (Same Bank)":
            fee = 0
            processing_time = "Immediate"
        elif payment_type in ["External Transfer (Other Banks)", "EFT Transfer"]:
            fee = 50 if payment_amount <= 100000 else 100
            processing_time = "Same day"
        elif payment_type == "RTGS Transfer":
            fee = 200
            processing_time = "Within 2 hours"
        elif payment_type == "Mobile Money Transfer":
            fee = payment_amount * 0.01  # 1% fee
            processing_time = "Immediate"
        else:  # International
            fee = 2500
            processing_time = "1-3 business days"
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Transaction Fee", f"KES {fee:,.2f}")
        col2.metric("Processing Time", processing_time)
        col3.metric("Total Debit", f"KES {payment_amount + fee:,.2f}")
        
        submitted = st.form_submit_button("💸 Submit Payment", type="primary")
        
        if submitted and payment_amount > 0:
            process_business_payment(user_data, payment_type, payment_amount, fee, requires_approval)

def process_business_payment(user_data, payment_type, amount, fee, requires_approval):
    """Process business payment"""
    try:
        if requires_approval:
            st.success("✅ Payment submitted for approval!")
            st.info("🔄 Payment is pending approval from authorized signatory")
            st.info("📧 Approval request sent via email and SMS")
            st.info("⏰ Payments are typically approved within 2-4 hours during business hours")
        else:
            st.success("✅ Payment processed successfully!")
            st.info(f"💸 Amount: KES {amount:,.2f}")
            st.info(f"💰 Fee: KES {fee:,.2f}")
            st.info(f"📋 Type: {payment_type}")
            
            # Generate reference
            ref_code = f"BP{uuid.uuid4().hex[:8].upper()}"
            st.info(f"📝 Reference: {ref_code}")
            
            if payment_type == "Internal Transfer (Same Bank)":
                st.info("✅ Transfer completed immediately")
            elif payment_type in ["RTGS Transfer", "EFT Transfer"]:
                st.info("🔄 Transfer initiated - recipient will be credited within processing time")
            
    except Exception as e:
        st.error(f"❌ Payment processing failed: {e}")

def render_bulk_payments_section(user_data):
    """Render bulk payments section (payroll, supplier payments)"""
    st.markdown("### 📊 Bulk Payments & Payroll")
    
    bulk_tab1, bulk_tab2, bulk_tab3 = st.tabs([
        "📤 Upload Bulk Payments", "👥 Payroll Management", "📋 Bulk Payment History"
    ])
    
    with bulk_tab1:
        st.markdown("#### 📤 Upload Bulk Payment File")
        
        col1, col2 = st.columns(2)
        
        with col1:
            payment_batch_type = st.selectbox("Batch Type", [
                "Supplier Payments", "Contractor Payments", "Utility Payments",
                "Tax Payments", "Insurance Premiums", "Other Bulk Payments"
            ])
            
            # File upload
            uploaded_file = st.file_uploader(
                "Upload Payment File (CSV/Excel)",
                type=['csv', 'xlsx'],
                help="File should contain: Account Number, Name, Amount, Reference"
            )
            
            if uploaded_file:
                # Display file preview
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                else:
                    df = pd.read_excel(uploaded_file)
                
                st.write("**File Preview:**")
                st.dataframe(df.head())
                
                # Validation
                required_columns = ['Account Number', 'Name', 'Amount', 'Reference']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    total_amount = df['Amount'].sum()
                    total_payments = len(df)
                    
                    st.success(f"✅ File validated successfully!")
                    st.info(f"📊 Total Payments: {total_payments}")
                    st.info(f"💰 Total Amount: KES {total_amount:,.2f}")
        
        with col2:
            st.markdown("#### Bulk Payment Template")
            
            # Download template
            template_data = {
                'Account Number': ['1234567890', '0987654321', '1122334455'],
                'Name': ['Supplier A Ltd', 'Contractor B', 'Service Provider C'],
                'Amount': [50000, 75000, 25000],
                'Reference': ['INV-001', 'CONTRACT-002', 'SERVICE-003'],
                'Bank Code': ['01', '02', '03'],
                'Notes': ['Monthly payment', 'Project completion', 'Service fee']
            }
            
            template_df = pd.DataFrame(template_data)
            
            st.download_button(
                label="📥 Download Template (CSV)",
                data=template_df.to_csv(index=False),
                file_name="bulk_payment_template.csv",
                mime="text/csv"
            )
            
            st.markdown("**Template Instructions:**")
            st.write("• Account Number: 10-digit account number")
            st.write("• Name: Recipient full name")
            st.write("• Amount: Payment amount (numbers only)")
            st.write("• Reference: Invoice/contract reference")
            st.write("• Bank Code: 01=Equity, 02=KCB, 03=Coop")
            st.write("• Notes: Optional payment description")
        
        if uploaded_file and not missing_columns:
            with st.form("bulk_payment_submission"):
                st.markdown("#### Bulk Payment Submission")
                
                execution_date = st.date_input("Execution Date", value=datetime.now().date())
                execution_time = st.selectbox("Execution Time", [
                    "09:00 AM", "12:00 PM", "03:00 PM", "Immediate"
                ])
                
                # Approval requirements
                st.warning("⚠️ Bulk payments require dual authorization")
                primary_approver = st.selectbox("Primary Approver", [
                    "John Doe (Managing Director)", "Jane Smith (Finance Director)"
                ])
                secondary_approver = st.selectbox("Secondary Approver", [
                    "Mike Johnson (Operations Manager)", "Sarah Wilson (Accounts Manager)"
                ])
                
                if st.form_submit_button("📤 Submit Bulk Payment Batch", type="primary"):
                    submit_bulk_payment_batch(user_data, df, payment_batch_type, execution_date)

    with bulk_tab2:
        st.markdown("#### 👥 Payroll Management")
        
        # Payroll options
        payroll_option = st.selectbox("Payroll Action", [
            "Process Monthly Payroll", "Process Bonus Payments", "Process Allowances", "View Payroll History"
        ])
        
        if payroll_option == "Process Monthly Payroll":
            col1, col2 = st.columns(2)
            
            with col1:
                payroll_month = st.selectbox("Payroll Month", [
                    "January 2026", "December 2025", "November 2025"
                ])
                
                # Mock employee data
                employees = [
                    {"name": "John Doe", "employee_id": "EMP001", "basic_salary": 80000, "allowances": 20000},
                    {"name": "Jane Smith", "employee_id": "EMP002", "basic_salary": 75000, "allowances": 15000},
                    {"name": "Mike Johnson", "employee_id": "EMP003", "basic_salary": 60000, "allowances": 10000},
                ]
                
                st.write(f"**Employees for {payroll_month}:**")
                for emp in employees:
                    gross_salary = emp['basic_salary'] + emp['allowances']
                    st.write(f"• {emp['name']} ({emp['employee_id']}): KES {gross_salary:,}")
                
                total_payroll = sum(emp['basic_salary'] + emp['allowances'] for emp in employees)
                st.metric("Total Payroll", f"KES {total_payroll:,}")
            
            with col2:
                st.markdown("**Payroll Processing**")
                
                with st.form("payroll_processing"):
                    payroll_date = st.date_input("Payroll Date")
                    include_statutory = st.checkbox("Include Statutory Deductions", value=True)
                    include_benefits = st.checkbox("Include Benefits", value=True)
                    
                    st.info("💡 **Payroll Information**")
                    st.write("• PAYE tax will be calculated automatically")
                    st.write("• NSSF and NHIF deductions included")
                    st.write("• Net salaries will be credited to employee accounts")
                    
                    if st.form_submit_button("👥 Process Payroll", type="primary"):
                        st.success("✅ Payroll processing initiated!")
                        st.info("🔄 Payroll batch created and sent for approval")
                        st.info("📧 Approval notifications sent to authorized signatories")

    with bulk_tab3:
        st.markdown("#### 📋 Bulk Payment History")
        
        # Mock bulk payment history
        bulk_history = [
            {
                "batch_id": "BP20260104001",
                "type": "Supplier Payments",
                "date": "2026-01-04",
                "payments": 15,
                "amount": 750000,
                "status": "Completed"
            },
            {
                "batch_id": "BP20260103001", 
                "type": "Monthly Payroll",
                "date": "2026-01-03",
                "payments": 25,
                "amount": 1250000,
                "status": "Pending Approval"
            }
        ]
        
        for batch in bulk_history:
            with st.expander(f"📊 {batch['batch_id']} - {batch['type']} ({batch['status']})"):
                col1, col2, col3 = st.columns(3)
                
                col1.write(f"**Batch ID:** {batch['batch_id']}")
                col1.write(f"**Type:** {batch['type']}")
                col1.write(f"**Date:** {batch['date']}")
                
                col2.write(f"**Payments:** {batch['payments']}")
                col2.write(f"**Amount:** KES {batch['amount']:,}")
                col2.write(f"**Status:** {batch['status']}")
                
                col3.write("**Actions:**")
                if batch['status'] == 'Pending Approval':
                    if st.button(f"✅ Approve", key=f"approve_{batch['batch_id']}"):
                        st.success("Batch approved!")
                    if st.button(f"❌ Reject", key=f"reject_{batch['batch_id']}"):
                        st.error("Batch rejected!")
                else:
                    if st.button(f"📄 View Details", key=f"view_{batch['batch_id']}"):
                        st.info("Batch details displayed")

def submit_bulk_payment_batch(user_data, df, batch_type, execution_date):
    """Submit bulk payment batch"""
    try:
        batch_id = f"BP{datetime.now().strftime('%Y%m%d%H%M')}"
        total_amount = df['Amount'].sum()
        total_payments = len(df)
        
        st.success("✅ Bulk payment batch submitted successfully!")
        st.info(f"📊 Batch ID: {batch_id}")
        st.info(f"💰 Total Amount: KES {total_amount:,.2f}")
        st.info(f"📋 Total Payments: {total_payments}")
        st.info(f"📅 Execution Date: {execution_date}")
        st.info("🔄 Batch sent for dual authorization")
        st.info("📧 Approval notifications sent to designated approvers")
        
    except Exception as e:
        st.error(f"❌ Bulk payment submission failed: {e}")

def render_standing_orders_section(user_data):
    """Render standing orders section"""
    st.markdown("### 🔄 Standing Orders & Recurring Payments")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Create New Standing Order")
        
        with st.form("standing_order_form"):
            so_type = st.selectbox("Standing Order Type", [
                "Rent Payment", "Utility Payment", "Loan Repayment", 
                "Insurance Premium", "Supplier Payment", "Tax Payment"
            ])
            
            recipient_name = st.text_input("Recipient Name")
            recipient_account = st.text_input("Recipient Account")
            recipient_bank = st.selectbox("Recipient Bank", [
                "Wekeza Bank (Internal)", "Equity Bank", "KCB Bank", "Cooperative Bank"
            ])
            
            so_amount = st.number_input("Payment Amount (KES)", min_value=100.0)
            
            frequency = st.selectbox("Payment Frequency", [
                "Monthly", "Quarterly", "Semi-Annually", "Annually"
            ])
            
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date (Optional)")
            
            reference = st.text_input("Payment Reference")
            
            if st.form_submit_button("🔄 Create Standing Order", type="primary"):
                create_standing_order(user_data, so_type, so_amount, frequency, start_date)
    
    with col2:
        st.markdown("#### Active Standing Orders")
        
        # Mock standing orders
        standing_orders = [
            {
                "id": "SO001",
                "type": "Rent Payment",
                "recipient": "Property Management Ltd",
                "amount": 150000,
                "frequency": "Monthly",
                "next_payment": "2026-02-01",
                "status": "Active"
            },
            {
                "id": "SO002", 
                "type": "Insurance Premium",
                "recipient": "Insurance Company",
                "amount": 25000,
                "frequency": "Monthly",
                "next_payment": "2026-01-15",
                "status": "Active"
            }
        ]
        
        for so in standing_orders:
            with st.expander(f"🔄 {so['type']} - {so['id']} ({so['status']})"):
                st.write(f"**Recipient:** {so['recipient']}")
                st.write(f"**Amount:** KES {so['amount']:,}")
                st.write(f"**Frequency:** {so['frequency']}")
                st.write(f"**Next Payment:** {so['next_payment']}")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"⏸️ Suspend", key=f"suspend_{so['id']}"):
                        st.warning("Standing order suspended")
                
                with col2:
                    if st.button(f"✏️ Modify", key=f"modify_{so['id']}"):
                        st.info("Modification form opened")
                
                with col3:
                    if st.button(f"❌ Cancel", key=f"cancel_{so['id']}"):
                        st.error("Standing order cancelled")

def create_standing_order(user_data, so_type, amount, frequency, start_date):
    """Create a standing order"""
    try:
        so_id = f"SO{uuid.uuid4().hex[:6].upper()}"
        
        st.success("✅ Standing order created successfully!")
        st.info(f"📋 Standing Order ID: {so_id}")
        st.info(f"💰 Amount: KES {amount:,.2f}")
        st.info(f"🔄 Frequency: {frequency}")
        st.info(f"📅 Start Date: {start_date}")
        st.info("📧 Confirmation sent to registered email")
        
    except Exception as e:
        st.error(f"❌ Standing order creation failed: {e}")

def render_payment_history_section(user_data):
    """Render payment history section"""
    st.markdown("### 📋 Business Payment History")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_filter = st.selectbox("Date Range", [
            "Last 7 days", "Last 30 days", "Last 3 months", "Last 6 months", "Custom"
        ])
    
    with col2:
        payment_filter = st.selectbox("Payment Type", [
            "All Payments", "Single Payments", "Bulk Payments", "Standing Orders", "Payroll"
        ])
    
    with col3:
        status_filter = st.selectbox("Status", [
            "All Statuses", "Completed", "Pending", "Failed", "Cancelled"
        ])
    
    # Mock payment history
    payment_history = [
        {
            "date": "2026-01-04",
            "type": "Single Payment",
            "recipient": "ABC Suppliers Ltd",
            "amount": 75000,
            "reference": "INV-2026-001",
            "status": "Completed"
        },
        {
            "date": "2026-01-03",
            "type": "Bulk Payment",
            "recipient": "Multiple Recipients",
            "amount": 450000,
            "reference": "BP20260103001",
            "status": "Pending Approval"
        },
        {
            "date": "2026-01-01",
            "type": "Standing Order",
            "recipient": "Property Management",
            "amount": 150000,
            "reference": "SO001-JAN2026",
            "status": "Completed"
        }
    ]
    
    # Display payment history
    for payment in payment_history:
        status_color = "🟢" if payment['status'] == 'Completed' else "🟡" if payment['status'] == 'Pending Approval' else "🔴"
        
        with st.expander(f"{status_color} {payment['type']} - KES {payment['amount']:,} ({payment['date']})"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Date:** {payment['date']}")
                st.write(f"**Type:** {payment['type']}")
                st.write(f"**Recipient:** {payment['recipient']}")
                st.write(f"**Amount:** KES {payment['amount']:,}")
            
            with col2:
                st.write(f"**Reference:** {payment['reference']}")
                st.write(f"**Status:** {payment['status']}")
                
                if payment['status'] == 'Completed':
                    if st.button(f"📄 Receipt", key=f"receipt_{payment['reference']}"):
                        st.success("Receipt downloaded!")
                elif payment['status'] == 'Pending Approval':
                    if st.button(f"❌ Cancel", key=f"cancel_{payment['reference']}"):
                        st.warning("Payment cancelled!")

def render_payment_settings_section(user_data):
    """Render payment settings section"""
    st.markdown("### ⚙️ Business Payment Settings")
    
    settings_tab1, settings_tab2, settings_tab3 = st.tabs([
        "💰 Payment Limits", "👥 Approval Workflow", "🔔 Notifications"
    ])
    
    with settings_tab1:
        st.markdown("#### 💰 Business Payment Limits")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Current Limits**")
            
            limits = {
                "Single Payment Limit": 1000000,
                "Daily Payment Limit": 5000000,
                "Monthly Payment Limit": 50000000,
                "Bulk Payment Limit": 10000000
            }
            
            for limit_type, amount in limits.items():
                st.write(f"• {limit_type}: KES {amount:,}")
        
        with col2:
            st.markdown("**Modify Limits**")
            
            with st.form("modify_limits"):
                new_single_limit = st.number_input("Single Payment Limit", value=1000000)
                new_daily_limit = st.number_input("Daily Payment Limit", value=5000000)
                new_monthly_limit = st.number_input("Monthly Payment Limit", value=50000000)
                
                justification = st.text_area("Business Justification for Change")
                
                if st.form_submit_button("📝 Request Limit Change"):
                    st.success("✅ Limit change request submitted!")
                    st.info("🔄 Request will be reviewed by relationship manager")

    with settings_tab2:
        st.markdown("#### 👥 Approval Workflow Configuration")
        
        # Approval matrix
        st.markdown("**Current Approval Matrix**")
        
        approval_matrix = [
            {"amount_range": "KES 0 - 50,000", "approval": "Single Signatory"},
            {"amount_range": "KES 50,001 - 500,000", "approval": "Dual Authorization"},
            {"amount_range": "KES 500,001 - 2,000,000", "approval": "Board Resolution"},
            {"amount_range": "Above KES 2,000,000", "approval": "Board + Central Bank"}
        ]
        
        df_approval = pd.DataFrame(approval_matrix)
        st.table(df_approval)
        
        # Authorized signatories
        st.markdown("**Authorized Signatories**")
        
        signatories = [
            {"name": "John Doe", "role": "Managing Director", "limit": 2000000, "status": "Active"},
            {"name": "Jane Smith", "role": "Finance Director", "limit": 1000000, "status": "Active"},
            {"name": "Mike Johnson", "role": "Operations Manager", "limit": 500000, "status": "Active"}
        ]
        
        for signatory in signatories:
            st.write(f"• {signatory['name']} ({signatory['role']}) - Limit: KES {signatory['limit']:,} - {signatory['status']}")

    with settings_tab3:
        st.markdown("#### 🔔 Payment Notification Settings")
        
        with st.form("payment_notification_settings"):
            st.markdown("**Email Notifications**")
            email_payment_success = st.checkbox("Payment Success", value=True)
            email_payment_failure = st.checkbox("Payment Failure", value=True)
            email_approval_required = st.checkbox("Approval Required", value=True)
            email_daily_summary = st.checkbox("Daily Payment Summary", value=False)
            
            st.markdown("**SMS Notifications**")
            sms_large_payments = st.checkbox("Large Payments (>KES 100,000)", value=True)
            sms_failed_payments = st.checkbox("Failed Payments", value=True)
            sms_approval_requests = st.checkbox("Approval Requests", value=True)
            
            st.markdown("**System Notifications**")
            system_limit_alerts = st.checkbox("Limit Alerts", value=True)
            system_security_alerts = st.checkbox("Security Alerts", value=True)
            
            if st.form_submit_button("💾 Save Notification Settings"):
                st.success("✅ Notification settings updated!")

def render_credit_section(user_data):
    """Render the credit and lending section"""
    st.subheader("💰 Business Credit & Lending")
    
    # Credit tabs
    credit_tab1, credit_tab2, credit_tab3, credit_tab4, credit_tab5 = st.tabs([
        "📝 Apply for Credit", "📋 My Credit Facilities", "💳 Credit Payments", "📊 Credit Analysis", "⚙️ Credit Settings"
    ])
    
    with credit_tab1:
        render_credit_application_section(user_data)
    
    with credit_tab2:
        render_my_credit_facilities_section(user_data)
    
    with credit_tab3:
        render_credit_payments_section(user_data)
    
    with credit_tab4:
        render_credit_analysis_section(user_data)
    
    with credit_tab5:
        render_credit_settings_section(user_data)

def render_credit_application_section(user_data):
    """Render credit application section"""
    st.markdown("### 📝 Business Credit Applications")
    
    # Credit product selection
    credit_products = [
        {
            "name": "Working Capital Loan",
            "description": "Short-term financing for daily operations",
            "max_amount": 5000000,
            "tenure": "6-24 months",
            "rate": "12-15% p.a.",
            "features": ["Quick approval", "Flexible repayment", "No collateral up to KES 1M"]
        },
        {
            "name": "Term Loan",
            "description": "Long-term financing for business expansion",
            "max_amount": 20000000,
            "tenure": "12-60 months",
            "rate": "10-14% p.a.",
            "features": ["Competitive rates", "Grace period available", "Asset financing"]
        },
        {
            "name": "Overdraft Facility",
            "description": "Credit line linked to your current account",
            "max_amount": 2000000,
            "tenure": "12 months renewable",
            "rate": "14-18% p.a.",
            "features": ["Pay interest on usage only", "Instant access", "Automatic renewal"]
        },
        {
            "name": "Asset Finance",
            "description": "Financing for equipment and machinery",
            "max_amount": 50000000,
            "tenure": "12-84 months",
            "rate": "11-16% p.a.",
            "features": ["Up to 90% financing", "Asset as collateral", "Flexible structures"]
        },
        {
            "name": "Trade Finance",
            "description": "Letters of credit and trade guarantees",
            "max_amount": 100000000,
            "tenure": "3-12 months",
            "rate": "8-12% p.a.",
            "features": ["Import/Export support", "Documentary credits", "Performance guarantees"]
        }
    ]
    
    selected_product = st.selectbox(
        "Select Credit Product",
        credit_products,
        format_func=lambda x: f"{x['name']} - Max: KES {x['max_amount']:,}"
    )
    
    # Display product details
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### {selected_product['name']}")
        st.write(f"**Description:** {selected_product['description']}")
        st.write(f"**Maximum Amount:** KES {selected_product['max_amount']:,}")
        st.write(f"**Tenure:** {selected_product['tenure']}")
        st.write(f"**Interest Rate:** {selected_product['rate']}")
        
        st.markdown("**Key Features:**")
        for feature in selected_product['features']:
            st.write(f"• {feature}")
    
    with col2:
        st.markdown("#### Quick Eligibility Check")
        
        with st.form("eligibility_check"):
            business_age = st.number_input("Business Age (years)", min_value=0.0, step=0.5)
            annual_turnover = st.number_input("Annual Turnover (KES)", min_value=0.0, step=100000.0)
            monthly_revenue = st.number_input("Average Monthly Revenue (KES)", min_value=0.0, step=10000.0)
            existing_loans = st.number_input("Existing Loan Obligations (KES)", min_value=0.0, step=10000.0)
            
            if st.form_submit_button("🔍 Check Eligibility"):
                eligibility_score = calculate_business_eligibility(business_age, annual_turnover, monthly_revenue, existing_loans)
                
                if eligibility_score >= 70:
                    st.success(f"✅ Excellent eligibility! Score: {eligibility_score}%")
                    st.info("You qualify for our best rates and terms")
                elif eligibility_score >= 50:
                    st.warning(f"⚠️ Good eligibility. Score: {eligibility_score}%")
                    st.info("You may qualify with additional documentation")
                else:
                    st.error(f"❌ Limited eligibility. Score: {eligibility_score}%")
                    st.info("Consider improving business metrics before applying")
    
    # Credit application form
    st.markdown("---")
    st.markdown("### 📋 Credit Application Form")
    
    with st.form("credit_application_form"):
        # Basic loan details
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Loan Requirements**")
            loan_amount = st.number_input(
                "Requested Amount (KES)",
                min_value=50000.0,
                max_value=float(selected_product['max_amount']),
                step=10000.0
            )
            
            loan_purpose = st.selectbox("Loan Purpose", [
                "Working Capital", "Business Expansion", "Equipment Purchase",
                "Inventory Financing", "Cash Flow Management", "Debt Consolidation",
                "Marketing & Advertising", "Technology Upgrade", "Other"
            ])
            
            if loan_purpose == "Other":
                other_purpose = st.text_input("Please specify purpose")
            
            preferred_tenure = st.selectbox("Preferred Tenure", [
                "6 months", "12 months", "18 months", "24 months", "36 months", "48 months", "60 months"
            ])
        
        with col2:
            st.markdown("**Business Information**")
            
            # Get business info from database
            try:
                conn = get_db_connection()
                cursor = conn.cursor(dictionary=True)
                
                cursor.execute("""
                    SELECT b.*, u.full_name, u.email, u.phone_number
                    FROM businesses b
                    JOIN users u ON b.business_id = u.business_id
                    WHERE b.business_id = %s AND u.user_id = %s
                """, (user_data['business_id'], user_data['user_id']))
                
                business_info = cursor.fetchone()
                conn.close()
                
                if business_info:
                    st.text_input("Business Name", value=business_info['business_name'], disabled=True)
                    st.text_input("Registration Number", value=business_info['registration_no'], disabled=True)
                    st.text_input("KRA PIN", value=business_info['kra_pin'], disabled=True)
                    st.text_input("Business Sector", value=business_info['sector'], disabled=True)
                
            except Exception as e:
                st.error(f"Error loading business information: {e}")
        
        # Financial information
        st.markdown("**Financial Information**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            monthly_sales = st.number_input("Average Monthly Sales (KES)", min_value=0.0, step=10000.0)
            monthly_expenses = st.number_input("Average Monthly Expenses (KES)", min_value=0.0, step=5000.0)
        
        with col2:
            cash_at_bank = st.number_input("Cash at Bank (KES)", min_value=0.0, step=5000.0)
            inventory_value = st.number_input("Inventory Value (KES)", min_value=0.0, step=10000.0)
        
        with col3:
            fixed_assets = st.number_input("Fixed Assets Value (KES)", min_value=0.0, step=50000.0)
            total_liabilities = st.number_input("Total Liabilities (KES)", min_value=0.0, step=10000.0)
        
        # Collateral information (if required)
        if selected_product['name'] in ['Term Loan', 'Asset Finance']:
            st.markdown("**Collateral Information**")
            
            collateral_type = st.selectbox("Collateral Type", [
                "Business Premises", "Equipment/Machinery", "Motor Vehicle", 
                "Land/Property", "Fixed Deposits", "Government Securities", "Other"
            ])
            
            collateral_value = st.number_input("Estimated Collateral Value (KES)", min_value=0.0, step=50000.0)
            collateral_description = st.text_area("Collateral Description")
        
        # Supporting documents
        st.markdown("**Supporting Documents**")
        
        st.info("📋 **Required Documents:**")
        st.write("• Certificate of Incorporation")
        st.write("• KRA PIN Certificate")
        st.write("• Business Permit/License")
        st.write("• 6 months bank statements")
        st.write("• Financial statements (if available)")
        st.write("• Collateral documents (if applicable)")
        
        # Document upload
        uploaded_docs = st.file_uploader(
            "Upload Supporting Documents",
            type=['pdf', 'jpg', 'png', 'doc', 'docx'],
            accept_multiple_files=True
        )
        
        # Terms and conditions
        st.markdown("**Terms and Conditions**")
        
        terms_accepted = st.checkbox("I accept the terms and conditions for credit application")
        consent_credit_check = st.checkbox("I consent to credit bureau checks and information sharing")
        
        # Calculate loan details
        if loan_amount > 0:
            # Simple interest calculation for display
            annual_rate = 0.13  # Average 13%
            monthly_rate = annual_rate / 12
            tenure_months = int(preferred_tenure.split()[0])
            
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate)**tenure_months) / ((1 + monthly_rate)**tenure_months - 1)
            total_payment = monthly_payment * tenure_months
            total_interest = total_payment - loan_amount
            
            st.markdown("**Loan Summary**")
            col1, col2, col3 = st.columns(3)
            col1.metric("Monthly Payment", f"KES {monthly_payment:,.2f}")
            col2.metric("Total Interest", f"KES {total_interest:,.2f}")
            col3.metric("Total Payment", f"KES {total_payment:,.2f}")
        
        submitted = st.form_submit_button("📝 Submit Credit Application", type="primary")
        
        if submitted and terms_accepted and consent_credit_check:
            submit_credit_application(user_data, selected_product, loan_amount, loan_purpose, preferred_tenure)

def calculate_business_eligibility(business_age, annual_turnover, monthly_revenue, existing_loans):
    """Calculate business credit eligibility score"""
    score = 0
    
    # Business age (max 25 points)
    if business_age >= 3:
        score += 25
    elif business_age >= 2:
        score += 20
    elif business_age >= 1:
        score += 15
    else:
        score += 5
    
    # Annual turnover (max 30 points)
    if annual_turnover >= 10000000:
        score += 30
    elif annual_turnover >= 5000000:
        score += 25
    elif annual_turnover >= 2000000:
        score += 20
    elif annual_turnover >= 1000000:
        score += 15
    else:
        score += 5
    
    # Monthly revenue consistency (max 25 points)
    expected_monthly = annual_turnover / 12 if annual_turnover > 0 else 0
    if monthly_revenue >= expected_monthly * 0.8:
        score += 25
    elif monthly_revenue >= expected_monthly * 0.6:
        score += 20
    else:
        score += 10
    
    # Debt-to-income ratio (max 20 points)
    if existing_loans == 0:
        score += 20
    elif existing_loans <= monthly_revenue * 3:
        score += 15
    elif existing_loans <= monthly_revenue * 6:
        score += 10
    else:
        score += 5
    
    return min(score, 100)

def submit_credit_application(user_data, product, amount, purpose, tenure):
    """Submit credit application"""
    try:
        # Generate application reference
        app_ref = f"CA{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        st.success("✅ Credit application submitted successfully!")
        st.info(f"📋 Application Reference: {app_ref}")
        st.info(f"💰 Product: {product['name']}")
        st.info(f"💵 Amount: KES {amount:,.2f}")
        st.info(f"📅 Tenure: {tenure}")
        st.info(f"🎯 Purpose: {purpose}")
        
        st.markdown("**Next Steps:**")
        st.info("1. 📧 Confirmation email sent to registered address")
        st.info("2. 📞 Relationship manager will contact you within 24 hours")
        st.info("3. 🔍 Credit assessment and verification (2-5 business days)")
        st.info("4. 📋 Loan committee review and approval")
        st.info("5. 💰 Disbursement upon approval and documentation")
        
        st.warning("⏰ **Processing Timeline:** 5-10 business days for most applications")
        
    except Exception as e:
        st.error(f"❌ Credit application submission failed: {e}")

def render_my_credit_facilities_section(user_data):
    """Render my credit facilities section"""
    st.markdown("### 📋 My Business Credit Facilities")
    
    # Mock credit facilities data
    credit_facilities = [
        {
            "facility_id": "CF001",
            "product": "Working Capital Loan",
            "approved_amount": 2000000,
            "outstanding_balance": 1450000,
            "monthly_payment": 185000,
            "next_payment_date": "2026-01-15",
            "interest_rate": 13.5,
            "status": "Active",
            "disbursement_date": "2025-06-15",
            "maturity_date": "2026-06-15"
        },
        {
            "facility_id": "CF002",
            "product": "Overdraft Facility", 
            "approved_amount": 500000,
            "outstanding_balance": 125000,
            "monthly_payment": 0,  # Interest only
            "next_payment_date": "2026-01-31",
            "interest_rate": 16.0,
            "status": "Active",
            "disbursement_date": "2025-01-01",
            "maturity_date": "2026-01-01"
        }
    ]
    
    if credit_facilities:
        # Summary metrics
        total_approved = sum(cf['approved_amount'] for cf in credit_facilities)
        total_outstanding = sum(cf['outstanding_balance'] for cf in credit_facilities)
        total_monthly_payment = sum(cf['monthly_payment'] for cf in credit_facilities)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Credit Limit", f"KES {total_approved:,.2f}")
        col2.metric("Total Outstanding", f"KES {total_outstanding:,.2f}")
        col3.metric("Available Credit", f"KES {total_approved - total_outstanding:,.2f}")
        col4.metric("Monthly Payments", f"KES {total_monthly_payment:,.2f}")
        
        st.markdown("---")
        
        # Individual facilities
        for facility in credit_facilities:
            utilization = (facility['outstanding_balance'] / facility['approved_amount']) * 100
            
            with st.expander(f"💳 {facility['product']} - {facility['facility_id']} ({facility['status']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Facility Details**")
                    st.write(f"Facility ID: {facility['facility_id']}")
                    st.write(f"Product: {facility['product']}")
                    st.write(f"Status: {facility['status']}")
                    st.write(f"Interest Rate: {facility['interest_rate']}% p.a.")
                
                with col2:
                    st.write(f"**Financial Summary**")
                    st.write(f"Approved Amount: KES {facility['approved_amount']:,}")
                    st.write(f"Outstanding: KES {facility['outstanding_balance']:,}")
                    st.write(f"Available: KES {facility['approved_amount'] - facility['outstanding_balance']:,}")
                    st.write(f"Utilization: {utilization:.1f}%")
                
                with col3:
                    st.write(f"**Payment Information**")
                    if facility['monthly_payment'] > 0:
                        st.write(f"Monthly Payment: KES {facility['monthly_payment']:,}")
                    else:
                        st.write("Interest Only Facility")
                    st.write(f"Next Payment: {facility['next_payment_date']}")
                    st.write(f"Maturity Date: {facility['maturity_date']}")
                
                # Progress bar for utilization
                st.progress(utilization / 100)
                
                # Action buttons
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button(f"💰 Make Payment", key=f"pay_{facility['facility_id']}"):
                        st.session_state[f'payment_facility_{facility["facility_id"]}'] = True
                
                with col2:
                    if st.button(f"📊 Statement", key=f"stmt_{facility['facility_id']}"):
                        generate_facility_statement(facility)
                
                with col3:
                    if facility['product'] == 'Overdraft Facility':
                        if st.button(f"💳 Draw Down", key=f"draw_{facility['facility_id']}"):
                            st.session_state[f'drawdown_facility_{facility["facility_id"]}'] = True
                
                with col4:
                    if st.button(f"📞 Contact RM", key=f"contact_{facility['facility_id']}"):
                        st.info("📞 Relationship Manager: John Kamau (+254 700 123 456)")
                
                # Payment form
                if st.session_state.get(f'payment_facility_{facility["facility_id"]}', False):
                    with st.form(f"payment_form_{facility['facility_id']}"):
                        st.markdown("**Make Loan Payment**")
                        
                        payment_type = st.selectbox("Payment Type", [
                            "Regular Monthly Payment", "Principal Payment", "Full Settlement", "Interest Only"
                        ])
                        
                        if payment_type == "Regular Monthly Payment":
                            payment_amount = facility['monthly_payment']
                        elif payment_type == "Full Settlement":
                            payment_amount = facility['outstanding_balance']
                        else:
                            payment_amount = st.number_input("Payment Amount (KES)", min_value=1000.0)
                        
                        st.metric("Payment Amount", f"KES {payment_amount:,.2f}")
                        
                        if st.form_submit_button("💰 Process Payment"):
                            process_loan_payment(facility, payment_amount, payment_type)
                            st.session_state[f'payment_facility_{facility["facility_id"]}'] = False
                            st.rerun()
                
                # Drawdown form for overdraft
                if st.session_state.get(f'drawdown_facility_{facility["facility_id"]}', False):
                    with st.form(f"drawdown_form_{facility['facility_id']}"):
                        st.markdown("**Overdraft Drawdown**")
                        
                        available_limit = facility['approved_amount'] - facility['outstanding_balance']
                        drawdown_amount = st.number_input(
                            "Drawdown Amount (KES)",
                            min_value=1000.0,
                            max_value=float(available_limit),
                            step=1000.0
                        )
                        
                        drawdown_purpose = st.text_input("Purpose of Drawdown")
                        
                        st.info(f"💰 Available Limit: KES {available_limit:,.2f}")
                        st.info(f"📈 Interest Rate: {facility['interest_rate']}% p.a.")
                        
                        if st.form_submit_button("💳 Draw Down"):
                            process_overdraft_drawdown(facility, drawdown_amount, drawdown_purpose)
                            st.session_state[f'drawdown_facility_{facility["facility_id"]}'] = False
                            st.rerun()
    else:
        st.info("📋 No active credit facilities found")
        st.info("💡 Apply for a credit facility using the 'Apply for Credit' tab")

def generate_facility_statement(facility):
    """Generate facility statement"""
    try:
        st.success("✅ Facility statement generated!")
        st.info(f"📧 Statement for {facility['product']} will be sent to your email")
        
        # Create downloadable statement
        statement_content = f"""
WEKEZA BANK CREDIT FACILITY STATEMENT
Facility ID: {facility['facility_id']}
Product: {facility['product']}
Statement Date: {datetime.now().strftime('%Y-%m-%d')}

Facility Summary:
- Approved Amount: KES {facility['approved_amount']:,}
- Outstanding Balance: KES {facility['outstanding_balance']:,}
- Interest Rate: {facility['interest_rate']}% p.a.
- Next Payment Date: {facility['next_payment_date']}

This is a sample statement. The actual statement will be sent to your email.
        """
        
        st.download_button(
            label="📥 Download Statement",
            data=statement_content,
            file_name=f"facility_statement_{facility['facility_id']}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Statement generation failed: {e}")

def process_loan_payment(facility, amount, payment_type):
    """Process loan payment"""
    try:
        st.success("✅ Loan payment processed successfully!")
        st.info(f"💰 Amount: KES {amount:,.2f}")
        st.info(f"📋 Type: {payment_type}")
        st.info(f"🏦 Facility: {facility['product']}")
        
        # Generate payment reference
        payment_ref = f"LP{uuid.uuid4().hex[:8].upper()}"
        st.info(f"📝 Payment Reference: {payment_ref}")
        
        st.info("📧 Payment confirmation sent to registered email")
        st.info("📱 SMS notification sent")
        
    except Exception as e:
        st.error(f"❌ Loan payment failed: {e}")

def process_overdraft_drawdown(facility, amount, purpose):
    """Process overdraft drawdown"""
    try:
        st.success("✅ Overdraft drawdown processed successfully!")
        st.info(f"💰 Amount: KES {amount:,.2f}")
        st.info(f"🎯 Purpose: {purpose}")
        st.info(f"🏦 Facility: {facility['product']}")
        
        # Generate drawdown reference
        drawdown_ref = f"OD{uuid.uuid4().hex[:8].upper()}"
        st.info(f"📝 Drawdown Reference: {drawdown_ref}")
        
        st.info("💳 Funds credited to your operating account immediately")
        st.info("📧 Drawdown confirmation sent to registered email")
        
    except Exception as e:
        st.error(f"❌ Overdraft drawdown failed: {e}")

def render_credit_payments_section(user_data):
    """Render credit payments section"""
    st.markdown("### 💳 Credit Payments & Management")
    
    # Payment options
    payment_tab1, payment_tab2, payment_tab3 = st.tabs([
        "💰 Make Payments", "📅 Payment Schedule", "📊 Payment History"
    ])
    
    with payment_tab1:
        st.markdown("#### 💰 Make Credit Payments")
        
        # Get active facilities for payment
        active_facilities = [
            {"id": "CF001", "product": "Working Capital Loan", "outstanding": 1450000, "monthly_payment": 185000},
            {"id": "CF002", "product": "Overdraft Facility", "outstanding": 125000, "monthly_payment": 0}
        ]
        
        if active_facilities:
            selected_facility = st.selectbox(
                "Select Facility for Payment",
                active_facilities,
                format_func=lambda x: f"{x['product']} ({x['id']}) - Outstanding: KES {x['outstanding']:,}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                with st.form("credit_payment_form"):
                    payment_method = st.selectbox("Payment Method", [
                        "Debit from Operating Account", "Bank Transfer", "Cheque Payment", "Cash Payment"
                    ])
                    
                    payment_type = st.selectbox("Payment Type", [
                        "Regular Monthly Payment", "Extra Principal Payment", "Interest Only Payment", "Full Settlement"
                    ])
                    
                    if payment_type == "Regular Monthly Payment" and selected_facility['monthly_payment'] > 0:
                        payment_amount = selected_facility['monthly_payment']
                        st.metric("Payment Amount", f"KES {payment_amount:,.2f}")
                    elif payment_type == "Full Settlement":
                        payment_amount = selected_facility['outstanding']
                        st.metric("Payment Amount", f"KES {payment_amount:,.2f}")
                    else:
                        payment_amount = st.number_input("Payment Amount (KES)", min_value=1000.0, step=1000.0)
                    
                    payment_date = st.date_input("Payment Date", value=datetime.now().date())
                    payment_reference = st.text_input("Payment Reference (Optional)")
                    
                    if st.form_submit_button("💰 Process Payment", type="primary"):
                        if payment_amount > 0:
                            st.success("✅ Credit payment processed successfully!")
                            st.info(f"💰 Amount: KES {payment_amount:,.2f}")
                            st.info(f"🏦 Facility: {selected_facility['product']}")
                            st.info(f"📅 Payment Date: {payment_date}")
            
            with col2:
                st.markdown("#### Payment Impact Analysis")
                
                if payment_amount > 0:
                    # Calculate payment impact
                    remaining_balance = max(0, selected_facility['outstanding'] - payment_amount)
                    
                    st.metric("Current Outstanding", f"KES {selected_facility['outstanding']:,.2f}")
                    st.metric("Payment Amount", f"KES {payment_amount:,.2f}")
                    st.metric("New Balance", f"KES {remaining_balance:,.2f}")
                    
                    if remaining_balance == 0:
                        st.success("🎉 This payment will fully settle the facility!")
                    else:
                        reduction_percentage = (payment_amount / selected_facility['outstanding']) * 100
                        st.info(f"📉 Balance reduction: {reduction_percentage:.1f}%")
        else:
            st.info("No active credit facilities requiring payments")

    with payment_tab2:
        st.markdown("#### 📅 Payment Schedule")
        
        # Mock payment schedule
        payment_schedule = [
            {"date": "2026-01-15", "facility": "Working Capital Loan", "amount": 185000, "type": "Monthly Payment", "status": "Due"},
            {"date": "2026-01-31", "facility": "Overdraft Facility", "amount": 2083, "type": "Interest Payment", "status": "Due"},
            {"date": "2026-02-15", "facility": "Working Capital Loan", "amount": 185000, "type": "Monthly Payment", "status": "Scheduled"},
            {"date": "2026-02-28", "facility": "Overdraft Facility", "amount": 2083, "type": "Interest Payment", "status": "Scheduled"}
        ]
        
        # Display upcoming payments
        st.markdown("**Upcoming Payments (Next 60 Days)**")
        
        for payment in payment_schedule:
            status_color = "🔴" if payment['status'] == 'Due' else "🟡" if payment['status'] == 'Scheduled' else "🟢"
            
            with st.expander(f"{status_color} {payment['date']} - {payment['facility']} - KES {payment['amount']:,}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Date:** {payment['date']}")
                    st.write(f"**Facility:** {payment['facility']}")
                    st.write(f"**Amount:** KES {payment['amount']:,}")
                    st.write(f"**Type:** {payment['type']}")
                
                with col2:
                    st.write(f"**Status:** {payment['status']}")
                    
                    if payment['status'] == 'Due':
                        if st.button(f"💰 Pay Now", key=f"pay_scheduled_{payment['date']}_{payment['facility']}"):
                            st.success("Payment processed!")
                    elif payment['status'] == 'Scheduled':
                        if st.button(f"📅 Reschedule", key=f"reschedule_{payment['date']}_{payment['facility']}"):
                            st.info("Rescheduling options displayed")

    with payment_tab3:
        st.markdown("#### 📊 Credit Payment History")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            history_period = st.selectbox("Period", ["Last 30 days", "Last 3 months", "Last 6 months", "Last 12 months"])
        
        with col2:
            facility_filter = st.selectbox("Facility", ["All Facilities", "Working Capital Loan", "Overdraft Facility"])
        
        with col3:
            payment_type_filter = st.selectbox("Payment Type", ["All Types", "Monthly Payments", "Principal Payments", "Interest Payments"])
        
        # Mock payment history
        payment_history = [
            {"date": "2025-12-15", "facility": "Working Capital Loan", "amount": 185000, "type": "Monthly Payment", "reference": "LP12345678"},
            {"date": "2025-11-15", "facility": "Working Capital Loan", "amount": 185000, "type": "Monthly Payment", "reference": "LP12345679"},
            {"date": "2025-11-30", "facility": "Overdraft Facility", "amount": 2083, "type": "Interest Payment", "reference": "LP12345680"}
        ]
        
        # Summary metrics
        total_payments = sum(p['amount'] for p in payment_history)
        payment_count = len(payment_history)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Payments", f"KES {total_payments:,}")
        col2.metric("Number of Payments", payment_count)
        col3.metric("Average Payment", f"KES {total_payments/payment_count if payment_count > 0 else 0:,.2f}")
        
        # Payment history details
        for payment in payment_history:
            with st.expander(f"💰 {payment['date']} - {payment['facility']} - KES {payment['amount']:,}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Date:** {payment['date']}")
                    st.write(f"**Facility:** {payment['facility']}")
                    st.write(f"**Amount:** KES {payment['amount']:,}")
                
                with col2:
                    st.write(f"**Type:** {payment['type']}")
                    st.write(f"**Reference:** {payment['reference']}")
                    
                    if st.button(f"📄 Receipt", key=f"receipt_{payment['reference']}"):
                        st.success("Payment receipt downloaded!")

def render_credit_analysis_section(user_data):
    """Render credit analysis section"""
    st.markdown("### 📊 Business Credit Analysis")
    
    analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs([
        "📈 Credit Utilization", "💰 Payment Performance", "🎯 Credit Recommendations"
    ])
    
    with analysis_tab1:
        st.markdown("#### 📈 Credit Utilization Analysis")
        
        # Mock utilization data
        facilities_utilization = [
            {"facility": "Working Capital Loan", "limit": 2000000, "used": 1450000, "available": 550000},
            {"facility": "Overdraft Facility", "limit": 500000, "used": 125000, "available": 375000}
        ]
        
        # Overall utilization metrics
        total_limit = sum(f['limit'] for f in facilities_utilization)
        total_used = sum(f['used'] for f in facilities_utilization)
        total_available = sum(f['available'] for f in facilities_utilization)
        overall_utilization = (total_used / total_limit) * 100 if total_limit > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Credit Limit", f"KES {total_limit:,}")
        col2.metric("Total Utilized", f"KES {total_used:,}")
        col3.metric("Available Credit", f"KES {total_available:,}")
        col4.metric("Overall Utilization", f"{overall_utilization:.1f}%")
        
        # Individual facility utilization
        st.markdown("**Facility-wise Utilization**")
        
        for facility in facilities_utilization:
            utilization_pct = (facility['used'] / facility['limit']) * 100
            
            st.write(f"**{facility['facility']}**")
            st.progress(utilization_pct / 100)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Limit", f"KES {facility['limit']:,}")
            col2.metric("Used", f"KES {facility['used']:,}")
            col3.metric("Available", f"KES {facility['available']:,}")
            
            # Utilization status
            if utilization_pct > 80:
                st.error(f"⚠️ High utilization ({utilization_pct:.1f}%) - Consider additional credit or payment")
            elif utilization_pct > 60:
                st.warning(f"⚠️ Moderate utilization ({utilization_pct:.1f}%) - Monitor closely")
            else:
                st.success(f"✅ Healthy utilization ({utilization_pct:.1f}%)")
            
            st.markdown("---")

    with analysis_tab2:
        st.markdown("#### 💰 Payment Performance Analysis")
        
        # Payment performance metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("On-time Payments", "95%")
        col2.metric("Late Payments", "5%")
        col3.metric("Average Days Late", "2.3")
        col4.metric("Payment Score", "Excellent")
        
        # Payment trend chart
        st.markdown("**Payment Trend (Last 12 Months)**")
        
        months = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan']
        on_time = [100, 100, 95, 100, 90, 100, 100, 95, 100, 100, 90, 95]
        
        df_payments = pd.DataFrame({
            'Month': months,
            'On-time Payment %': on_time
        })
        
        st.line_chart(df_payments.set_index('Month'))
        
        # Payment insights
        st.markdown("**Payment Insights**")
        st.success("✅ Excellent payment history with 95% on-time payments")
        st.info("💡 Consistent payment behavior qualifies you for better rates")
        st.warning("⚠️ 2 late payments in the last 12 months - maintain consistency for rate improvements")

    with analysis_tab3:
        st.markdown("#### 🎯 Credit Recommendations")
        
        # Personalized recommendations based on business profile
        recommendations = [
            {
                "title": "Increase Overdraft Limit",
                "description": "Based on your payment history and cash flow, you qualify for an increased overdraft limit",
                "benefit": "Better cash flow management",
                "action": "Apply for limit increase",
                "priority": "High"
            },
            {
                "title": "Term Loan for Expansion",
                "description": "Your business growth indicates readiness for expansion financing",
                "benefit": "Lower interest rates than working capital",
                "action": "Explore term loan options",
                "priority": "Medium"
            },
            {
                "title": "Asset Finance Opportunity",
                "description": "Consider asset financing for equipment purchases instead of working capital",
                "benefit": "Lower rates and longer tenure",
                "action": "Discuss with relationship manager",
                "priority": "Low"
            }
        ]
        
        for rec in recommendations:
            priority_color = "🔴" if rec['priority'] == 'High' else "🟡" if rec['priority'] == 'Medium' else "🟢"
            
            with st.expander(f"{priority_color} {rec['title']} ({rec['priority']} Priority)"):
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Benefit:** {rec['benefit']}")
                st.write(f"**Recommended Action:** {rec['action']}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"📞 Contact RM", key=f"contact_rm_{rec['title']}"):
                        st.info("📞 Relationship Manager will contact you within 24 hours")
                
                with col2:
                    if st.button(f"📝 Apply Now", key=f"apply_{rec['title']}"):
                        st.success("Application process initiated!")

def render_credit_settings_section(user_data):
    """Render credit settings section"""
    st.markdown("### ⚙️ Credit Settings & Preferences")
    
    settings_tab1, settings_tab2, settings_tab3 = st.tabs([
        "🔔 Payment Alerts", "📊 Credit Monitoring", "📞 Relationship Manager"
    ])
    
    with settings_tab1:
        st.markdown("#### 🔔 Payment Alert Settings")
        
        with st.form("payment_alert_settings"):
            st.markdown("**Payment Reminder Settings**")
            
            reminder_days = st.selectbox("Payment Reminder (Days Before Due)", [1, 3, 5, 7, 10])
            reminder_methods = st.multiselect("Reminder Methods", ["Email", "SMS", "Push Notification"], default=["Email", "SMS"])
            
            st.markdown("**Late Payment Alerts**")
            late_payment_alerts = st.checkbox("Enable late payment alerts", value=True)
            escalation_days = st.selectbox("Escalation after (Days)", [1, 2, 3, 5])
            
            st.markdown("**Payment Confirmation**")
            payment_confirmation = st.checkbox("Send payment confirmations", value=True)
            monthly_statements = st.checkbox("Monthly credit statements", value=True)
            
            if st.form_submit_button("💾 Save Alert Settings"):
                st.success("✅ Payment alert settings updated!")

    with settings_tab2:
        st.markdown("#### 📊 Credit Monitoring Preferences")
        
        with st.form("credit_monitoring_settings"):
            st.markdown("**Utilization Alerts**")
            utilization_threshold = st.slider("Alert when utilization exceeds (%)", 50, 95, 80)
            utilization_alerts = st.checkbox("Enable utilization alerts", value=True)
            
            st.markdown("**Credit Score Monitoring**")
            credit_score_monitoring = st.checkbox("Monitor business credit score", value=True)
            score_change_alerts = st.checkbox("Alert on score changes", value=True)
            
            st.markdown("**Market Rate Alerts**")
            rate_change_alerts = st.checkbox("Alert on favorable rate changes", value=True)
            refinancing_opportunities = st.checkbox("Refinancing opportunity alerts", value=True)
            
            if st.form_submit_button("💾 Save Monitoring Settings"):
                st.success("✅ Credit monitoring settings updated!")

    with settings_tab3:
        st.markdown("#### 📞 Relationship Manager Contact")
        
        # RM information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Your Relationship Manager**")
            st.write("**Name:** John Kamau")
            st.write("**Title:** Senior Relationship Manager")
            st.write("**Phone:** +254 700 123 456")
            st.write("**Email:** john.kamau@wekezebank.co.ke")
            st.write("**Office:** Westlands Branch")
        
        with col2:
            st.markdown("**Contact Preferences**")
            
            with st.form("rm_contact_preferences"):
                preferred_contact_method = st.selectbox("Preferred Contact Method", ["Phone", "Email", "WhatsApp", "In-person"])
                preferred_contact_time = st.selectbox("Preferred Contact Time", [
                    "Morning (8AM-12PM)", "Afternoon (12PM-5PM)", "Evening (5PM-8PM)", "Anytime"
                ])
                
                contact_frequency = st.selectbox("Contact Frequency", [
                    "Weekly", "Bi-weekly", "Monthly", "Quarterly", "As needed only"
                ])
                
                if st.form_submit_button("💾 Save Contact Preferences"):
                    st.success("✅ Contact preferences updated!")
        
        # Quick contact actions
        st.markdown("**Quick Actions**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📞 Schedule Call"):
                st.success("Call scheduled! RM will contact you within 24 hours")
        
        with col2:
            if st.button("📧 Send Email"):
                st.success("Email sent to your relationship manager")
        
        with col3:
            if st.button("📅 Book Meeting"):
                st.success("Meeting request sent! You'll receive confirmation shortly")