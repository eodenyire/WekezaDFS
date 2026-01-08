#!/usr/bin/env python3
"""
Manual business creation to bypass admin panel lock issues
"""

import mysql.connector
from datetime import datetime

def create_business_manual():
    """Create business manually"""
    
    # Business details
    business_name = "Quadritech Solutions Ltd"
    registration_no = "PVT_5253_728"
    kra_pin = "A004526892V"
    sector = "Technology"
    
    # Director details
    director_name = "David Mutune"
    director_email = "davidmtune@gmail.com"
    director_password = "business123"
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🏢 Creating business manually...")
        
        # Insert business
        cursor.execute("""
        INSERT INTO businesses (business_name, registration_no, kra_pin, sector, created_at)
        VALUES (%s, %s, %s, %s, %s)
        """, (business_name, registration_no, kra_pin, sector, datetime.now()))
        
        business_id = cursor.lastrowid
        print(f"   ✅ Business created with ID: {business_id}")
        
        # Create director user
        cursor.execute("""
        INSERT INTO users (full_name, email, phone_number, national_id, password_hash, kyc_tier, is_active, business_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (director_name, director_email, '0716478836', f"DIR{registration_no}", 
              director_password, 'TIER_3', 1, business_id, datetime.now()))
        
        user_id = cursor.lastrowid
        print(f"   ✅ Director created with ID: {user_id}")
        
        # Create business account
        account_number = f"BIZ{1000000 + business_id}"
        cursor.execute("""
        INSERT INTO accounts (business_id, account_number, balance, currency, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """, (business_id, account_number, 50000.0, 'KES', 'ACTIVE', datetime.now()))
        
        print(f"   ✅ Business account created: {account_number}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Business registration complete!")
        print(f"🏢 Business: {business_name}")
        print(f"💰 Account: {account_number} (KES 50,000)")
        print(f"🔑 Director login: {director_email} / {director_password}")
        print(f"🌐 Test at: http://localhost:8504")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        try:
            conn.rollback()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    create_business_manual()