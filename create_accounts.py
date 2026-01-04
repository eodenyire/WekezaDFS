#!/usr/bin/env python3
"""
Create accounts for existing users
"""

import mysql.connector
from mysql.connector import Error
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wekeza_dfs_db'
}

def create_accounts():
    """Create accounts for users who don't have them"""
    print("🔍 Creating accounts for existing users...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Get users without accounts
        cursor.execute("""
            SELECT u.user_id, u.full_name, u.email 
            FROM users u 
            LEFT JOIN accounts a ON u.user_id = a.user_id 
            WHERE a.account_id IS NULL
        """)
        
        users_without_accounts = cursor.fetchall()
        
        if not users_without_accounts:
            print("✅ All users already have accounts")
            return
        
        print(f"Found {len(users_without_accounts)} users without accounts")
        
        # Account balances for each user
        balances = {
            'john@test.com': 25000.00,
            'jane@test.com': 15000.00,
            'mike@test.com': 50000.00,
            'sarah@test.com': 8000.00,
            'david@test.com': 75000.00
        }
        
        for user_id, full_name, email in users_without_accounts:
            try:
                account_number = f"ACC{1000000 + user_id}"
                balance = balances.get(email, 10000.00)  # Default balance
                
                account_query = """
                INSERT INTO accounts (user_id, account_number, balance, currency, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                account_values = (
                    user_id,
                    account_number,
                    balance,
                    'KES',
                    'ACTIVE',
                    datetime.now()
                )
                
                cursor.execute(account_query, account_values)
                print(f"   ✅ {full_name} - Account: {account_number} - Balance: KES {balance:,.2f}")
                
            except Error as e:
                print(f"   ❌ Error creating account for {full_name}: {e}")
        
        connection.commit()
        print("✅ Accounts created successfully!")
        
    except Error as e:
        print(f"❌ Database error: {e}")
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    create_accounts()