import streamlit as st
import pandas as pd
import mysql.connector
from datetime import datetime
import uuid

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

def render_save_section(user_data):
    """Render the savings/deposits section"""
    st.subheader("💳 Save Money - Deposits & Savings")
    
    # Savings tabs
    save_tab1, save_tab2, save_tab3, save_tab4 = st.tabs([
        "💰 Make Deposit", "📊 Savings Goals", "🎯 Fixed Deposits", "📈 Savings History"
    ])
    
    with save_tab1:
        render_deposit_section(user_data)
    
    with save_tab2:
        render_savings_goals_section(user_data)
    
    with save_tab3:
        render_fixed_deposits_section(user_data)
    
    with save_tab4:
        render_savings_history_section(user_data)

def render_deposit_section(user_data):
    """Render deposit section"""
    st.markdown("### 💰 Make a Deposit")
    
    with st.form("deposit_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            deposit_method = st.selectbox("Deposit Method", [
                "Cash Deposit (Branch)",
                "Cheque Deposit",
                "Mobile Money Deposit",
                "Bank Transfer"
            ])
            
            deposit_amount = st.number_input("Deposit Amount (KES)", min_value=10.0, step=10.0)
            
            if deposit_method == "Cheque Deposit":
                cheque_number = st.text_input("Cheque Number")
                issuing_bank = st.selectbox("Issuing Bank", [
                    "Equity Bank", "KCB Bank", "Cooperative Bank", "NCBA Bank",
                    "Absa Bank", "Standard Chartered", "DTB Bank", "Family Bank"
                ])
                cheque_date = st.date_input("Cheque Date")
            
            deposit_reference = st.text_input("Reference/Description", placeholder="Salary, business income, etc.")
        
        with col2:
            st.info("💡 **Deposit Information**")
            
            if deposit_method == "Cash Deposit (Branch)":
                st.write("• Visit any Wekeza branch")
                st.write("• Bring valid ID")
                st.write("• Funds available immediately")
                processing_time = "Immediate"
            elif deposit_method == "Cheque Deposit":
                st.write("• 2-3 business days clearing")
                st.write("• Local cheques: 2 days")
                st.write("• Upcountry cheques: 3 days")
                processing_time = "2-3 business days"
            elif deposit_method == "Mobile Money Deposit":
                st.write("• M-Pesa Paybill: 522522")
                st.write(f"• Account: {user_data['account_number']}")
                st.write("• Funds available immediately")
                processing_time = "Immediate"
            else:
                st.write("• Inter-bank transfers")
                st.write("• Same day processing")
                st.write("• Funds available within hours")
                processing_time = "Same day"
            
            st.metric("Processing Time", processing_time)
        
        submitted = st.form_submit_button("💰 Schedule Deposit", type="primary")
        
        if submitted and deposit_amount > 0:
            schedule_deposit(user_data, deposit_method, deposit_amount, deposit_reference)

def schedule_deposit(user_data, method, amount, reference):
    """Schedule a deposit (for tracking purposes)"""
    try:
        # For demo purposes, we'll create a pending deposit record
        st.success(f"✅ Deposit scheduled successfully!")
        st.info(f"💰 Amount: KES {amount:,.2f}")
        st.info(f"📋 Method: {method}")
        st.info(f"📝 Reference: {reference}")
        
        if method == "Cash Deposit (Branch)":
            st.info("🏦 Visit any Wekeza branch to complete your deposit")
        elif method == "Cheque Deposit":
            st.info("📄 Bring your cheque to any Wekeza branch or use our cheque drop box")
        elif method == "Mobile Money Deposit":
            st.info(f"📱 Send money to Paybill 522522, Account: {user_data['account_number']}")
        else:
            st.info("🏦 Initiate transfer from your other bank account")
        
    except Exception as e:
        st.error(f"❌ Deposit scheduling failed: {e}")

