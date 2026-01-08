#!/usr/bin/env python3
"""
Fix password for existing user
"""

import mysql.connector

def fix_user_password():
    """Set proper password for existing user"""
    
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='wekeza_dfs_db'
    )
    cursor = conn.cursor()
    
    # Update the existing user's password
    email = "eodenyire@gmail.com"
    new_password = "password123"  # Simple password for testing
    
    cursor.execute("""
        UPDATE users 
        SET password_hash = %s 
        WHERE email = %s
    """, (new_password, email))
    
    if cursor.rowcount > 0:
        print(f"✅ Updated password for {email}")
        print(f"🔑 Login credentials: {email} / {new_password}")
    else:
        print(f"❌ User {email} not found")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    fix_user_password()