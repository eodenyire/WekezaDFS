import mysql.connector

def debug_transfer_accounts():
    """Debug transfer accounts to see what's available"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        
        cursor = conn.cursor(dictionary=True)
        
        print("🔍 Available accounts for transfer testing:")
        cursor.execute("""
            SELECT a.account_number, a.account_id, a.balance, a.status, u.full_name
            FROM accounts a
            JOIN users u ON a.user_id = u.user_id
            WHERE a.status = 'ACTIVE'
            ORDER BY a.account_number
        """)
        
        accounts = cursor.fetchall()
        
        for account in accounts:
            print(f"Account: {account['account_number']} | Holder: {account['full_name']} | Balance: KES {account['balance']:,.2f} | Status: {account['status']}")
        
        print(f"\n📊 Total active accounts: {len(accounts)}")
        
        # Test specific accounts
        test_accounts = ['ACC1000014', 'ACC1000022', 'ACC1000023']
        
        print(f"\n🧪 Testing specific accounts:")
        for acc_num in test_accounts:
            cursor.execute("""
                SELECT a.account_number, a.account_id, a.balance, a.status, u.full_name
                FROM accounts a
                JOIN users u ON a.user_id = u.user_id
                WHERE a.account_number = %s
            """, (acc_num,))
            
            account = cursor.fetchone()
            if account:
                print(f"✅ {acc_num}: {account['full_name']} - KES {account['balance']:,.2f} ({account['status']})")
            else:
                print(f"❌ {acc_num}: Not found")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_transfer_accounts()