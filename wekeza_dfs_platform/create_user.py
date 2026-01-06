#!/usr/bin/env python3
"""
Simple User Creation Script for Wekeza DFS Platform
Run this to create users that can login to the web portals
"""

import sys
import os
import mysql.connector
from mysql.connector import Error
from passlib.context import CryptContext
from datetime import datetime
import uuid

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), '03_Source_Code', 'backend_api', 'app')
sys.path.insert(0, app_dir)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wekeza_dfs_db'
}

# Use the same password context as the API
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user_interactive():
    """Interactive user creation"""
    print("🚀 Wekeza DFS Platform - User Creation")
    print("=" * 50)
    
    # Get user input
    full_name = input("Enter Full Name: ").strip()
    email = input("Enter Email: ").strip()
    phone = input("Enter Phone Number (e.g., 0712345678): ").strip()
    national_id = input("Enter National ID: ").strip()
    password = input("Enter Password: ").strip()
    
    # Validate input
    if not all([full_name, email, phone, national_id, password]):
        print("❌ All fields are required!")
        return False
    
    # Ask for initial balance
    try:
        balance = float(input("Enter Initial Balance (KES): ").strip() or "10000")
    except ValueError:
        balance = 10000.0
    
    return create_user(full_name, email, phone, national_id, password, balance)

def create_user(full_name, email, phone, national_id, password, balance=10000.0):
    """Create a user with account"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print(f"\n🔍 Creating user: {full_name} ({email})")
        
        # Check if user already exists
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"⚠️  User with email {email} already exists!")
            return False
        
        # Hash password
        hashed_password = pwd_context.hash(password)
        
        # Insert user
        user_query = """
        INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        user_values = (
            full_name,
            email,
            phone,
            national_id,
            hashed_password,
            'TIER_2',
            1,
            datetime.now()
        )
        
        cursor.execute(user_query, user_values)
        user_id = cursor.lastrowid
        
        # Create account
        account_number = f"ACC{1000000 + user_id}"
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
        
        connection.commit()
        
        print(f"✅ User created successfully!")
        print(f"   Name: {full_name}")
        print(f"   Email: {email}")
        print(f"   Account: {account_number}")
        print(f"   Balance: KES {balance:,.2f}")
        print(f"\n🌐 You can now login at:")
        print(f"   Customer Portal: http://localhost:8502")
        print(f"   Credentials: {email} / {password}")
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def create_quick_test_user():
    """Create a quick test user for immediate testing"""
    print("🚀 Creating Quick Test User...")
    
    # Generate unique email
    import time
    timestamp = int(time.time())
    email = f"test{timestamp}@wekeza.com"
    
    return create_user(
        full_name="Test User",
        email=email,
        phone=f"07{timestamp % 100000000}",
        national_id=f"ID{timestamp}",
        password="test123",
        balance=25000.0
    )

def main():
    print("🚀 Wekeza DFS Platform - User Creation Tool")
    print("=" * 60)
    print("Choose an option:")
    print("1. Create user interactively")
    print("2. Create quick test user")
    print("3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        create_user_interactive()
    elif choice == "2":
        create_quick_test_user()
    elif choice == "3":
        print("Goodbye!")
        return
    else:
        print("Invalid choice!")
        return
    
    # Ask if user wants to create another
    if input("\nCreate another user? (y/n): ").lower().startswith('y'):
        main()

if __name__ == "__main__":
    main()