#!/usr/bin/env python3
"""
Check pending items in authorization queue
"""

import mysql.connector
from datetime import datetime

def check_pending():
    """Check pending authorization items"""
    print("🔍 Checking Pending Authorization Queue")
    print("=" * 50)
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT queue_id, transaction_type, status, amount, description, created_at
            FROM authorization_queue 
            WHERE status = 'PENDING'
            ORDER BY created_at DESC 
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        if results:
            print(f"📋 Found {len(results)} pending items:")
            print()
            for queue_id, txn_type, status, amount, description, created_at in results:
                print(f"🔸 {queue_id}")
                print(f"   Type: {txn_type}")
                print(f"   Amount: KES {amount:,.2f}")
                print(f"   Description: {description}")
                print(f"   Created: {created_at}")
                print()
        else:
            print("✅ No pending items found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_pending()