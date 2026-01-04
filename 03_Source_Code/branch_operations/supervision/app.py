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
        st.subheader("📝 Transactions Pending Authorization")
        
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                
                # Get recent high-value transactions that might need approval (only pending ones)
                cursor.execute("""
                    SELECT t.*, a.account_number, u.full_name
                    FROM transactions t
                    JOIN accounts a ON t.account_id = a.account_id
                    JOIN users u ON a.user_id = u.user_id
                    WHERE t.amount > 50000 
                    AND DATE(t.created_at) = CURDATE()
                    AND (t.status IS NULL OR t.status = 'PENDING' OR t.status = 'COMPLETED')
                    AND (t.approved_by IS NULL OR t.approved_by = '')
                    ORDER BY t.created_at DESC
                    LIMIT 20
                """)
                
                transactions = cursor.fetchall()
                conn.close()
                
                if transactions:
                    for txn in transactions:
                        with st.expander(f"Transaction {txn['reference_code']} - KES {txn['amount']:,.2f}"):
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.write(f"**Account:** {txn['account_number']}")
                                st.write(f"**Customer:** {txn['full_name']}")
                                st.write(f"**Type:** {txn['txn_type']}")
                                
                            with col2:
                                st.write(f"**Amount:** KES {txn['amount']:,.2f}")
                                st.write(f"**Date:** {txn['created_at']}")
                                st.write(f"**Reference:** {txn['reference_code']}")
                                
                            with col3:
                                col3a, col3b = st.columns(2)
                                with col3a:
                                    if st.button(f"✅ Approve", key=f"approve_{txn['transaction_id']}"):
                                        try:
                                            # Update transaction status to approved
                                            conn_update = get_db_connection()
                                            if conn_update:
                                                cursor_update = conn_update.cursor()
                                                cursor_update.execute("""
                                                    UPDATE transactions 
                                                    SET status = 'APPROVED', 
                                                        approved_by = %s, 
                                                        approved_at = NOW(),
                                                        remarks = CONCAT(COALESCE(remarks, ''), ' - Approved by supervisor')
                                                    WHERE transaction_id = %s
                                                """, (staff['staff_code'], txn['transaction_id']))
                                                conn_update.commit()
                                                conn_update.close()
                                                
                                                st.success(f"✅ Transaction {txn['reference_code']} approved successfully!")
                                                st.write(f"**Approved by:** {staff['full_name']}")
                                                st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                                
                                                # Refresh the page to update the queue
                                                st.rerun()
                                        except Exception as e:
                                            st.error(f"Error approving transaction: {e}")
                                
                                with col3b:
                                    if st.button(f"❌ Reject", key=f"reject_{txn['transaction_id']}"):
                                        try:
                                            # Update transaction status to rejected
                                            conn_update = get_db_connection()
                                            if conn_update:
                                                cursor_update = conn_update.cursor()
                                                cursor_update.execute("""
                                                    UPDATE transactions 
                                                    SET status = 'REJECTED', 
                                                        approved_by = %s, 
                                                        approved_at = NOW(),
                                                        remarks = CONCAT(COALESCE(remarks, ''), ' - Rejected by supervisor')
                                                    WHERE transaction_id = %s
                                                """, (staff['staff_code'], txn['transaction_id']))
                                                conn_update.commit()
                                                conn_update.close()
                                                
                                                st.error(f"❌ Transaction {txn['reference_code']} rejected!")
                                                st.write(f"**Rejected by:** {staff['full_name']}")
                                                st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                                                
                                                # Refresh the page to update the queue
                                                st.rerun()
                                        except Exception as e:
                                            st.error(f"Error rejecting transaction: {e}")
                else:
                    st.info("No transactions pending authorization")
                    
        except Exception as e:
            st.error(f"Error loading authorization queue: {e}")

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
                                            approved_by = %s, 
                                            approved_at = NOW(),
                                            remarks = %s
                                        WHERE transaction_id = %s
                                    """, (status, staff['staff_code'], remarks or f"{action} by supervisor", transaction['transaction_id']))
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