#!/usr/bin/env python3

import mysql.connector
from datetime import datetime, timedelta

def check_new_loan_in_queue():
    """Check if new loan application was pulled into authorization queue"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking for NEW loan applications in authorization queue...")
        
        # Check for very recent loan applications (last 10 minutes)
        print("\n📋 Recent LOAN_APPLICATION entries in authorization_queue (last 10 minutes):")
        cursor.execute("""
            SELECT queue_id, transaction_type, reference_id, amount, status, created_at, maker_name, operation_data
            FROM authorization_queue 
            WHERE transaction_type = 'LOAN_APPLICATION' 
            AND created_at >= %s
            ORDER BY created_at DESC
        """, (datetime.now() - timedelta(minutes=10),))
        
        recent_loans = cursor.fetchall()
        
        if recent_loans:
            print(f"✅ Found {len(recent_loans)} recent loan application(s):")
            for loan in recent_loans:
                print(f"  - Queue ID: {loan['queue_id']}")
                print(f"    Reference: {loan['reference_id']}")
                print(f"    Amount: KES {loan['amount']:,.2f}")
                print(f"    Status: {loan['status']}")
                print(f"    Created: {loan['created_at']}")
                print(f"    Maker: {loan['maker_name']}")
                if loan['operation_data']:
                    print(f"    Has Operation Data: YES")
                else:
                    print(f"    Has Operation Data: NO")
                print("    ---")
        else:
            print("❌ No recent loan applications found in authorization_queue")
        
        # Check ALL pending loan applications
        print(f"\n📋 ALL PENDING loan applications in authorization_queue:")
        cursor.execute("""
            SELECT queue_id, reference_id, amount, created_at, maker_name
            FROM authorization_queue 
            WHERE transaction_type = 'LOAN_APPLICATION' AND status = 'PENDING'
            ORDER BY created_at DESC
        """)
        
        all_pending_loans = cursor.fetchall()
        
        if all_pending_loans:
            print(f"✅ Found {len(all_pending_loans)} pending loan application(s):")
            for loan in all_pending_loans:
                print(f"  - {loan['queue_id']}: {loan['reference_id']} - KES {loan['amount']:,.2f} - {loan['created_at']}")
        else:
            print("❌ No pending loan applications found")
        
        # Check if there are any new entries in loan_applications table
        print(f"\n📋 Recent entries in loan_applications table (last 10 minutes):")
        cursor.execute("""
            SELECT application_id, loan_type, loan_amount, status, created_at, created_by
            FROM loan_applications 
            WHERE created_at >= %s
            ORDER BY created_at DESC
        """, (datetime.now() - timedelta(minutes=10),))
        
        recent_loan_apps = cursor.fetchall()
        
        if recent_loan_apps:
            print(f"⚠️ Found {len(recent_loan_apps)} recent loan_applications entries:")
            for app in recent_loan_apps:
                print(f"  - {app['application_id']}: {app['loan_type']} - KES {app['loan_amount']:,.2f} - {app['status']} - {app['created_at']}")
            print("⚠️ NOTE: These should NOT exist if maker-checker is working properly!")
        else:
            print("✅ No recent entries in loan_applications table (GOOD - means maker-checker is working)")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking queue: {e}")

if __name__ == "__main__":
    check_new_loan_in_queue()