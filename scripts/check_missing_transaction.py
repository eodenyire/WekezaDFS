#!/usr/bin/env python3
"""
Check for the missing transaction BPCAF498AB
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

def check_transaction():
    """Check for the missing transaction"""
    print("🔍 Checking for Transaction BPCAF498AB")
    print("=" * 50)
    
    conn = get_db_connection()
    if not conn:
        return
    
    cursor = conn.cursor(dictionary=True)
    
    # Check authorization queue
    print("1. Checking Authorization Queue...")
    cursor.execute("""
        SELECT * FROM authorization_queue 
        WHERE reference_id LIKE %s OR queue_id LIKE %s OR description LIKE %s
    """, ('%BPCAF498AB%', '%BPCAF498AB%', '%BPCAF498AB%'))
    
    queue_results = cursor.fetchall()
    print(f"   Found {len(queue_results)} items in authorization queue")
    for item in queue_results:
        print(f"   - {item['queue_id']} | {item['transaction_type']} | {item['status']}")
    
    # Check transactions table
    print("\n2. Checking Transactions Table...")
    cursor.execute("""
        SELECT * FROM transactions 
        WHERE reference_code LIKE %s OR description LIKE %s
    """, ('%BPCAF498AB%', '%BPCAF498AB%'))
    
    txn_results = cursor.fetchall()
    print(f"   Found {len(txn_results)} items in transactions table")
    for item in txn_results:
        print(f"   - {item['reference_code']} | {item['txn_type']} | KES {item['amount']} | {item['created_at']}")
    
    # Check account balances
    print("\n3. Checking Account Balances...")
    cursor.execute("SELECT account_number, balance FROM accounts WHERE account_number IN ('BIZ1000014', 'ACC1000023')")
    
    balances = cursor.fetchall()
    for acc in balances:
        print(f"   {acc['account_number']}: KES {acc['balance']:,.2f}")
    
    # Check recent transactions on these accounts
    print("\n4. Checking Recent Transactions on These Accounts...")
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

def main():
    """Main function"""
    print("🏦 WEKEZA BANK - MISSING TRANSACTION INVESTIGATION")
    print("=" * 60)
    print(f"Investigation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        check_transaction()
        
        print("\n" + "=" * 60)
        print("🔍 INVESTIGATION COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ INVESTIGATION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()