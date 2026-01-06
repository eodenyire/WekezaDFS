#!/usr/bin/env python3
"""
Fix missing accounts for users who were created but don't have accounts
"""

import mysql.connector

def fix_missing_accounts():
    """Create accounts for users who don't have them"""
    
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='wekeza_dfs_db'
    )
    cursor = conn.cursor(dictionary=True)
    
    print("🔍 Finding users without accounts...")
    
    # Find users without accounts
    cursor.execute("""
        SELECT u.user_id, u.full_name, u.email 
        FROM users u 
        LEFT JOIN accounts a ON u.user_id = a.user_id 
        WHERE a.user_id IS NULL
    """)
    
    users_without_accounts = cursor.fetchall()
    
    if not users_without_accounts:
        print("✅ All users have accounts")
        return
    
    print(f"📋 Found {len(users_without_accounts)} users without accounts:")
    
    for user in users_without_accounts:
        user_id = user['user_id']
        full_name = user['full_name']
        email = user['email']
        
        print(f"   - {full_name} ({email})")
        
        # Create account for this user
        account_number = f"ACC{1000000 + user_id}"
        
        cursor.execute("""
            INSERT INTO accounts (user_id, account_number, balance, currency, status)
            VALUES (%s, %s, 10000.00, 'KES', 'ACTIVE')
        """, (user_id, account_number))
        
        print(f"     ✅ Created account: {account_number}")
    
    conn.commit()
    conn.close()
    
    print(f"\n🎉 Fixed {len(users_without_accounts)} missing accounts!")

if __name__ == "__main__":
    fix_missing_accounts()