#!/usr/bin/env python3

import mysql.connector

def check_insurance_tables():
    """Check existing insurance table structures"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔍 Checking existing insurance-related tables...")
        
        # Check what tables exist
        cursor.execute("SHOW TABLES LIKE '%insurance%'")
        insurance_tables = cursor.fetchall()
        
        print(f"\n📋 Found {len(insurance_tables)} insurance-related tables:")
        for table in insurance_tables:
            print(f"- {table[0]}")
        
        # Check each table structure
        for table in insurance_tables:
            table_name = table[0]
            print(f"\n📊 Structure of {table_name}:")
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            for col in columns:
                print(f"  - {col[0]} ({col[1]}) {'NOT NULL' if col[2] == 'NO' else 'NULL'} {'DEFAULT: ' + str(col[4]) if col[4] else ''}")
        
        # Check if there are any existing insurance records
        for table in insurance_tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n📈 {table_name}: {count} records")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error checking tables: {e}")

if __name__ == "__main__":
    check_insurance_tables()