def render_savings_goals_section(user_data):
    """Render savings goals section"""
    st.markdown("### 📊 Savings Goals")
    
    # Mock savings goals data
    savings_goals = [
        {"name": "Emergency Fund", "target": 100000, "current": 45000, "deadline": "2026-12-31"},
        {"name": "Vacation Fund", "target": 50000, "current": 12000, "deadline": "2026-06-30"},
        {"name": "New Car", "target": 800000, "current": 150000, "deadline": "2027-03-31"}
    ]
    
    # Display existing goals
    if savings_goals:
        st.markdown("#### Your Savings Goals")
        
        for goal in savings_goals:
            progress = (goal['current'] / goal['target']) * 100
            
            with st.expander(f"🎯 {goal['name']} - {progress:.1f}% Complete"):
                col1, col2, col3 = st.columns(3)
                
                col1.metric("Target Amount", f"KES {goal['target']:,.2f}")
                col2.metric("Current Savings", f"KES {goal['current']:,.2f}")
                col3.metric("Remaining", f"KES {goal['target'] - goal['current']:,.2f}")
                
                # Progress bar
                st.progress(progress / 100)
                
                # Monthly savings needed
                from datetime import datetime
                deadline = datetime.strptime(goal['deadline'], '%Y-%m-%d')
                months_left = max(1, (deadline - datetime.now()).days / 30)
                monthly_needed = (goal['target'] - goal['current']) / months_left
                
                st.write(f"**Deadline:** {goal['deadline']}")
                st.write(f"**Monthly savings needed:** KES {monthly_needed:,.2f}")
                
                # Quick save button
                if st.button(f"💰 Save towards {goal['name']}", key=f"save_{goal['name']}"):
                    st.session_state[f'quick_save_{goal["name"]}'] = True
    
    # Create new goal
    st.markdown("#### Create New Savings Goal")
    
    with st.form("new_savings_goal"):
        col1, col2 = st.columns(2)
        
        with col1:
            goal_name = st.text_input("Goal Name", placeholder="e.g., New Phone, Holiday")
            target_amount = st.number_input("Target Amount (KES)", min_value=1000.0, step=1000.0)
        
        with col2:
            target_date = st.date_input("Target Date")
            initial_deposit = st.number_input("Initial Deposit (KES)", min_value=0.0, step=100.0)
        
        if st.form_submit_button("🎯 Create Goal", type="primary"):
            if goal_name and target_amount > 0:
                st.success(f"✅ Savings goal '{goal_name}' created!")
                st.info(f"🎯 Target: KES {target_amount:,.2f} by {target_date}")
                if initial_deposit > 0:
                    st.info(f"💰 Initial deposit: KES {initial_deposit:,.2f}")

