import mysql.connector
import pandas as pd

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='wekeza_dfs_db'
)

print("🏦 Checking account data for ACC1000014...")

cursor = conn.cursor(dictionary=True)

# Check account details
cursor.execute("""
    SELECT a.*, u.full_name, u.email, u.phone_number
    FROM accounts a
    JOIN users u ON a.user_id = u.user_id
    WHERE a.account_number = %s
""", ("ACC1000014",))

account = cursor.fetchone()

if account:
    print(f"✅ Account found:")
    print(f"   Account Number: {account['account_number']}")
    print(f"   Account ID: {account['account_id']}")
    print(f"   Account Holder: {account['full_name']}")
    print(f"   Email: {account['email']}")
    print(f"   Phone: {account['phone_number']}")
    print(f"   Balance: KES {account['balance']:,.2f}")
    print(f"   Status: {account['status']}")
    
    # Check recent transactions using account_id
    print(f"\n📊 Recent transactions for ACC1000014 (account_id: {account['account_id']}):")
    cursor.execute("""
        SELECT * FROM transactions 
        WHERE account_id = %s 
        ORDER BY created_at DESC 
        LIMIT 10
    """, (account['account_id'],))

    transactions = cursor.fetchall()

    if transactions:
        for txn in transactions:
            print(f"   {txn['created_at']} | {txn['txn_type']} | KES {txn['amount']:,.2f} | {txn['description']}")
    else:
        print("   No transactions found")
        
else:
    print("❌ Account not found")

conn.close()