#!/usr/bin/env python3
"""
Insert Test Users into Wekeza DFS Database
This script creates sample users, accounts, and businesses for testing
"""

import mysql.connector
from mysql.connector import Error
import hashlib
import uuid
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wekeza_dfs_db'
}

def hash_password(password):
    """Simple password hashing (in production, use proper bcrypt)"""
    return hashlib.sha256(password.encode()).hexdigest()

def insert_test_users():
    """Insert test users into the database"""
    print("🔍 Connecting to database...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("✅ Connected to MySQL database")
        
        # Test users data
        test_users = [
            {
                'full_name': 'John Doe',
                'email': 'john@test.com',
                'phone_number': '0712345678',
                'national_id': '12345678',
                'password': 'password123',
                'balance': 25000.00
            },
            {
                'full_name': 'Jane Smith',
                'email': 'jane@test.com',
                'phone_number': '0723456789',
                'national_id': '23456789',
                'password': 'password123',
                'balance': 15000.00
            },
            {
                'full_name': 'Mike Johnson',
                'email': 'mike@test.com',
                'phone_number': '0734567890',
                'national_id': '34567890',
                'password': 'password123',
                'balance': 50000.00
            },
            {
                'full_name': 'Sarah Wilson',
                'email': 'sarah@test.com',
                'phone_number': '0745678901',
                'national_id': '45678901',
                'password': 'password123',
                'balance': 8000.00
            },
            {
                'full_name': 'David Brown',
                'email': 'david@test.com',
                'phone_number': '0756789012',
                'national_id': '56789012',
                'password': 'password123',
                'balance': 75000.00
            }
        ]
        
        print(f"\n🔍 Inserting {len(test_users)} test users...")
        
        for i, user in enumerate(test_users, 1):
            try:
                # Check if user already exists
                cursor.execute("SELECT user_id FROM users WHERE email = %s", (user['email'],))
                if cursor.fetchone():
                    print(f"   ⚠️  User {user['full_name']} already exists - skipping")
                    continue
                
                # Insert user
                user_query = """
                INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                user_values = (
                    user['full_name'],
                    user['email'],
                    user['phone_number'],
                    user['national_id'],
                    hash_password(user['password']),
                    'TIER_2',
                    1,
                    datetime.now()
                )
                
                cursor.execute(user_query, user_values)
                user_id = cursor.lastrowid
                
                # Create account for user
                account_number = f"ACC{1000000 + user_id}"
                account_query = """
                INSERT INTO accounts (user_id, account_number, balance, currency, status, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """
                account_values = (
                    user_id,
                    account_number,
                    user['balance'],
                    'KES',
                    'ACTIVE',
                    datetime.now()
                )
                
                cursor.execute(account_query, account_values)
                
                print(f"   ✅ {user['full_name']} - Account: {account_number} - Balance: KES {user['balance']:,.2f}")
                
            except Error as e:
                print(f"   ❌ Error creating user {user['full_name']}: {e}")
        
        # Insert test businesses
        print(f"\n🔍 Inserting test businesses...")
        
        test_businesses = [
            {
                'business_name': 'Tech Solutions Ltd',
                'registration_no': 'BIZ001',
                'kra_pin': 'A123456789',
                'sector': 'Technology',
                'director_email': 'director@techsolutions.com',
                'director_password': 'business123'
            },
            {
                'business_name': 'Green Farm Co',
                'registration_no': 'BIZ002',
                'kra_pin': 'A987654321',
                'sector': 'Agriculture',
                'director_email': 'manager@greenfarm.com',
                'director_password': 'business123'
            }
        ]
        
        for business in test_businesses:
            try:
                # Check if business already exists
                cursor.execute("SELECT business_id FROM businesses WHERE registration_no = %s", (business['registration_no'],))
                if cursor.fetchone():
                    print(f"   ⚠️  Business {business['business_name']} already exists - skipping")
                    continue
                
                business_query = """
                INSERT INTO businesses (business_name, registration_no, kra_pin, sector, created_at)
                VALUES (%s, %s, %s, %s, %s)
                """
                business_values = (
                    business['business_name'],
                    business['registration_no'],
                    business['kra_pin'],
                    business['sector'],
                    datetime.now()
                )
                
                cursor.execute(business_query, business_values)
                
                print(f"   ✅ {business['business_name']} - Reg: {business['registration_no']}")
                
            except Error as e:
                print(f"   ❌ Error creating business {business['business_name']}: {e}")
        
        # Commit all changes
        connection.commit()
        
        print(f"\n🎉 Test data inserted successfully!")
        print(f"\n📋 Test User Credentials:")
        print("=" * 50)
        for user in test_users:
            print(f"Email: {user['email']}")
            print(f"Password: {user['password']}")
            print(f"Balance: KES {user['balance']:,.2f}")
            print("-" * 30)
        
        print(f"\n📋 Test Business Credentials:")
        print("=" * 50)
        for business in test_businesses:
            print(f"Business: {business['business_name']}")
            print(f"Director Email: {business['director_email']}")
            print(f"Password: {business['director_password']}")
            print("-" * 30)
        
        print(f"\n🚀 You can now test the system with these accounts!")
        print("Visit: http://localhost:8502 (Customer Portal)")
        print("Visit: http://localhost:8504 (Business Portal)")
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\n🔌 Database connection closed")
    
    return True

def verify_data():
    """Verify the inserted data"""
    print(f"\n🔍 Verifying inserted data...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   Users: {user_count}")
        
        # Count accounts
        cursor.execute("SELECT COUNT(*) FROM accounts")
        account_count = cursor.fetchone()[0]
        print(f"   Accounts: {account_count}")
        
        # Count businesses
        cursor.execute("SELECT COUNT(*) FROM businesses")
        business_count = cursor.fetchone()[0]
        print(f"   Businesses: {business_count}")
        
        # Show sample data
        cursor.execute("SELECT full_name, email, phone_number FROM users LIMIT 3")
        users = cursor.fetchall()
        print(f"\n   Sample Users:")
        for user in users:
            print(f"   - {user[0]} ({user[1]})")
        
    except Error as e:
        print(f"❌ Error verifying data: {e}")
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Wekeza DFS Platform - Test Data Insertion")
    print("=" * 60)
    
    success = insert_test_users()
    if success:
        verify_data()
        print(f"\n✅ Ready for testing! Use the credentials above to login.")
    else:
        print(f"\n❌ Failed to insert test data. Check database connection.")