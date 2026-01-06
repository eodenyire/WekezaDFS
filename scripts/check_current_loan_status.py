#!/usr/bin/env python3

import mysql.connector
from datetime import datetime, timedelta

def check_current_loan_status():
    """Check the actual current status of loans for ACC1000014"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking ACTUAL database status for ACC1000014...")
        
        # Check ALL loan applications for this account
        print("\n📋 ALL Loan Applications for ACC1000014:")
        cursor.execute("""
            SELECT application_id, loan_type, loan_amount, status, created_at, created_by
            FROM loan_applications 
            WHERE account_number = 'ACC1000014'
            ORDER BY created_at DESC
        """)
        
        all_loans = cursor.fetchall()
        if all_loans:
            for loan in all_loans:
                print(f"  - {loan['application_id']}: {loan['loan_type']} - KES {loan['loan_amount']:,.2f} - {loan['status']} - {loan['created_at']}")
        else:
            print("  - No loan applications found in loan_applications table")
        
        # Check ALL authorization queue entries for this user
        print(f"\n📋 ALL Authorization Queue Entries (last 24 hours):")
        cursor.execute("""
            SELECT queue_id, transaction_type, reference_id, amount, status, created_at, maker_name
            FROM authorization_queue 
            WHERE (maker_id LIKE '%14%' OR maker_name LIKE '%Emmanuel%' OR reference_id LIKE '%014%')
            AND created_at >= %s
            ORDER BY created_at DESC
        """, (datetime.now() - timedelta(hours=24),))
        
        queue_entries = cursor.fetchall()
        if queue_entries:
            for entry in queue_entries:
                print(f"  - {entry['queue_id']}: {entry['transaction_type']} - {entry['reference_id']} - KES {entry['amount']:,.2f} - {entry['status']} - {entry['created_at']}")
        else:
            print("  - No recent queue entries found")
        
        # Check specifically for the Queue ID shown in the screenshot
        print(f"\n🔍 Checking specific Queue ID from screenshot: AQ20260104104014")
        cursor.execute("SELECT * FROM authorization_queue WHERE queue_id = %s", ('AQ20260104104014',))
        specific_queue = cursor.fetchone()
        
        if specific_queue:
            print(f"✅ Found: {specific_queue['queue_id']} - {specific_queue['transaction_type']} - Status: {specific_queue['status']}")
            print(f"   Reference: {specific_queue['reference_id']} - Amount: KES {specific_queue['amount']:,.2f}")
            print(f"   Created: {specific_queue['created_at']} - Maker: {specific_queue['maker_name']}")
            
            if specific_queue['status'] == 'REJECTED':
                print("   ❌ This loan was REJECTED - the portal should not show it as pending")
            elif specific_queue['status'] == 'PENDING':
                print("   ⏳ This loan is actually PENDING approval")
            elif specific_queue['status'] == 'APPROVED':
                print("   ✅ This loan was APPROVED")
        else:
            print("❌ Queue ID AQ20260104104014 not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    check_current_loan_status()