def render_fixed_deposits_section(user_data):
    """Render fixed deposits section"""
    st.markdown("### 🎯 Fixed Deposits")
    
    # Fixed deposit rates
    fd_rates = [
        {"term": "3 months", "rate": 8.5, "min_amount": 50000},
        {"term": "6 months", "rate": 9.0, "min_amount": 50000},
        {"term": "12 months", "rate": 10.0, "min_amount": 50000},
        {"term": "24 months", "rate": 11.0, "min_amount": 100000},
        {"term": "36 months", "rate": 12.0, "min_amount": 100000}
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Current Fixed Deposit Rates")
        
        for rate in fd_rates:
            st.write(f"**{rate['term']}:** {rate['rate']}% p.a. (Min: KES {rate['min_amount']:,})")
        
        st.markdown("#### Create New Fixed Deposit")
        
        with st.form("fixed_deposit_form"):
            selected_term = st.selectbox("Select Term", fd_rates, format_func=lambda x: f"{x['term']} - {x['rate']}% p.a.")
            
            fd_amount = st.number_input(
                "Deposit Amount (KES)",
                min_value=float(selected_term['min_amount']),
                step=1000.0,
                value=float(selected_term['min_amount'])
            )
            
            # Calculate maturity
            interest_earned = (fd_amount * selected_term['rate'] / 100) * (int(selected_term['term'].split()[0]) / 12)
            maturity_amount = fd_amount + interest_earned
            
            st.info(f"💰 **Maturity Amount:** KES {maturity_amount:,.2f}")
            st.info(f"📈 **Interest Earned:** KES {interest_earned:,.2f}")
            
            auto_renew = st.checkbox("Auto-renew at maturity")
            
            if st.form_submit_button("🎯 Create Fixed Deposit", type="primary"):
                if fd_amount >= selected_term['min_amount']:
                    if fd_amount <= user_data['balance']:
                        create_fixed_deposit(user_data, selected_term, fd_amount, auto_renew)
                    else:
                        st.error("Insufficient balance for this fixed deposit")
                else:
                    st.error(f"Minimum amount is KES {selected_term['min_amount']:,}")
    
    with col2:
        st.markdown("#### My Fixed Deposits")
        
        # Mock existing FDs
        existing_fds = [
            {
                "fd_number": "FD001234",
                "amount": 100000,
                "rate": 10.0,
                "term": "12 months",
                "start_date": "2025-12-01",
                "maturity_date": "2026-12-01",
                "status": "Active"
            }
        ]
        
        if existing_fds:
            for fd in existing_fds:
                with st.expander(f"💎 {fd['fd_number']} - KES {fd['amount']:,}"):
                    st.write(f"**Amount:** KES {fd['amount']:,}")
                    st.write(f"**Interest Rate:** {fd['rate']}% p.a.")
                    st.write(f"**Term:** {fd['term']}")
                    st.write(f"**Start Date:** {fd['start_date']}")
                    st.write(f"**Maturity Date:** {fd['maturity_date']}")
                    st.write(f"**Status:** {fd['status']}")
                    
                    # Calculate current value
                    from datetime import datetime
                    start = datetime.strptime(fd['start_date'], '%Y-%m-%d')
                    days_elapsed = (datetime.now() - start).days
                    daily_interest = (fd['amount'] * fd['rate'] / 100) / 365
                    current_value = fd['amount'] + (daily_interest * days_elapsed)
                    
                    st.metric("Current Value", f"KES {current_value:,.2f}")
        else:
            st.info("No fixed deposits found")

def create_fixed_deposit(user_data, term_info, amount, auto_renew):
    """Create a fixed deposit"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Update account balance
        cursor.execute("UPDATE accounts SET balance = balance - %s WHERE user_id = %s", 
                      (amount, user_data['user_id']))
        
        # Generate FD number
        fd_number = f"FD{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        
        # Record transaction
        ref_code = f"FD{uuid.uuid4().hex[:8].upper()}"
        cursor.execute("""
            INSERT INTO transactions (account_id, txn_type, amount, reference_code, description, created_at)
            SELECT account_id, 'FIXED_DEPOSIT', %s, %s, %s, %s
            FROM accounts WHERE user_id = %s
        """, (amount, ref_code, f"Fixed deposit creation - {fd_number}", datetime.now(), user_data['user_id']))
        
        conn.commit()
        conn.close()
        
        st.success(f"✅ Fixed deposit created successfully!")
        st.info(f"📋 FD Number: {fd_number}")
        st.info(f"💰 Amount: KES {amount:,.2f}")
        st.info(f"📈 Interest Rate: {term_info['rate']}% p.a.")
        st.info(f"⏰ Term: {term_info['term']}")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Fixed deposit creation failed: {e}")

def render_savings_history_section(user_data):
    """Render savings history section"""
    st.markdown("### 📈 Savings History")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get deposit transactions
        cursor.execute("""
            SELECT t.*, a.account_number
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = %s 
            AND t.txn_type IN ('DEPOSIT', 'TRANSFER_IN', 'FIXED_DEPOSIT')
            ORDER BY t.created_at DESC
            LIMIT 20
        """, (user_data['user_id'],))
        
        deposits = cursor.fetchall()
        conn.close()
        
        if deposits:
            # Summary
            total_deposits = sum(d['amount'] for d in deposits)
            col1, col2, col3 = st.columns(3)
            
            col1.metric("Total Deposits", f"KES {total_deposits:,.2f}")
            col2.metric("Number of Deposits", len(deposits))
            col3.metric("Average Deposit", f"KES {total_deposits/len(deposits):,.2f}")
            
            st.markdown("---")
            
            # Deposit history
            for deposit in deposits:
                with st.expander(f"💰 {deposit['txn_type'].replace('_', ' ').title()} - KES {deposit['amount']:,.2f} ({deposit['created_at'].strftime('%Y-%m-%d')})"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Amount:** KES {deposit['amount']:,.2f}")
                        st.write(f"**Type:** {deposit['txn_type'].replace('_', ' ').title()}")
                        st.write(f"**Reference:** {deposit['reference_code']}")
                    
                    with col2:
                        st.write(f"**Date:** {deposit['created_at'].strftime('%Y-%m-%d %H:%M')}")
                        st.write(f"**Account:** {deposit['account_number']}")
                        if deposit.get('description'):
                            st.write(f"**Description:** {deposit['description']}")
        else:
            st.info("No savings history found")
            
    except Exception as e:
        st.error(f"Error loading savings history: {e}")

def render_view_section(user_data):
    """Render the view/statements section"""
    st.subheader("📊 View Accounts & Statements")
    
    # View tabs
    view_tab1, view_tab2, view_tab3, view_tab4 = st.tabs([
        "💰 Account Balance", "📄 Account Statement", "📋 Loan Statements", "🛡️ Insurance Statements"
    ])
    
    with view_tab1:
        render_account_balance_section(user_data)
    
    with view_tab2:
        render_account_statement_section(user_data)
    
    with view_tab3:
        render_loan_statements_section(user_data)
    
    with view_tab4:
        render_insurance_statements_section(user_data)
def render_account_balance_section(user_data):
    """Render account balance section"""
    st.markdown("### 💰 Account Balance & Summary")
    
    # Real-time balance
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get current balance
        cursor.execute("""
            SELECT balance, status, created_at, currency
            FROM accounts 
            WHERE user_id = %s
        """, (user_data['user_id'],))
        
        account_info = cursor.fetchone()
        
        # Get today's transactions
        cursor.execute("""
            SELECT COUNT(*) as txn_count, 
                   SUM(CASE WHEN txn_type LIKE '%IN%' OR txn_type = 'DEPOSIT' THEN amount ELSE 0 END) as credits,
                   SUM(CASE WHEN txn_type LIKE '%OUT%' OR txn_type LIKE '%PAYMENT%' OR txn_type LIKE '%TRANSFER%' THEN amount ELSE 0 END) as debits
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = %s AND DATE(t.created_at) = CURDATE()
        """, (user_data['user_id'],))
        
        today_summary = cursor.fetchone()
        
        # Get monthly summary
        cursor.execute("""
            SELECT COUNT(*) as txn_count,
                   SUM(CASE WHEN txn_type LIKE '%IN%' OR txn_type = 'DEPOSIT' THEN amount ELSE 0 END) as credits,
                   SUM(CASE WHEN txn_type LIKE '%OUT%' OR txn_type LIKE '%PAYMENT%' OR txn_type LIKE '%TRANSFER%' THEN amount ELSE 0 END) as debits
            FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.user_id = %s AND MONTH(t.created_at) = MONTH(NOW()) AND YEAR(t.created_at) = YEAR(NOW())
        """, (user_data['user_id'],))
        
        monthly_summary = cursor.fetchone()
        conn.close()
        
        # Display balance information
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Current Balance", f"KES {account_info['balance']:,.2f}")
        col2.metric("Account Status", account_info['status'])
        col3.metric("Currency", account_info['currency'])
        col4.metric("Account Age", f"{(datetime.now() - account_info['created_at']).days} days")
        
        st.markdown("---")
        
        # Today's activity
        st.markdown("#### Today's Activity")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Transactions", today_summary['txn_count'] or 0)
        col2.metric("Money In", f"KES {today_summary['credits'] or 0:,.2f}")
        col3.metric("Money Out", f"KES {today_summary['debits'] or 0:,.2f}")
        
        # Monthly activity
        st.markdown("#### This Month's Activity")
        col1, col2, col3 = st.columns(3)
        
        col1.metric("Transactions", monthly_summary['txn_count'] or 0)
        col2.metric("Money In", f"KES {monthly_summary['credits'] or 0:,.2f}")
        col3.metric("Money Out", f"KES {monthly_summary['debits'] or 0:,.2f}")
        
        # Quick actions
        st.markdown("#### Quick Actions")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔄 Refresh Balance"):
                st.rerun()
        
        with col2:
            if st.button("📧 Email Balance"):
                st.success("Balance sent to your email!")
        
        with col3:
            if st.button("📱 SMS Balance"):
                st.success("Balance sent via SMS!")
        
        with col4:
            if st.button("🖨️ Print Balance"):
                st.success("Balance slip ready for printing!")
        
    except Exception as e:
        st.error(f"Error loading account information: {e}")

def render_account_statement_section(user_data):
    """Render account statement section"""
    st.markdown("### 📄 Account Statement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Generate Statement")
        
        statement_period = st.selectbox("Statement Period", [
            "Last 7 days", "Last 30 days", "Last 3 months", 
            "Last 6 months", "Last 12 months", "Custom Range"
        ])
        
        if statement_period == "Custom Range":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
        
        statement_format = st.selectbox("Format", ["PDF", "Excel", "CSV"])
        
        if st.button("📄 Generate Statement", type="primary"):
            generate_account_statement(user_data, statement_period, statement_format)
    
    with col2:
        st.markdown("#### Recent Transactions")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT t.*, a.account_number
                FROM transactions t
                JOIN accounts a ON t.account_id = a.account_id
                WHERE a.user_id = %s
                ORDER BY t.created_at DESC
                LIMIT 10
            """, (user_data['user_id'],))
            
            recent_txns = cursor.fetchall()
            conn.close()
            
            if recent_txns:
                for txn in recent_txns:
                    # Determine transaction type icon
                    if 'IN' in txn['txn_type'] or txn['txn_type'] == 'DEPOSIT':
                        icon = "📥"
                        color = "success"
                    else:
                        icon = "📤"
                        color = "info"
                    
                    st.write(f"{icon} **{txn['txn_type'].replace('_', ' ').title()}**")
                    st.write(f"KES {txn['amount']:,.2f} - {txn['created_at'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"Ref: {txn['reference_code']}")
                    st.markdown("---")
            else:
                st.info("No recent transactions")
                
        except Exception as e:
            st.error(f"Error loading transactions: {e}")

def generate_account_statement(user_data, period, format_type):
    """Generate account statement"""
    try:
        # Mock statement generation
        st.success(f"✅ {format_type} statement generated successfully!")
        st.info(f"📧 Statement for {period} will be sent to your email within 5 minutes")
        st.info(f"📱 SMS notification sent to confirm statement generation")
        
        # Create downloadable content
        statement_content = f"""
WEKEZA BANK ACCOUNT STATEMENT
Account Number: {user_data['account_number']}
Account Holder: {user_data['full_name']}
Statement Period: {period}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This is a sample statement. The actual statement will be sent to your email.
        """
        
        st.download_button(
            label=f"📥 Download {format_type} Statement",
            data=statement_content,
            file_name=f"statement_{user_data['account_number']}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Statement generation failed: {e}")

def render_loan_statements_section(user_data):
    """Render loan statements section"""
    st.markdown("### 📋 Loan Statements")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user's loans
        cursor.execute("""
            SELECT la.application_id, la.account_number, la.loan_type, la.loan_amount, 
                   la.tenure_months, la.status, la.monthly_payment, la.created_at,
                   la.loan_type as product_name
            FROM loan_applications la
            WHERE la.account_number = %s AND la.status IN ('APPROVED', 'DISBURSED', 'ACTIVE', 'PAID')
            ORDER BY la.created_at DESC
        """, (user_data['account_number'],))
        
        loans = cursor.fetchall()
        conn.close()
        
        if loans:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Select Loan for Statement")
                
                selected_loan = st.selectbox(
                    "Choose Loan",
                    loans,
                    format_func=lambda x: f"{x.get('product_name', x['loan_type'])} - App #{x['application_id']} ({x['status']})"
                )
                
                statement_type = st.selectbox("Statement Type", [
                    "Payment History", "Loan Schedule", "Outstanding Balance", "Full Statement"
                ])
                
                if st.button("📋 Generate Loan Statement", type="primary"):
                    generate_loan_statement(user_data, selected_loan, statement_type)
            
            with col2:
                st.markdown("#### Loan Summary")
                
                if selected_loan:
                    st.write(f"**Product:** {selected_loan.get('product_name', selected_loan['loan_type'])}")
                    st.write(f"**Application ID:** {selected_loan['application_id']}")
                    st.write(f"**Loan Amount:** KES {selected_loan['loan_amount']:,.2f}")
                    st.write(f"**Term:** {selected_loan['tenure_months']} months")
                    st.write(f"**Status:** {selected_loan['status']}")
                    
                    if selected_loan.get('outstanding_balance'):
                        st.write(f"**Outstanding:** KES {selected_loan['outstanding_balance']:,.2f}")
                    
                    if selected_loan.get('monthly_payment'):
                        st.write(f"**Monthly Payment:** KES {selected_loan['monthly_payment']:,.2f}")
        else:
            st.info("No loan history found")
            
    except Exception as e:
        st.error(f"Error loading loan information: {e}")

def generate_loan_statement(user_data, loan, statement_type):
    """Generate loan statement"""
    try:
        st.success(f"✅ {statement_type} generated successfully!")
        st.info(f"📧 Loan statement will be sent to your email within 5 minutes")
        
        # Create downloadable content
        statement_content = f"""
WEKEZA BANK LOAN STATEMENT
Account Holder: {user_data['full_name']}
Loan Product: {loan.get('product_name', loan['loan_type'])}
Application ID: {loan['application_id']}
Statement Type: {statement_type}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Loan Details:
- Principal Amount: KES {loan['loan_amount']:,.2f}
- Term: {loan['tenure_months']} months
- Status: {loan['status']}

This is a sample statement. The actual statement will be sent to your email.
        """
        
        st.download_button(
            label=f"📥 Download {statement_type}",
            data=statement_content,
            file_name=f"loan_statement_{loan['application_id']}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Loan statement generation failed: {e}")

def render_insurance_statements_section(user_data):
    """Render insurance statements section"""
    st.markdown("### 🛡️ Insurance Statements")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Get user's insurance policies
        cursor.execute("""
            SELECT p.*, pr.product_name
            FROM insurance_policies p
            LEFT JOIN insurance_products pr ON p.product_id = pr.product_id
            WHERE p.account_number = %s
            ORDER BY p.created_at DESC
        """, (user_data['account_number'],))
        
        policies = cursor.fetchall()
        conn.close()
        
        if policies:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Select Policy for Statement")
                
                selected_policy = st.selectbox(
                    "Choose Policy",
                    policies,
                    format_func=lambda x: f"{x.get('product_name', 'Insurance')} - {x['policy_number']} ({x['status']})"
                )
                
                statement_type = st.selectbox("Statement Type", [
                    "Premium Payment History", "Policy Certificate", "Claims History", "Full Policy Statement"
                ])
                
                if st.button("🛡️ Generate Insurance Statement", type="primary"):
                    generate_insurance_statement(user_data, selected_policy, statement_type)
            
            with col2:
                st.markdown("#### Policy Summary")
                
                if selected_policy:
                    st.write(f"**Policy Number:** {selected_policy['policy_number']}")
                    st.write(f"**Product:** {selected_policy.get('product_name', 'N/A')}")
                    st.write(f"**Coverage:** KES {selected_policy['coverage_amount']:,.2f}")
                    st.write(f"**Annual Premium:** KES {selected_policy['annual_premium']:,.2f}")
                    st.write(f"**Status:** {selected_policy['status']}")
                    
                    if selected_policy.get('beneficiary_name'):
                        st.write(f"**Beneficiary:** {selected_policy['beneficiary_name']}")
        else:
            st.info("No insurance policies found")
            
    except Exception as e:
        st.error(f"Error loading insurance information: {e}")

def generate_insurance_statement(user_data, policy, statement_type):
    """Generate insurance statement"""
    try:
        st.success(f"✅ {statement_type} generated successfully!")
        st.info(f"📧 Insurance statement will be sent to your email within 5 minutes")
        
        # Create downloadable content
        statement_content = f"""
WEKEZA SALAMA INSURANCE STATEMENT
Policy Holder: {user_data['full_name']}
Policy Number: {policy['policy_number']}
Product: {policy.get('product_name', 'Insurance Policy')}
Statement Type: {statement_type}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Policy Details:
- Coverage Amount: KES {policy['coverage_amount']:,.2f}
- Annual Premium: KES {policy['annual_premium']:,.2f}
- Status: {policy['status']}

This is a sample statement. The actual statement will be sent to your email.
        """
        
        st.download_button(
            label=f"📥 Download {statement_type}",
            data=statement_content,
            file_name=f"insurance_statement_{policy['policy_number']}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )
        
    except Exception as e:
        st.error(f"Insurance statement generation failed: {e}")

def render_settings_section(user_data):
    """Render the settings section"""
    st.subheader("⚙️ Account Settings & Security")
    
    # Settings tabs
    settings_tab1, settings_tab2, settings_tab3, settings_tab4, settings_tab5 = st.tabs([
        "👤 Profile", "🔒 Security", "💳 Cards", "📱 Notifications", "🎯 Preferences"
    ])
    
    with settings_tab1:
        render_profile_settings(user_data)
    
    with settings_tab2:
        render_security_settings(user_data)
    
    with settings_tab3:
        render_card_management(user_data)
    
    with settings_tab4:
        render_notification_settings(user_data)
    
    with settings_tab5:
        render_preferences_settings(user_data)

def render_profile_settings(user_data):
    """Render profile settings"""
    st.markdown("### 👤 Profile Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Personal Details")
        
        with st.form("profile_update"):
            full_name = st.text_input("Full Name", value=user_data['full_name'])
            email = st.text_input("Email Address", value=user_data['email'])
            phone = st.text_input("Phone Number", value=user_data.get('phone_number', ''))
            
            # Address information
            st.markdown("**Address Information**")
            physical_address = st.text_area("Physical Address", placeholder="Enter your physical address")
            postal_address = st.text_input("Postal Address", placeholder="P.O. Box...")
            
            if st.form_submit_button("💾 Update Profile", type="primary"):
                update_profile(user_data, full_name, email, phone, physical_address, postal_address)
    
    with col2:
        st.markdown("#### Account Information")
        
        st.info("**Account Details**")
        st.write(f"**Account Number:** {user_data['account_number']}")
        st.write(f"**Account Status:** {user_data['account_status']}")
        st.write(f"**Customer ID:** {user_data['user_id']}")
        
        if user_data.get('national_id'):
            st.write(f"**National ID:** {user_data['national_id']}")
        
        st.markdown("#### KYC Status")
        st.success("✅ KYC Verified")
        st.write("• Identity verification: Complete")
        st.write("• Address verification: Complete")
        st.write("• Income verification: Complete")
        
        if st.button("📄 Update KYC Documents"):
            st.info("📞 Please visit any Wekeza branch to update your KYC documents")

def update_profile(user_data, name, email, phone, physical_addr, postal_addr):
    """Update user profile"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE users 
            SET full_name = %s, email = %s, phone_number = %s, updated_at = %s
            WHERE user_id = %s
        """, (name, email, phone, datetime.now(), user_data['user_id']))
        
        conn.commit()
        conn.close()
        
        st.success("✅ Profile updated successfully!")
        st.info("🔄 Please refresh the page to see changes")
        
    except Exception as e:
        st.error(f"❌ Profile update failed: {e}")

def render_security_settings(user_data):
    """Render security settings"""
    st.markdown("### 🔒 Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Change Password")
        
        with st.form("change_password"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔒 Change Password", type="primary"):
                if new_password == confirm_password:
                    change_password(user_data, current_password, new_password)
                else:
                    st.error("New passwords don't match!")
        
        st.markdown("#### Two-Factor Authentication")
        
        tfa_enabled = st.checkbox("Enable SMS Two-Factor Authentication", value=False)
        
        if tfa_enabled:
            st.success("✅ Two-factor authentication will be enabled")
            st.info("📱 You will receive SMS codes for login verification")
        
        if st.button("💾 Update Security Settings"):
            st.success("✅ Security settings updated!")
    
    with col2:
        st.markdown("#### Security Status")
        
        st.info("**Current Security Level: Medium**")
        
        security_items = [
            ("Password Protection", "✅", "Active"),
            ("Email Verification", "✅", "Verified"),
            ("Phone Verification", "✅", "Verified"),
            ("Two-Factor Auth", "❌", "Disabled"),
            ("Login Notifications", "✅", "Enabled")
        ]
        
        for item, status, description in security_items:
            st.write(f"{status} **{item}:** {description}")
        
        st.markdown("#### Recent Login Activity")
        
        login_history = [
            {"date": "2026-01-04 14:30", "device": "Chrome Browser", "location": "Nairobi, Kenya"},
            {"date": "2026-01-03 09:15", "device": "Mobile App", "location": "Nairobi, Kenya"},
            {"date": "2026-01-02 16:45", "device": "Chrome Browser", "location": "Nairobi, Kenya"}
        ]
        
        for login in login_history:
            st.write(f"📅 {login['date']}")
            st.write(f"💻 {login['device']} - {login['location']}")
            st.markdown("---")

def change_password(user_data, current_password, new_password):
    """Change user password"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Verify current password
        cursor.execute("SELECT password_hash FROM users WHERE user_id = %s", (user_data['user_id'],))
        user = cursor.fetchone()
        
        if user and user['password_hash'] == current_password:
            # Update password
            cursor.execute("""
                UPDATE users SET password_hash = %s, updated_at = %s WHERE user_id = %s
            """, (new_password, datetime.now(), user_data['user_id']))
            
            conn.commit()
            conn.close()
            
            st.success("✅ Password changed successfully!")
            st.info("🔐 Please use your new password for future logins")
        else:
            st.error("❌ Current password is incorrect!")
            
    except Exception as e:
        st.error(f"❌ Password change failed: {e}")

def render_card_management(user_data):
    """Render card management section"""
    st.markdown("### 💳 Card Management")
    
    # Mock card data
    cards = [
        {
            "card_number": "**** **** **** 1234",
            "card_type": "Debit Card",
            "status": "Active",
            "expiry": "12/28",
            "daily_limit": 50000
        },
        {
            "card_number": "**** **** **** 5678", 
            "card_type": "Credit Card",
            "status": "Active",
            "expiry": "06/27",
            "daily_limit": 100000
        }
    ]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### My Cards")
        
        for card in cards:
            with st.expander(f"💳 {card['card_type']} - {card['card_number']}"):
                st.write(f"**Type:** {card['card_type']}")
                st.write(f"**Status:** {card['status']}")
                st.write(f"**Expiry:** {card['expiry']}")
                st.write(f"**Daily Limit:** KES {card['daily_limit']:,}")
                
                col1a, col2a, col3a = st.columns(3)
                
                with col1a:
                    if st.button(f"🔒 Block Card", key=f"block_{card['card_number']}"):
                        block_card(card)
                
                with col2a:
                    if st.button(f"📱 Get PIN", key=f"pin_{card['card_number']}"):
                        request_pin(card)
                
                with col3a:
                    if st.button(f"⚙️ Set Limits", key=f"limits_{card['card_number']}"):
                        st.session_state[f'show_limits_{card["card_number"]}'] = True
    
    with col2:
        st.markdown("#### Card Services")
        
        if st.button("💳 Request New Card", type="primary"):
            st.success("✅ New card request submitted!")
            st.info("📦 Your new card will be delivered within 5-7 business days")
        
        if st.button("🔄 Replace Lost Card"):
            st.success("✅ Card replacement request submitted!")
            st.info("💰 Replacement fee: KES 500")
            st.info("📦 New card will be delivered within 3-5 business days")
        
        if st.button("📊 Card Statement"):
            st.success("✅ Card statement generated!")
            st.info("📧 Statement will be sent to your email")
        
        st.markdown("#### Emergency Services")
        
        st.error("🚨 **Lost/Stolen Card?**")
        st.write("Call our 24/7 hotline immediately:")
        st.write("📞 **+254 700 123 456**")
        
        if st.button("🚨 Report Lost Card", type="secondary"):
            st.success("✅ Card blocked immediately for security!")
            st.info("📞 Our team will contact you within 30 minutes")

def block_card(card):
    """Block a card"""
    st.success(f"✅ {card['card_type']} {card['card_number']} has been blocked!")
    st.info("🔒 Card is now inactive for all transactions")
    st.info("📞 Contact customer service to unblock: +254 700 123 456")

def request_pin(card):
    """Request PIN for card"""
    st.success(f"✅ PIN request submitted for {card['card_type']} {card['card_number']}")
    st.info("📱 PIN will be sent to your registered mobile number within 5 minutes")

def render_notification_settings(user_data):
    """Render notification settings"""
    st.markdown("### 📱 Notification Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### SMS Notifications")
        
        sms_balance = st.checkbox("Balance inquiries", value=True)
        sms_transactions = st.checkbox("Transaction alerts", value=True)
        sms_loans = st.checkbox("Loan payment reminders", value=True)
        sms_insurance = st.checkbox("Insurance premium reminders", value=True)
        sms_security = st.checkbox("Security alerts", value=True)
        
        st.markdown("#### Email Notifications")
        
        email_statements = st.checkbox("Monthly statements", value=True)
        email_promotions = st.checkbox("Product promotions", value=False)
        email_news = st.checkbox("Bank news & updates", value=True)
        email_security = st.checkbox("Security notifications", value=True)
    
    with col2:
        st.markdown("#### Push Notifications")
        
        push_transactions = st.checkbox("Transaction notifications", value=True)
        push_balance = st.checkbox("Low balance alerts", value=True)
        push_payments = st.checkbox("Payment due reminders", value=True)
        push_offers = st.checkbox("Special offers", value=False)
        
        st.markdown("#### Notification Timing")
        
        notification_time = st.selectbox("Preferred time for reminders", [
            "Morning (8:00 AM)", "Afternoon (2:00 PM)", "Evening (6:00 PM)"
        ])
        
        weekend_notifications = st.checkbox("Receive notifications on weekends", value=True)
    
    if st.button("💾 Save Notification Settings", type="primary"):
        st.success("✅ Notification preferences updated!")
        st.info("📱 Changes will take effect immediately")

def render_preferences_settings(user_data):
    """Render preferences settings"""
    st.markdown("### 🎯 Account Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Display Preferences")
        
        language = st.selectbox("Language", ["English", "Kiswahili"])
        currency_display = st.selectbox("Currency Display", ["KES (Kenyan Shilling)", "USD (US Dollar)"])
        date_format = st.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        
        st.markdown("#### Transaction Preferences")
        
        default_transfer_limit = st.number_input("Daily Transfer Limit (KES)", min_value=1000.0, max_value=1000000.0, value=100000.0)
        auto_save = st.checkbox("Auto-save to savings goals", value=False)
        
        if auto_save:
            auto_save_percentage = st.slider("Auto-save percentage", 1, 20, 5)
            st.info(f"💰 {auto_save_percentage}% of deposits will be automatically saved")
    
    with col2:
        st.markdown("#### Privacy Settings")
        
        profile_visibility = st.selectbox("Profile Visibility", ["Private", "Limited", "Public"])
        transaction_history = st.selectbox("Transaction History Retention", ["1 year", "2 years", "5 years"])
        
        st.markdown("#### Marketing Preferences")
        
        marketing_emails = st.checkbox("Receive marketing emails", value=False)
        sms_marketing = st.checkbox("Receive promotional SMS", value=False)
        call_marketing = st.checkbox("Allow marketing calls", value=False)
        
        st.markdown("#### Data & Analytics")
        
        usage_analytics = st.checkbox("Share usage analytics (helps improve services)", value=True)
        personalized_offers = st.checkbox("Receive personalized offers", value=True)
    
    if st.button("💾 Save Preferences", type="primary"):
        st.success("✅ Preferences updated successfully!")
        st.info("🔄 Some changes may require app restart to take effect")

# Import necessary modules for the main app
import streamlit as st
import mysql.connector
from datetime import datetime
import uuid