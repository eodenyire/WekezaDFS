#!/usr/bin/env python3
"""
Test database connection and check the new user
"""

import mysql.connector

def test_db_connection():
    """Test database connection and check users"""
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("✅ Database connection successful!")
        
        # Check the new user
        cursor.execute("""
            SELECT user_id, full_name, email, password_hash, business_id, is_active
            FROM users 
            WHERE email = 'mohammedchibu@gmail.com'
        """)
        
        user = cursor.fetchone()
        
        if user:
            print(f"✅ User found:")
            print(f"   ID: {user['user_id']}")
            print(f"   Name: {user['full_name']}")
            print(f"   Email: {user['email']}")
            print(f"   Password: {user['password_hash']}")
            print(f"   Business ID: {user['business_id']}")
            print(f"   Active: {user['is_active']}")
            
            # Check account
            cursor.execute("""
                SELECT account_number, balance, status
                FROM accounts 
                WHERE user_id = %s
            """, (user['user_id'],))
            
            account = cursor.fetchone()
            if account:
                print(f"✅ Account found:")
                print(f"   Number: {account['account_number']}")
                print(f"   Balance: {account['balance']}")
                print(f"   Status: {account['status']}")
            else:
                print("❌ No account found for user")
        else:
            print("❌ User not found")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()