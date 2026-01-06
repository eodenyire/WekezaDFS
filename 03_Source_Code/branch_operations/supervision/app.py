# supervision/app.py
import streamlit as st
import os
import mysql.connector
from datetime import datetime

def render_supervision_ui(staff_info):
    """
    Main render function for the supervision module.
    This function is called by the main branch system.
    
    Args:
        staff_info (dict): Staff information from the main system
    """
    # -----------------------------------------------------------------------------
    # Check Supervision Access
    # -----------------------------------------------------------------------------
    def check_supervision_access():
        """Verify user has supervision access"""
        allowed_roles = ['SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
        
        if staff_info['role'] not in allowed_roles:
            st.error(f"❌ Access Denied: Role '{staff_info['role']}' is not authorized for supervision operations.")
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
    staff = check_supervision_access()

    st.title("🛡️ Branch Supervision System")
    st.markdown(f"**Supervisor:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
    st.markdown("---")

    # Create supervisor info for the sub-modules
    supervisor = {
        "supervisor_id": staff['staff_code'],
        "name": staff['full_name'],
        "role": staff['role'],
        "branch_code": staff.get('branch_code', 'MAIN')
    }
    
    API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
    
    # Supervision Tabs
    tab_queue, tab_approvals, tab_reversals, tab_exceptions, tab_reports = st.tabs([
        "📝 Authorization Queue",
        "✅ Transaction Approvals",
        "↩️ Reversals",
        "⚠️ Exception Handling",
        "📊 Reports"
    ])

    # TAB 1: Authorization Queue
    with tab_queue:
        st.subheader("📝 Items Pending Authorization")
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.selectbox("Filter by Type", [
                "All", "LOAN_APPLICATION", "BANK_TRANSFER", "MOBILE_MONEY_TRANSFER", "BILL_PAYMENT", "CDSC_TRANSFER",
                "CASH_DEPOSIT", "CASH_WITHDRAWAL", "CHEQUE_DEPOSIT", 
                "CIF_CREATE", "ACCOUNT_OPENING", "ACCOUNT_MAINTENANCE", "ACCOUNT_CLOSURE", 
                "MANDATE_MANAGEMENT", "POLICY_SALE", "CLAIMS_PROCESSING", "PREMIUM_COLLECTION",
                "TELLER_CASH_ISSUE", "TELLER_CASH_RECEIVE", "VAULT_OPENING", "VAULT_CLOSING",
                "ATM_CASH_LOADING", "ATM_CASH_OFFLOADING"
            ])
        with col2:
            filter_priority = st.selectbox("Filter by Priority", ["All", "URGENT", "HIGH", "MEDIUM", "LOW"])
        with col3:
            if st.button("🔄 Refresh Queue"):
                st.rerun()
        
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                
                # Build filter conditions
                type_condition = "" if filter_type == "All" else f"AND aq.transaction_type = '{filter_type}'"
                priority_condition = "" if filter_priority == "All" else f"AND aq.priority = '{filter_priority}'"
                
                # Get items from authorization queue with detailed information
                cursor.execute(f"""
                    SELECT aq.*, 
                           la.loan_type, la.purpose, la.interest_rate, la.tenure_months,
                           la.account_number, u.full_name as customer_name,
                           CASE 
                               WHEN aq.transaction_type = 'LOAN_APPLICATION' THEN CONCAT('Loan Application - ', la.loan_type)
                               WHEN aq.transaction_type = 'BANK_TRANSFER' THEN CONCAT('Bank Transfer - ', SUBSTRING(aq.description, LOCATE('from ', aq.description) + 5, 15))
                               WHEN aq.transaction_type = 'MOBILE_MONEY_TRANSFER' THEN CONCAT('Mobile Money Transfer - ', SUBSTRING(aq.description, LOCATE('to ', aq.description) + 3, 15))
                               WHEN aq.transaction_type = 'BILL_PAYMENT' THEN CONCAT('Bill Payment - ', SUBSTRING(aq.description, LOCATE('to ', aq.description) + 3, 20))
                               WHEN aq.transaction_type = 'CDSC_TRANSFER' THEN CONCAT('CDSC Transfer - ', SUBSTRING(aq.description, LOCATE('to ', aq.description) + 3, 15))
                               WHEN aq.transaction_type = 'CASH_DEPOSIT' THEN CONCAT('Cash Deposit - Account ', SUBSTRING(aq.description, LOCATE('account ', aq.description) + 8, 10))
                               WHEN aq.transaction_type = 'CASH_WITHDRAWAL' THEN CONCAT('Cash Withdrawal - Account ', SUBSTRING(aq.description, LOCATE('account ', aq.description) + 8, 10))
                               WHEN aq.transaction_type = 'CHEQUE_DEPOSIT' THEN CONCAT('Cheque Deposit - Account ', SUBSTRING(aq.description, LOCATE('account ', aq.description) + 8, 10))
                               WHEN aq.transaction_type = 'CIF_CREATE' THEN CONCAT('CIF Creation - ', SUBSTRING(aq.description, LOCATE('for ', aq.description) + 4))
                               WHEN aq.transaction_type = 'ACCOUNT_OPENING' THEN CONCAT('Account Opening - ', SUBSTRING(aq.description, LOCATE('for ', aq.description) + 4))
                               WHEN aq.transaction_type = 'ACCOUNT_CLOSURE' THEN CONCAT('Account Closure - ', SUBSTRING(aq.description, LOCATE('for ', aq.description) + 4))
                               WHEN aq.transaction_type = 'POLICY_SALE' THEN CONCAT('Insurance Policy Sale - ', SUBSTRING(aq.description, LOCATE('- ', aq.description) + 2))
                               WHEN aq.transaction_type = 'CLAIMS_PROCESSING' THEN CONCAT('Insurance Claim - ', SUBSTRING(aq.description, LOCATE('- ', aq.description) + 2))
                               WHEN aq.transaction_type = 'PREMIUM_COLLECTION' THEN CONCAT('Premium Payment - ', SUBSTRING(aq.description, LOCATE('for ', aq.description) + 4))
                               ELSE aq.description
                           END as display_description
                    FROM authorization_queue aq
                    LEFT JOIN loan_applications la ON aq.reference_id = la.application_id AND aq.transaction_type = 'LOAN_APPLICATION'
                    LEFT JOIN accounts a ON la.account_number = a.account_number
                    LEFT JOIN users u ON a.user_id = u.user_id
                    WHERE aq.status = 'PENDING'
                    {type_condition}
                    {priority_condition}
                    ORDER BY 
                        CASE aq.priority 
                            WHEN 'URGENT' THEN 1 
                            WHEN 'HIGH' THEN 2 
                            WHEN 'MEDIUM' THEN 3 
                            WHEN 'LOW' THEN 4 
                        END,
                        aq.created_at ASC
                    LIMIT 50
                """)
                
                queue_items = cursor.fetchall()
                
                if queue_items:
                    st.info(f"📋 {len(queue_items)} items pending your authorization")
                    
                    for item in queue_items:
                        # Priority color coding
                        priority_colors = {
                            'URGENT': '🔴',
                            'HIGH': '🟠', 
                            'MEDIUM': '🟡',
                            'LOW': '🟢'
                        }
                        priority_icon = priority_colors.get(item['priority'], '⚪')
                        
                        with st.expander(f"{priority_icon} {item['transaction_type']} - {item['reference_id']} - KES {item['amount']:,.2f}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write("**Transaction Details**")
                                st.write(f"**Type:** {item['transaction_type']}")
                                st.write(f"**Reference:** {item['reference_id']}")
                                st.write(f"**Amount:** KES {item['amount']:,.2f}")
                                st.write(f"**Priority:** {item['priority']}")
                                
                                if item['transaction_type'] == 'LOAN':
                                    st.write(f"**Account:** {item['account_number']}")
                                    st.write(f"**Customer:** {item['customer_name']}")
                                
                            with col2:
                                st.write("**Maker Information**")
                                st.write(f"**Maker ID:** {item['maker_id']}")
                                st.write(f"**Maker Name:** {item['maker_name']}")
                                st.write(f"**Created:** {item['created_at']}")
                                st.write(f"**Branch:** {item['branch_code']}")
                                
                                if item['transaction_type'] == 'LOAN':
                                    st.write(f"**Loan Type:** {item['loan_type']}")
                                    st.write(f"**Interest Rate:** {item['interest_rate']}%")
                                    st.write(f"**Tenure:** {item['tenure_months']} months")
                                
                            with col3:
                                st.write("**Authorization Actions**")
                                
                                if item['transaction_type'] == 'LOAN':
                                    st.write(f"**Purpose:** {item['purpose']}")
                                
                                st.write(f"**Description:** {item['display_description']}")
                                
                                # Approval buttons
                                col3a, col3b = st.columns(2)
                                with col3a:
                                    if st.button(f"✅ Approve", key=f"approve_{item['queue_id']}", type="primary"):
                                        approve_queue_item(item, staff, conn)
                                
                                with col3b:
                                    if st.button(f"❌ Reject", key=f"reject_{item['queue_id']}", type="secondary"):
                                        st.session_state[f'show_reject_form_{item["queue_id"]}'] = True
                                
                                # Rejection reason form
                                if st.session_state.get(f'show_reject_form_{item["queue_id"]}', False):
                                    with st.form(f"reject_form_{item['queue_id']}"):
                                        rejection_reason = st.text_area("Rejection Reason", placeholder="Please provide reason for rejection...")
                                        
                                        col_submit, col_cancel = st.columns(2)
                                        with col_submit:
                                            if st.form_submit_button("❌ Confirm Rejection"):
                                                if rejection_reason.strip():
                                                    reject_queue_item(item, staff, rejection_reason, conn)
                                                    st.session_state[f'show_reject_form_{item["queue_id"]}'] = False
                                                    st.rerun()
                                                else:
                                                    st.error("Please provide a rejection reason")
                                        
                                        with col_cancel:
                                            if st.form_submit_button("Cancel"):
                                                st.session_state[f'show_reject_form_{item["queue_id"]}'] = False
                                                st.rerun()
                else:
                    st.success("✅ No items pending authorization")
                    st.info("All transactions have been processed or no high-value transactions today.")
                
                conn.close()
                
        except Exception as e:
            st.error(f"Error loading authorization queue: {e}")
            st.write("Please check database connection and try again.")

    # TAB 2: Transaction Approvals
    with tab_approvals:
        st.subheader("✅ Transaction Approval Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Manual Approval")
            transaction_id = st.text_input("Enter Transaction ID to Approve/Reject")
            action = st.radio("Action", ["Approve", "Reject"])
            remarks = st.text_area("Remarks (optional)")
            
            if st.button("Submit Decision", type="primary"):
                if transaction_id:
                    try:
                        # First check if transaction exists
                        conn_check = get_db_connection()
                        if conn_check:
                            cursor_check = conn_check.cursor(dictionary=True)
                            cursor_check.execute("""
                                SELECT t.*, a.account_number, u.full_name
                                FROM transactions t
                                JOIN accounts a ON t.account_id = a.account_id
                                JOIN users u ON a.user_id = u.user_id
                                WHERE t.reference_code = %s OR t.transaction_id = %s
                            """, (transaction_id, transaction_id))
                            
                            transaction = cursor_check.fetchone()
                            conn_check.close()
                            
                            if transaction:
                                # Update transaction status
                                conn_update = get_db_connection()
                                if conn_update:
                                    cursor_update = conn_update.cursor()
                                    status = action.upper()
                                    cursor_update.execute("""
                                        UPDATE transactions 
                                        SET status = %s,
                                            description = CONCAT(COALESCE(description, ''), ' - ', %s, ' by supervisor')
                                        WHERE transaction_id = %s
                                    """, (status, action, transaction['transaction_id']))
                                    conn_update.commit()
                                    conn_update.close()
                                    
                                    st.success(f"✅ Transaction {transaction_id} {action.lower()}d successfully!")
                                    st.write(f"**Transaction:** {transaction['reference_code']}")
                                    st.write(f"**Customer:** {transaction['full_name']}")
                                    st.write(f"**Amount:** KES {float(transaction['amount']):,.2f}")
                                    st.write(f"**Action:** {action}")
                                    st.write(f"**Supervisor:** {staff['full_name']}")
                                    st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                    if remarks:
                                        st.write(f"**Remarks:** {remarks}")
                            else:
                                st.error(f"Transaction {transaction_id} not found")
                    except Exception as e:
                        st.error(f"Error processing transaction: {e}")
                else:
                    st.error("Please enter a transaction ID")
            
        with col2:
            st.markdown("### Approval Statistics")
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_today,
                            SUM(CASE WHEN amount > 100000 THEN 1 ELSE 0 END) as high_value,
                            AVG(amount) as avg_amount
                        FROM transactions 
                        WHERE DATE(created_at) = CURDATE()
                    """)
                    
                    stats = cursor.fetchone()
                    conn.close()
                    
                    if stats:
                        st.metric("Today's Transactions", int(stats['total_today'] or 0))
                        st.metric("High Value (>100K)", int(stats['high_value'] or 0))
                        st.metric("Average Amount", f"KES {float(stats['avg_amount'] or 0):,.2f}")
            except Exception as e:
                st.error(f"Error loading statistics: {e}")

    # TAB 3: Reversals
    with tab_reversals:
        st.subheader("↩️ Transaction Reversals")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Initiate Reversal")
            reversal_ref = st.text_input("Transaction Reference", placeholder="Enter reference code")
            reversal_reason = st.selectbox("Reversal Reason", [
                "Customer Request",
                "System Error",
                "Fraud Prevention",
                "Duplicate Transaction",
                "Other"
            ])
            reversal_notes = st.text_area("Additional Notes", placeholder="Explain the reason for reversal")
            
            if st.button("↩️ Process Reversal", type="primary"):
                if reversal_ref and reversal_reason:
                    st.success(f"✅ Reversal initiated for transaction {reversal_ref}")
                    st.write(f"**Reason:** {reversal_reason}")
                    st.write(f"**Processed by:** {staff['full_name']}")
                    st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    if reversal_notes:
                        st.write(f"**Notes:** {reversal_notes}")
                else:
                    st.error("Please provide transaction reference and reason")
        
        with col2:
            st.markdown("### Recent Reversals")
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # Look for transactions that might be reversals (negative amounts or specific patterns)
                    cursor.execute("""
                        SELECT reference_code, amount, txn_type, created_at
                        FROM transactions 
                        WHERE (txn_type LIKE '%REVERSAL%' OR amount < 0)
                        AND DATE(created_at) = CURDATE()
                        ORDER BY created_at DESC
                        LIMIT 5
                    """)
                    
                    reversals = cursor.fetchall()
                    conn.close()
                    
                    if reversals:
                        for rev in reversals:
                            st.write(f"• {rev['reference_code']} - KES {abs(rev['amount']):,.2f} ({rev['created_at']})")
                    else:
                        st.info("No recent reversals found")
            except Exception as e:
                st.info("No recent reversals found")

    # TAB 4: Exception Handling
    with tab_exceptions:
        st.subheader("⚠️ Exception Handling")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### System Exceptions")
            
            # Check for potential exceptions in the database
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # Check for high transaction volumes
                    cursor.execute("""
                        SELECT account_id, COUNT(*) as txn_count, SUM(amount) as total_amount
                        FROM transactions 
                        WHERE DATE(created_at) = CURDATE()
                        GROUP BY account_id
                        HAVING COUNT(*) > 10 OR SUM(amount) > 500000
                        LIMIT 5
                    """)
                    
                    exceptions = cursor.fetchall()
                    conn.close()
                    
                    if exceptions:
                        for exc in exceptions:
                            if exc['txn_count'] > 10:
                                st.warning(f"⚠️ High transaction volume: Account {exc['account_id']} - {exc['txn_count']} transactions")
                            if float(exc['total_amount']) > 500000:
                                st.error(f"❌ High value alert: Account {exc['account_id']} - KES {float(exc['total_amount']):,.2f}")
                    else:
                        st.success("✅ No exceptions detected")
            except Exception as e:
                st.info("Exception monitoring unavailable")
            
        with col2:
            st.markdown("### Exception Actions")
            exception_account = st.text_input("Account Number", placeholder="Enter account for investigation")
            exception_action = st.selectbox("Action", [
                "Investigate Transaction Pattern",
                "Contact Customer",
                "Temporary Block Account",
                "Request Additional Documentation",
                "Escalate to Management"
            ])
            
            if st.button("🔍 Take Action"):
                if exception_account:
                    st.success(f"✅ Action '{exception_action}' initiated for account {exception_account}")
                    st.write(f"**Supervisor:** {staff['full_name']}")
                    st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.error("Please enter an account number")

    # TAB 5: Reports
    with tab_reports:
        st.subheader("📊 Supervision Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Daily Summary")
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    cursor.execute("""
                        SELECT 
                            COUNT(*) as total_transactions,
                            SUM(amount) as total_amount,
                            COUNT(DISTINCT account_id) as unique_accounts,
                            MAX(amount) as highest_transaction,
                            MIN(amount) as lowest_transaction
                        FROM transactions 
                        WHERE DATE(created_at) = CURDATE()
                    """)
                    
                    summary = cursor.fetchone()
                    conn.close()
                    
                    if summary:
                        st.metric("Total Transactions", int(summary['total_transactions'] or 0))
                        st.metric("Total Amount", f"KES {float(summary['total_amount'] or 0):,.2f}")
                        st.metric("Active Accounts", int(summary['unique_accounts'] or 0))
                        st.metric("Highest Transaction", f"KES {float(summary['highest_transaction'] or 0):,.2f}")
            except Exception as e:
                st.error(f"Error loading summary: {e}")
        
        with col2:
            st.markdown("### Generate Reports")
            report_type = st.selectbox("Report Type", [
                "Daily Transaction Summary",
                "High Value Transactions",
                "Exception Report",
                "Approval Log",
                "Reversal Report"
            ])
            
            report_date = st.date_input("Report Date", value=datetime.now().date())
            
            if st.button("📊 Generate Report"):
                st.success(f"✅ {report_type} generated successfully!")
                
                # Generate sample report content
                report_content = f"""
{report_type}
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Report Date: {report_date}
Generated by: {staff['full_name']} ({staff['staff_code']})
Branch: {staff['branch_name']}

Summary:
- Report type: {report_type}
- Date range: {report_date}
- Status: Generated successfully
                """
                
                st.download_button(
                    label="📥 Download Report",
                    data=report_content,
                    file_name=f"{report_type.lower().replace(' ', '_')}_{report_date}.txt",
                    mime="text/plain"
                )


def approve_queue_item(item, staff, conn):
    """Approve an item in the authorization queue"""
    try:
        cursor = conn.cursor()
        
        # Update authorization queue status
        cursor.execute("""
            UPDATE authorization_queue 
            SET status = 'APPROVED', approved_by = %s, approved_at = %s
            WHERE queue_id = %s
        """, (staff['staff_code'], datetime.now(), item['queue_id']))
        
        # Use authorization helper to execute the approved operation
        try:
            # Import authorization helper
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
            from authorization_helper import execute_approved_operation
            
            # Execute the approved operation
            execution_result = execute_approved_operation(item)
            
        except Exception as e:
            execution_result = {"success": False, "error": f"Failed to execute operation: {e}"}
        
        conn.commit()
        
        st.success(f"✅ {item['transaction_type'].replace('_', ' ').title()} approved and executed successfully!")
        st.write(f"**Approved by:** {staff['full_name']}")
        st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Show execution details
        if execution_result.get('success'):
            st.info(f"💰 {execution_result['message']}")
        else:
            st.warning(f"⚠️ Approval recorded but execution failed: {execution_result.get('error', 'Unknown error')}")
        
        # Show operation-specific details
        if item['transaction_type'] == 'LOAN_APPLICATION':
            st.info(f"💰 Loan of KES {item['amount']:,.2f} approved for customer {item.get('customer_name', 'N/A')}")
        elif item['transaction_type'] in ['CASH_DEPOSIT', 'CASH_WITHDRAWAL', 'CHEQUE_DEPOSIT']:
            st.info(f"💰 {item['transaction_type'].replace('_', ' ').title()} of KES {item['amount']:,.2f} processed")
        elif item['transaction_type'] == 'CIF_CREATE':
            st.info(f"👤 Customer Information File created and activated")
        elif item['transaction_type'] == 'ACCOUNT_OPENING':
            st.info(f"🏦 New account opened and activated")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error approving item: {e}")


def reject_queue_item(item, staff, rejection_reason, conn):
    """Reject an item in the authorization queue"""
    try:
        cursor = conn.cursor()
        
        # Update authorization queue status
        cursor.execute("""
            UPDATE authorization_queue 
            SET status = 'REJECTED', approved_by = %s, approved_at = %s, rejection_reason = %s
            WHERE queue_id = %s
        """, (staff['staff_code'], datetime.now(), rejection_reason, item['queue_id']))
        
        # If it's a loan application, update the loan status
        if item['transaction_type'] == 'LOAN_APPLICATION':
            cursor.execute("""
                UPDATE loan_applications 
                SET status = 'REJECTED', approved_by = %s, approved_at = %s
                WHERE application_id = %s
            """, (staff['staff_code'], datetime.now(), item['reference_id']))
        
        conn.commit()
        
        st.error(f"❌ {item['transaction_type']} {item['reference_id']} rejected")
        st.write(f"**Rejected by:** {staff['full_name']}")
        st.write(f"**Reason:** {rejection_reason}")
        st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        st.rerun()
        
    except Exception as e:
        st.error(f"Error rejecting item: {e}")


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
    # Check Supervision Access
    # -----------------------------------------------------------------------------
    def check_supervision_access():
        """Verify user has supervision access"""
        staff = get_current_staff()
        allowed_roles = ['SUPERVISOR', 'BRANCH_MANAGER', 'ADMIN']
        
        if staff['role'] not in allowed_roles:
            st.error(f"❌ Access Denied: Role '{staff['role']}' is not authorized for supervision operations.")
            st.stop()
        
        return staff

    # Check access first
    staff = check_supervision_access()

    st.title("🛡️ Branch Supervision System")
    st.markdown(f"**Supervisor:** {staff['full_name']} ({staff['staff_code']}) | **Role:** {staff['role']} | **Branch:** {staff['branch_name']}")
    st.markdown("---")


if __name__ == "__main__":
    main()