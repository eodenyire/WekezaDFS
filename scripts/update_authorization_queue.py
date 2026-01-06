#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def update_authorization_queue_table():
    """Update authorization queue table with missing columns and new operation types"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔄 Updating authorization queue table...")
        
        # Check if operation_data column exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'wekeza_dfs_db' 
            AND TABLE_NAME = 'authorization_queue' 
            AND COLUMN_NAME = 'operation_data'
        """)
        
        if not cursor.fetchone():
            print("➕ Adding operation_data column...")
            cursor.execute("""
                ALTER TABLE authorization_queue 
                ADD COLUMN operation_data TEXT AFTER priority
            """)
            print("✅ Added operation_data column")
        else:
            print("✅ operation_data column already exists")
        
        # Update transaction_type enum to include new types
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
        print("✅ Updated transaction_type enum with new operation types")
        
        # Fix existing LOAN entries to LOAN_APPLICATION
        cursor.execute("""
            UPDATE authorization_queue 
            SET transaction_type = 'LOAN_APPLICATION' 
            WHERE transaction_type = 'LOAN'
        """)
        updated_rows = cursor.rowcount
        if updated_rows > 0:
            print(f"✅ Updated {updated_rows} existing LOAN entries to LOAN_APPLICATION")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Authorization queue table updated successfully!")
        print("\n📊 Summary:")
        print("- ✅ operation_data column added/verified")
        print("- ✅ transaction_type enum updated with new operation types")
        print("- ✅ Existing LOAN entries fixed to LOAN_APPLICATION")
        print("- ✅ Ready for comprehensive maker-checker workflow")
        
    except Exception as e:
        print(f"❌ Error updating authorization queue table: {e}")

if __name__ == "__main__":
    update_authorization_queue_table()