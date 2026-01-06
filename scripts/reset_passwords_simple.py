#!/usr/bin/env python3
"""
Reset all passwords to use simple SHA256 hashing to avoid bcrypt issues
"""

import mysql.connector
from mysql.connector import Error
import hashlib

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wekeza_dfs_db'
}

def simple_hash(password):
    """Simple SHA256 hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def reset_all_passwords():
    """Reset all user passwords to simple hashing"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        print("🔍 Resetting all passwords to simple hashing...")
        
        # Get all users
        cursor.execute("SELECT user_id, email FROM users")
        users = cursor.fetchall()
        
        # Default password for all users
        default_password = "test123"
        hashed_password = simple_hash(default_password)
        
        print(f"Setting all users to password: {default_password}")
        print(f"Hash: {hashed_password}")
        
        # Update all users
        for user_id, email in users:
            cursor.execute("UPDATE users SET password_hash = %s WHERE user_id = %s", 
                         (hashed_password, user_id))
            print(f"   ✅ Updated {email}")
        
        connection.commit()
        
        print(f"\n✅ All passwords reset successfully!")
        print(f"\n📋 ALL USERS NOW HAVE:")
        print(f"   Password: {default_password}")
        print(f"\n🌐 Test at: http://localhost:8502")
        print(f"\n📧 Available emails:")
        for user_id, email in users:
            print(f"   - {email}")
        
        return True
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Wekeza DFS Platform - Simple Password Reset")
    print("=" * 60)
    reset_all_passwords()