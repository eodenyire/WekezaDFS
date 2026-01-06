#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def recreate_authorization_queue_table():
    """Recreate authorization queue table with proper structure"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔄 Recreating authorization queue table...")
        
        # First, backup existing data
        print("💾 Backing up existing data...")
        cursor.execute("SELECT * FROM authorization_queue")
        existing_data = cursor.fetchall()
        print(f"📋 Found {len(existing_data)} existing records")
        
        # Drop the existing table
        cursor.execute("DROP TABLE IF EXISTS authorization_queue")
        print("🗑️ Dropped existing table")
        
        # Create new table with correct structure
        cursor.execute("""
            CREATE TABLE authorization_queue (
                queue_id VARCHAR(20) PRIMARY KEY,
                transaction_type ENUM(
                    'CASH_DEPOSIT', 'CASH_WITHDRAWAL', 'CHEQUE_DEPOSIT', 
                    'CIF_CREATE', 'ACCOUNT_OPENING', 'ACCOUNT_MAINTENANCE', 'ACCOUNT_CLOSURE', 
                    'MANDATE_MANAGEMENT', 'LOAN_APPLICATION', 'LOAN_DISBURSEMENT', 'LOAN_RESTRUCTURING', 
                    'POLICY_SALE', 'CLAIMS_PROCESSING', 'PREMIUM_COLLECTION',
                    'TELLER_CASH_ISSUE', 'TELLER_CASH_RECEIVE', 'VAULT_OPENING', 'VAULT_CLOSING',
                    'ATM_CASH_LOADING', 'ATM_CASH_OFFLOADING', 
                    'BANK_TRANSFER', 'MOBILE_MONEY_TRANSFER', 'BILL_PAYMENT', 'CDSC_TRANSFER',
                    'OTHER'
                ) NOT NULL,
                reference_id VARCHAR(20) NOT NULL,
                maker_id VARCHAR(20) NOT NULL,
                maker_name VARCHAR(255),
                amount DECIMAL(15,2) NOT NULL,
                description TEXT,
                branch_code VARCHAR(10),
                status ENUM('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
                priority ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT') DEFAULT 'MEDIUM',
                operation_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                approved_by VARCHAR(20),
                approved_at DATETIME,
                rejection_reason TEXT,
                INDEX idx_status (status),
                INDEX idx_type (transaction_type),
                INDEX idx_maker (maker_id),
                INDEX idx_created_at (created_at),
                INDEX idx_branch (branch_code)
            )
        """)
        print("✅ Created new authorization_queue table")
        
        # Restore data with corrected transaction types
        restored_count = 0
        for row in existing_data:
            # Convert old data format to new format
            queue_id = row[0]
            transaction_type = 'LOAN_APPLICATION' if row[1] == 'LOAN' else row[1]
            reference_id = row[2]
            maker_id = row[3]
            maker_name = row[4]
            amount = row[5]
            description = row[6]
            branch_code = row[7]
            status = row[8]
            priority = row[9]
            operation_data = row[10] if len(row) > 10 else None
            created_at = row[11] if len(row) > 11 else datetime.now()
            approved_by = row[12] if len(row) > 12 else None
            approved_at = row[13] if len(row) > 13 else None
            rejection_reason = row[14] if len(row) > 14 else None
            
            cursor.execute("""
                INSERT INTO authorization_queue 
                (queue_id, transaction_type, reference_id, maker_id, maker_name, 
                 amount, description, branch_code, status, priority, operation_data,
                 created_at, approved_by, approved_at, rejection_reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                queue_id, transaction_type, reference_id, maker_id, maker_name,
                amount, description, branch_code, status, priority, operation_data,
                created_at, approved_by, approved_at, rejection_reason
            ))
            restored_count += 1
        
        print(f"✅ Restored {restored_count} records with corrected transaction types")
        
        # Verify the table structure
        cursor.execute("DESCRIBE authorization_queue")
        columns = cursor.fetchall()
        print("\n📊 New table structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
        
        # Check current queue contents
        cursor.execute("SELECT COUNT(*) FROM authorization_queue WHERE status = 'PENDING'")
        pending_count = cursor.fetchone()[0]
        print(f"\n📋 Current pending items in queue: {pending_count}")
        
        if pending_count > 0:
            cursor.execute("""
                SELECT queue_id, transaction_type, reference_id, amount, status 
                FROM authorization_queue 
                WHERE status = 'PENDING' 
                ORDER BY created_at
            """)
            pending_items = cursor.fetchall()
            print("\n📋 Pending items:")
            for item in pending_items:
                print(f"  - {item[0]}: {item[1]} - {item[2]} - KES {item[3]:,.2f} - {item[4]}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Authorization queue table recreated successfully!")
        print("\n📊 Summary:")
        print("- ✅ Table recreated with proper structure")
        print("- ✅ operation_data column included")
        print("- ✅ All new transaction types supported")
        print("- ✅ Existing data restored and corrected")
        print("- ✅ Ready for comprehensive maker-checker workflow")
        
    except Exception as e:
        print(f"❌ Error recreating authorization queue table: {e}")

if __name__ == "__main__":
    recreate_authorization_queue_table()