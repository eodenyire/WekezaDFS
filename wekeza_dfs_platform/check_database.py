#!/usr/bin/env python3
"""
Check what's currently in the database
"""

import mysql.connector

def check_database():
    """Check current database state"""
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("📊 Current Database State:")
        print("=" * 40)
        
        # Check what tables exist
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if not tables:
            print("❌ No tables found")
            return
            
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"📋 {table_name}: {count} records")
            
            # Show sample data for tables with records
            if count > 0 and count <= 10:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cursor.fetchall()
                cursor.execute(f"DESCRIBE {table_name}")
                columns = [col[0] for col in cursor.fetchall()]
                
                print(f"   Sample data from {table_name}:")
                for row in rows:
                    row_data = dict(zip(columns, row))
                    if table_name == 'users':
                        print(f"     ID: {row_data.get('user_id')}, Email: {row_data.get('email')}, Name: {row_data.get('full_name')}")
                    elif table_name == 'accounts':
                        print(f"     ID: {row_data.get('account_id')}, Number: {row_data.get('account_number')}, Balance: {row_data.get('balance')}")
                    else:
                        print(f"     {row_data}")
                print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

if __name__ == "__main__":
    check_database()