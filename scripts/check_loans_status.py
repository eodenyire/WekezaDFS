#!/usr/bin/env python3

import mysql.connector

def check_loans_status():
    """Check current status of loans and authorization queue"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("📋 Checking loan applications...")
        cursor.execute("SELECT * FROM loan_applications WHERE account_number = 'ACC1000014'")
        loans = cursor.fetchall()
        
        print(f"Found {len(loans)} loan applications for ACC1000014:")
        for loan in loans:
            print(f"  - {loan['application_id']}: {loan['loan_type']} - KES {loan['loan_amount']:,.2f} - Status: {loan['status']}")
        
        print("\n📋 Checking authorization queue...")
        cursor.execute("SELECT * FROM authorization_queue WHERE status = 'PENDING'")
        queue_items = cursor.fetchall()
        
        print(f"Found {len(queue_items)} pending items in authorization queue:")
        for item in queue_items:
            print(f"  - {item['queue_id']}: {item['transaction_type']} - {item['reference_id']} - KES {item['amount']:,.2f}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    check_loans_status()