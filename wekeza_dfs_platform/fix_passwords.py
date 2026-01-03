#!/usr/bin/env python3
"""
Fix password hashing for test users to match the API's bcrypt implementation
"""

import mysql.connector
from mysql.connector import Error
from passlib.context import CryptContext

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wekeza_dfs_db'
}

# Use the same password context as the API
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fix_user_passwords():
    """Update user passwords with proper bcrypt hashing"""
    print("🔍 Fixing user passwords with bcrypt hashing...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Test users with their passwords
        test_users = [
            ('john@test.com', 'password123'),
            ('jane@test.com', 'password123'),
            ('mike@test.com', 'password123'),
            ('sarah@test.com', 'password123'),
            ('david@test.com', 'password123')
        ]
        
        print(f"Updating passwords for {len(test_users)} users...")
        
        for email, password in test_users:
            try:
                # Generate bcrypt hash
                hashed_password = pwd_context.hash(password)
                
                # Update user password
                update_query = "UPDATE users SET password_hash = %s WHERE email = %s"
                cursor.execute(update_query, (hashed_password, email))
                
                if cursor.rowcount > 0:
                    print(f"   ✅ Updated password for {email}")
                else:
                    print(f"   ⚠️  User {email} not found")
                
            except Error as e:
                print(f"   ❌ Error updating {email}: {e}")
        
        connection.commit()
        print("✅ Password update completed!")
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def create_business_users():
    """Create user accounts for business directors so they can login"""
    print("\n🔍 Creating user accounts for business directors...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        
        # Business directors that need user accounts
        business_users = [
            {
                'full_name': 'Tech Director',
                'email': 'director@techsolutions.com',
                'phone_number': '0700000001',
                'national_id': 'DIR001',
                'password': 'business123'
            },
            {
                'full_name': 'Farm Manager',
                'email': 'manager@greenfarm.com',
                'phone_number': '0700000002',
                'national_id': 'DIR002',
                'password': 'business123'
            }
        ]
        
        for user in business_users:
            try:
                # Check if user already exists
                cursor.execute("SELECT user_id FROM users WHERE email = %s", (user['email'],))
                if cursor.fetchone():
                    print(f"   ⚠️  User {user['email']} already exists - updating password")
                    
                    # Update password
                    hashed_password = pwd_context.hash(user['password'])
                    cursor.execute("UPDATE users SET password_hash = %s WHERE email = %s", 
                                 (hashed_password, user['email']))
                else:
                    # Create new user
                    hashed_password = pwd_context.hash(user['password'])
                    
                    user_query = """
                    INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    user_values = (
                        user['full_name'],
                        user['email'],
                        user['phone_number'],
                        user['national_id'],
                        hashed_password,
                        'TIER_2',
                        1
                    )
                    
                    cursor.execute(user_query, user_values)
                    print(f"   ✅ Created user account for {user['email']}")
                
            except Error as e:
                print(f"   ❌ Error processing {user['email']}: {e}")
        
        connection.commit()
        print("✅ Business user accounts ready!")
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def verify_authentication():
    """Test authentication with the fixed passwords"""
    print("\n🔍 Testing authentication...")
    
    import requests
    
    API_URL = "http://localhost:8000"
    
    # Test personal banking login
    test_credentials = [
        ("john@test.com", "password123"),
        ("director@techsolutions.com", "business123")
    ]
    
    for email, password in test_credentials:
        try:
            response = requests.post(f"{API_URL}/token", 
                                   data={"username": email, "password": password})
            
            if response.status_code == 200:
                print(f"   ✅ Authentication successful for {email}")
            else:
                print(f"   ❌ Authentication failed for {email}: {response.status_code}")
                print(f"      Response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error testing {email}: {e}")

if __name__ == "__main__":
    print("🚀 Wekeza DFS Platform - Password Fix")
    print("=" * 50)
    
    # Fix personal banking passwords
    if fix_user_passwords():
        # Create business user accounts
        if create_business_users():
            # Test authentication
            verify_authentication()
            
            print(f"\n🎉 Password fix completed!")
            print(f"\n📋 Updated Credentials:")
            print("=" * 30)
            print("Personal Banking:")
            print("  john@test.com / password123")
            print("  jane@test.com / password123")
            print("  mike@test.com / password123")
            print("  sarah@test.com / password123")
            print("  david@test.com / password123")
            print("\nBusiness Banking:")
            print("  director@techsolutions.com / business123")
            print("  manager@greenfarm.com / business123")
            print(f"\n🚀 Try logging in again!")
        else:
            print(f"\n❌ Failed to create business users")
    else:
        print(f"\n❌ Failed to fix passwords")