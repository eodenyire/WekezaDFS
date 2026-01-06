#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def add_approval_columns():
    """Add approval-related columns to transactions table if they don't exist"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔧 Adding approval columns to transactions table...")
        
        # Add status column
        try:
            cursor.execute("""
                ALTER TABLE transactions 
                ADD COLUMN status VARCHAR(20) DEFAULT 'COMPLETED'
            """)
            print("✅ Added 'status' column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("ℹ️ 'status' column already exists")
            else:
                print(f"❌ Error adding status column: {e}")
        
        # Add approved_by column
        try:
            cursor.execute("""
                ALTER TABLE transactions 
                ADD COLUMN approved_by VARCHAR(50) NULL
            """)
            print("✅ Added 'approved_by' column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("ℹ️ 'approved_by' column already exists")
            else:
                print(f"❌ Error adding approved_by column: {e}")
        
        # Add approved_at column
        try:
            cursor.execute("""
                ALTER TABLE transactions 
                ADD COLUMN approved_at DATETIME NULL
            """)
            print("✅ Added 'approved_at' column")
        except mysql.connector.Error as e:
            if "Duplicate column name" in str(e):
                print("ℹ️ 'approved_at' column already exists")
            else:
                print(f"❌ Error adding approved_at column: {e}")
        
        # Commit changes
        conn.commit()
        
        # Show current table structure
        cursor.execute("DESCRIBE transactions")
        columns = cursor.fetchall()
        
        print("\n📋 Current transactions table structure:")
        for col in columns:
            print(f"   {col[0]} - {col[1]} - {col[2]} - {col[3]} - {col[4]} - {col[5]}")
        
        conn.close()
        print("\n✅ Database update completed successfully!")
        
    except Exception as e:
        print(f"❌ Error updating database: {e}")

if __name__ == "__main__":
    add_approval_columns()