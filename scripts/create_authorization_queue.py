#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def create_authorization_queue_table():
    """Create authorization queue table for maker-checker workflow"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🏦 Creating authorization queue table...")
        
        # Create authorization_queue table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authorization_queue (
                queue_id VARCHAR(20) PRIMARY KEY,
                transaction_type ENUM('CASH_DEPOSIT', 'CASH_WITHDRAWAL', 'CHEQUE_DEPOSIT', 'CIF_CREATE', 
                                    'ACCOUNT_OPENING', 'ACCOUNT_MAINTENANCE', 'ACCOUNT_CLOSURE', 'MANDATE_MANAGEMENT',
                                    'LOAN_APPLICATION', 'LOAN_DISBURSEMENT', 'LOAN_RESTRUCTURING', 'LOAN_SETUP',
                                    'POLICY_SALE', 'CLAIMS_PROCESSING', 'PREMIUM_COLLECTION',
                                    'TELLER_CASH_ISSUE', 'TELLER_CASH_RECEIVE', 'VAULT_OPENING', 'VAULT_CLOSING',
                                    'ATM_CASH_LOADING', 'ATM_CASH_OFFLOADING', 'OTHER') NOT NULL,
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
        print("✅ Created authorization_queue table")
        
        # Insert sample pending loan applications into queue
        print("\n📋 Adding existing pending loans to authorization queue...")
        
        # Get existing pending loan applications
        cursor.execute("""
            SELECT la.application_id, la.loan_amount, la.created_by, la.loan_type, 
                   la.account_number, u.full_name, la.created_at
            FROM loan_applications la
            LEFT JOIN accounts a ON la.account_number = a.account_number
            LEFT JOIN users u ON a.user_id = u.user_id
            WHERE la.status = 'PENDING'
        """)
        
        pending_loans = cursor.fetchall()
        
        for loan in pending_loans:
            queue_id = f"AQ{datetime.now().strftime('%Y%m%d')}{loan[0][-6:]}"  # Use last 6 chars of app_id
            
            cursor.execute("""
                INSERT IGNORE INTO authorization_queue 
                (queue_id, transaction_type, reference_id, maker_id, maker_name, 
                 amount, description, branch_code, status, priority, created_at)
                VALUES (%s, 'LOAN', %s, %s, %s, %s, %s, %s, 'PENDING', 'HIGH', %s)
            """, (
                queue_id, loan[0], loan[2], loan[5] or 'Unknown', loan[1],
                f"Loan Application - {loan[3]} for Account {loan[4]}", 
                'MAIN', loan[6]
            ))
        
        print(f"✅ Added {len(pending_loans)} pending loans to authorization queue")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Authorization queue table created successfully!")
        print("\n📊 Summary:")
        print("- ✅ authorization_queue table created")
        print("- ✅ Existing pending loans added to queue")
        print("- ✅ Ready for maker-checker workflow")
        
    except Exception as e:
        print(f"❌ Error creating authorization queue table: {e}")

if __name__ == "__main__":
    create_authorization_queue_table()