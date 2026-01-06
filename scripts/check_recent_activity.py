#!/usr/bin/env python3

import mysql.connector
from datetime import datetime, timedelta

def check_recent_activity():
    """Check recent loan applications and authorization queue entries"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        # Check recent loan applications (last 2 hours)
        print("📋 Checking recent loan applications (last 2 hours)...")
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE created_at >= %s 
            ORDER BY created_at DESC
        """, (datetime.now() - timedelta(hours=2),))
        
        recent_loans = cursor.fetchall()
        print(f"Found {len(recent_loans)} recent loan applications:")
        for loan in recent_loans:
            print(f"  - {loan['application_id']}: {loan['loan_type']} - KES {loan['loan_amount']:,.2f} - Status: {loan['status']} - Created: {loan['created_at']}")
        
        # Check recent authorization queue entries (last 2 hours)
        print(f"\n📋 Checking recent authorization queue entries (last 2 hours)...")
        cursor.execute("""
            SELECT * FROM authorization_queue 
            WHERE created_at >= %s 
            ORDER BY created_at DESC
        """, (datetime.now() - timedelta(hours=2),))
        
        recent_queue = cursor.fetchall()
        print(f"Found {len(recent_queue)} recent queue entries:")
        for item in recent_queue:
            print(f"  - {item['queue_id']}: {item['transaction_type']} - {item['reference_id']} - KES {item['amount']:,.2f} - Created: {item['created_at']}")
        
        # Check for the specific queue ID from the screenshot
        print(f"\n🔍 Checking for specific Queue ID: AQ20260104104014...")
        cursor.execute("SELECT * FROM authorization_queue WHERE queue_id = %s", ('AQ20260104104014',))
        specific_item = cursor.fetchone()
        
        if specific_item:
            print("✅ Found the queue item:")
            print(f"  - Queue ID: {specific_item['queue_id']}")
            print(f"  - Type: {specific_item['transaction_type']}")
            print(f"  - Reference: {specific_item['reference_id']}")
            print(f"  - Amount: KES {specific_item['amount']:,.2f}")
            print(f"  - Status: {specific_item['status']}")
            print(f"  - Created: {specific_item['created_at']}")
        else:
            print("❌ Queue ID AQ20260104104014 not found in authorization_queue table")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking recent activity: {e}")

if __name__ == "__main__":
    check_recent_activity()