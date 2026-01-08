#!/usr/bin/env python3
"""
Investigate the new transfer BP05BA0930 for KES 40,000
"""

import mysql.connector
from datetime import datetime

def investigate_transfer():
    """Investigate the BP05BA0930 transfer"""
    print("🚨 URGENT INVESTIGATION: Transfer BP05BA0930")
    print("=" * 60)
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        # Check authorization queue for BP05BA0930
        print("1. Checking Authorization Queue...")
        cursor.execute("""
            SELECT * FROM authorization_queue 
            WHERE reference_id LIKE %s OR queue_id LIKE %s OR description LIKE %s
        """, ('%BP05BA0930%', '%BP05BA0930%', '%BP05BA0930%'))
        
        queue_results = cursor.fetchall()
        print(f"   Found {len(queue_results)} items in authorization queue")
        for item in queue_results:
            print(f"   - {item['queue_id']} | {item['transaction_type']} | {item['status']} | KES {item['amount']:,.2f}")
        
        # Check transactions table for BP05BA0930
        print("\n2. Checking Transactions Table...")
        cursor.execute("""
            SELECT * FROM transactions 
            WHERE reference_code LIKE %s OR description LIKE %s
        """, ('%BP05BA0930%', '%BP05BA0930%'))
        
        txn_results = cursor.fetchall()
        print(f"   Found {len(txn_results)} items in transactions table")
        for item in txn_results:
            print(f"   - {item['reference_code']} | {item['txn_type']} | KES {item['amount']} | {item['created_at']}")
        
        # Check current account balances
        print("\n3. Checking Current Account Balances...")
        cursor.execute("SELECT account_number, balance FROM accounts WHERE account_number IN ('BIZ1000014', 'ACC1000023')")
        
        balances = cursor.fetchall()
        for acc in balances:
            print(f"   {acc['account_number']}: KES {acc['balance']:,.2f}")
        
        # Check ALL pending items in queue
        print("\n4. Checking ALL Pending Items...")
        cursor.execute("""
            SELECT queue_id, transaction_type, status, amount, description, created_at
            FROM authorization_queue 
            WHERE status = 'PENDING'
            ORDER BY created_at DESC
        """)
        
        pending_results = cursor.fetchall()
        print(f"   Found {len(pending_results)} pending items:")
        for item in pending_results:
            print(f"   - {item['queue_id']} | {item['transaction_type']} | KES {item['amount']:,.2f} | {item['created_at']}")
        
        # Check recent transactions on these accounts
        print("\n5. Checking Recent Transactions (Last 10)...")
        cursor.execute("""
            SELECT t.*, a.account_number FROM transactions t
            JOIN accounts a ON t.account_id = a.account_id
            WHERE a.account_number IN ('BIZ1000014', 'ACC1000023')
            ORDER BY t.created_at DESC LIMIT 10
        """)
        
        recent_txns = cursor.fetchall()
        print(f"   Found {len(recent_txns)} recent transactions:")
        for txn in recent_txns:
            print(f"   - {txn['account_number']} | {txn['txn_type']} | KES {txn['amount']} | {txn['reference_code']} | {txn['created_at']}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main investigation"""
    print("🏦 WEKEZA BANK - URGENT TRANSFER INVESTIGATION")
    print("=" * 60)
    print(f"Investigation Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Transfer: BP05BA0930 - KES 40,000")
    print("Status: Showing 'completed' but money not transferred")
    print()
    
    investigate_transfer()
    
    print("\n" + "=" * 60)
    print("🔍 INVESTIGATION COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    main()