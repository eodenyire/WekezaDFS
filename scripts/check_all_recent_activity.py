#!/usr/bin/env python3

import mysql.connector
from datetime import datetime, timedelta

def check_all_recent_activity():
    """Check ALL recent activity in authorization queue"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Checking ALL recent activity in authorization_queue...")
        
        # Check ALL recent entries (last 15 minutes)
        cursor.execute("""
            SELECT queue_id, transaction_type, reference_id, amount, status, created_at, maker_name
            FROM authorization_queue 
            WHERE created_at >= %s
            ORDER BY created_at DESC
        """, (datetime.now() - timedelta(minutes=15),))
        
        recent_activity = cursor.fetchall()
        
        if recent_activity:
            print(f"📋 Found {len(recent_activity)} recent entries (last 15 minutes):")
            for entry in recent_activity:
                print(f"  - {entry['queue_id']}: {entry['transaction_type']} - KES {entry['amount']:,.2f} - {entry['status']} - {entry['created_at']}")
        else:
            print("❌ No recent activity found in authorization_queue")
        
        # Check the total count in authorization_queue
        cursor.execute("SELECT COUNT(*) as total FROM authorization_queue")
        total_count = cursor.fetchone()['total']
        print(f"\n📊 Total entries in authorization_queue: {total_count}")
        
        # Check pending entries
        cursor.execute("SELECT COUNT(*) as pending FROM authorization_queue WHERE status = 'PENDING'")
        pending_count = cursor.fetchone()['pending']
        print(f"📊 Pending entries: {pending_count}")
        
        conn.close()
        
        if recent_activity:
            print("\n✅ Authorization queue is active - other operations are being submitted")
            print("❓ If you submitted a loan and it's not here, there might be an error in the loan submission")
        else:
            print("\n❌ No recent activity - authorization queue might have an issue")
        
    except Exception as e:
        print(f"❌ Error checking activity: {e}")

if __name__ == "__main__":
    check_all_recent_activity()