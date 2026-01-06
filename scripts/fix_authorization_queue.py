#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def fix_authorization_queue_table():
    """Fix authorization queue table step by step"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔄 Fixing authorization queue table...")
        
        # First, check what transaction types exist
        cursor.execute("SELECT DISTINCT transaction_type FROM authorization_queue")
        existing_types = [row[0] for row in cursor.fetchall()]
        print(f"📋 Existing transaction types: {existing_types}")
        
        # Fix LOAN entries to LOAN_APPLICATION first
        cursor.execute("""
            UPDATE authorization_queue 
            SET transaction_type = 'LOAN_APPLICATION' 
            WHERE transaction_type = 'LOAN'
        """)
        updated_rows = cursor.rowcount
        if updated_rows > 0:
            print(f"✅ Updated {updated_rows} LOAN entries to LOAN_APPLICATION")
        
        # Now update the enum to include all new types
        print("🔄 Updating transaction_type enum...")
        cursor.execute("""
            ALTER TABLE authorization_queue 
            MODIFY COLUMN transaction_type ENUM(
                'CASH_DEPOSIT', 'CASH_WITHDRAWAL', 'CHEQUE_DEPOSIT', 
                'CIF_CREATE', 'ACCOUNT_OPENING', 'ACCOUNT_MAINTENANCE', 'ACCOUNT_CLOSURE', 
                'MANDATE_MANAGEMENT', 'LOAN_APPLICATION', 'LOAN_DISBURSEMENT', 'LOAN_RESTRUCTURING', 
                'POLICY_SALE', 'CLAIMS_PROCESSING', 'PREMIUM_COLLECTION',
                'TELLER_CASH_ISSUE', 'TELLER_CASH_RECEIVE', 'VAULT_OPENING', 'VAULT_CLOSING',
                'ATM_CASH_LOADING', 'ATM_CASH_OFFLOADING', 
                'BANK_TRANSFER', 'MOBILE_MONEY_TRANSFER', 'BILL_PAYMENT', 'CDSC_TRANSFER',
                'OTHER'
            ) NOT NULL
        """)
        print("✅ Updated transaction_type enum successfully")
        
        # Verify the table structure
        cursor.execute("DESCRIBE authorization_queue")
        columns = cursor.fetchall()
        print("\n📊 Current table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Check current queue contents
        cursor.execute("SELECT COUNT(*) FROM authorization_queue WHERE status = 'PENDING'")
        pending_count = cursor.fetchone()[0]
        print(f"\n📋 Current pending items in queue: {pending_count}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Authorization queue table fixed successfully!")
        
    except Exception as e:
        print(f"❌ Error fixing authorization queue table: {e}")

if __name__ == "__main__":
    fix_authorization_queue_table()