#!/usr/bin/env python3

import mysql.connector

def check_loan_table_structure():
    """Check what loan tables exist and their structure"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔍 Checking loan table structure...")
        
        # Check what tables exist
        cursor.execute("SHOW TABLES LIKE '%loan%'")
        loan_tables = cursor.fetchall()
        
        print(f"\n📋 Loan-related tables found:")
        for table in loan_tables:
            print(f"  - {table[0]}")
        
        # Check loan_accounts table structure if it exists
        try:
            cursor.execute("DESCRIBE loan_accounts")
            columns = cursor.fetchall()
            print(f"\n📋 LOAN_ACCOUNTS table structure:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        except Exception as e:
            print(f"\n❌ LOAN_ACCOUNTS table issue: {e}")
        
        # Check if there are any entries in loan_accounts
        try:
            cursor.execute("SELECT COUNT(*) FROM loan_accounts")
            count = cursor.fetchone()[0]
            print(f"\n📊 LOAN_ACCOUNTS entries: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM loan_accounts LIMIT 3")
                entries = cursor.fetchall()
                print("Sample entries:")
                for entry in entries:
                    print(f"  - {entry}")
        except Exception as e:
            print(f"\n❌ Error checking loan_accounts entries: {e}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    check_loan_table_structure()