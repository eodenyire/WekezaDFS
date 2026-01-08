#!/usr/bin/env python3
"""
Test script to verify the maker-checker system is working across all portals
"""

import mysql.connector
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def test_authorization_queue():
    """Test the authorization queue status"""
    print("🔍 Testing Authorization Queue Status")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Get queue statistics
    cursor.execute("""
        SELECT 
            status,
            COUNT(*) as count,
            SUM(amount) as total_amount
        FROM authorization_queue 
        GROUP BY status
        ORDER BY status
    """)
    
    stats = cursor.fetchall()
    
    print("📊 Authorization Queue Statistics:")
    for status, count, total_amount in stats:
        print(f"   {status}: {count} items, Total: KES {total_amount:,.2f}")
    
    print()
    
    # Get recent pending items
    cursor.execute("""
        SELECT queue_id, transaction_type, amount, description, created_at
        FROM authorization_queue 
        WHERE status = 'PENDING'
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    pending = cursor.fetchall()
    
    if pending:
        print("⏳ Recent Pending Items:")
        for queue_id, txn_type, amount, description, created_at in pending:
            print(f"   {queue_id} | {txn_type} | KES {amount:,.2f}")
            print(f"      {description}")
            print(f"      Created: {created_at}")
            print()
    else:
        print("✅ No pending items - all transactions processed!")
    
    # Get recent approved items
    cursor.execute("""
        SELECT queue_id, transaction_type, amount, approved_at
        FROM authorization_queue 
        WHERE status = 'APPROVED'
        ORDER BY approved_at DESC 
        LIMIT 5
    """)
    
    approved = cursor.fetchall()
    
    if approved:
        print("✅ Recent Approved Items:")
        for queue_id, txn_type, amount, approved_at in approved:
            print(f"   {queue_id} | {txn_type} | KES {amount:,.2f} | {approved_at}")
    
    conn.close()

def test_transaction_flow():
    """Test that transactions are going through the queue"""
    print("\n🔄 Testing Transaction Flow")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Check recent transactions vs queue items
    cursor.execute("""
        SELECT DATE(created_at) as txn_date, COUNT(*) as direct_txns
        FROM transactions 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(created_at)
        ORDER BY txn_date DESC
    """)
    
    direct_txns = cursor.fetchall()
    
    cursor.execute("""
        SELECT DATE(created_at) as queue_date, COUNT(*) as queue_items
        FROM authorization_queue 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY DATE(created_at)
        ORDER BY queue_date DESC
    """)
    
    queue_items = cursor.fetchall()
    
    print("📈 Daily Transaction vs Queue Comparison (Last 7 Days):")
    print("Date       | Direct Txns | Queue Items | Status")
    print("-" * 50)
    
    # Combine data for comparison
    dates = set()
    if direct_txns:
        dates.update([str(d[0]) for d in direct_txns])
    if queue_items:
        dates.update([str(d[0]) for d in queue_items])
    
    direct_dict = {str(d[0]): d[1] for d in direct_txns} if direct_txns else {}
    queue_dict = {str(d[0]): d[1] for d in queue_items} if queue_items else {}
    
    for date in sorted(dates, reverse=True):
        direct_count = direct_dict.get(date, 0)
        queue_count = queue_dict.get(date, 0)
        
        if queue_count > 0:
            status = "✅ Using Queue"
        elif direct_count > 0:
            status = "⚠️ Direct Processing"
        else:
            status = "No Activity"
        
        print(f"{date} | {direct_count:11} | {queue_count:11} | {status}")
    
    conn.close()

def test_system_compliance():
    """Test overall system compliance with maker-checker"""
    print("\n🛡️ Testing System Compliance")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    # Check for recent direct transactions (should be minimal)
    cursor.execute("""
        SELECT COUNT(*) as recent_direct
        FROM transactions 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        AND description NOT LIKE '%Approved%'
    """)
    
    recent_direct = cursor.fetchone()[0]
    
    # Check for recent queue items
    cursor.execute("""
        SELECT COUNT(*) as recent_queue
        FROM authorization_queue 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
    """)
    
    recent_queue = cursor.fetchone()[0]
    
    print(f"📊 Last 24 Hours Activity:")
    print(f"   Direct Transactions: {recent_direct}")
    print(f"   Queue Items: {recent_queue}")
    
    if recent_queue > 0 and recent_direct < recent_queue:
        print("✅ COMPLIANCE: Most transactions going through maker-checker")
    elif recent_queue == 0 and recent_direct == 0:
        print("ℹ️ INFO: No recent activity to analyze")
    else:
        print("⚠️ WARNING: Some transactions may be bypassing maker-checker")
    
    # Check transaction types in queue
    cursor.execute("""
        SELECT transaction_type, COUNT(*) as count
        FROM authorization_queue 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        GROUP BY transaction_type
        ORDER BY count DESC
    """)
    
    txn_types = cursor.fetchall()
    
    if txn_types:
        print(f"\n📋 Transaction Types in Queue (Last 7 Days):")
        for txn_type, count in txn_types:
            print(f"   {txn_type}: {count} items")
    
    conn.close()

def main():
    """Main test function"""
    print("🏦 WEKEZA BANK - MAKER-CHECKER SYSTEM TEST")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        test_authorization_queue()
        test_transaction_flow()
        test_system_compliance()
        
        print("\n" + "=" * 60)
        print("✅ MAKER-CHECKER SYSTEM TEST COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()