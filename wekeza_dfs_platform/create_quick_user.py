#!/usr/bin/env python3
"""
Quick User Creation - No interaction needed
"""

import sys
import os
import mysql.connector
from mysql.connector import Error
from passlib.context import CryptContext
from datetime import datetime
import time

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

def create_test_user():
    """Create a test user automatically"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Generate unique email
        timestamp = int(time.time())
        email = f"testuser{timestamp}@wekeza.com"
        
        user_data = {
            'full_name': 'Test User',
            'email': email,
            'phone': f"071{timestamp % 10000000}",
            'national_id': f"ID{timestamp}",
            'password': 'test123',
            'balance': 25000.0
        }
        
        print(f"🔍 Creating test user: {user_data['full_name']} ({user_data['email']})")
        
        # Hash password
        hashed_password = pwd_context.hash(user_data['password'])
        
        # Insert user
        user_query = """
        INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        user_values = (
            user_data['full_name'],
            user_data['email'],
            user_data['phone'],
            user_data['national_id'],
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
            user_data['balance'],
            'KES',
            'ACTIVE',
            datetime.now()
        )
        
        cursor.execute(account_query, account_values)
        
        connection.commit()
        
        print(f"✅ Test user created successfully!")
        print(f"=" * 50)
        print(f"📋 LOGIN CREDENTIALS:")
        print(f"   Email: {user_data['email']}")
        print(f"   Password: {user_data['password']}")
        print(f"   Account: {account_number}")
        print(f"   Balance: KES {user_data['balance']:,.2f}")
        print(f"=" * 50)
        print(f"🌐 LOGIN AT: http://localhost:8502")
        print(f"=" * 50)
        
        return user_data
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return None
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Creating Quick Test User...")
    create_test_user()