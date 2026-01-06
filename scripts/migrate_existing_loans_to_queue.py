#!/usr/bin/env python3

import mysql.connector
from datetime import datetime
import uuid

def migrate_existing_loans_to_queue():
    """
    Migrate existing pending loans from loan_applications table to authorization_queue
    and remove them from loan_applications until approved
    """
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor(dictionary=True)
        
        print("🔄 Migrating existing pending loans to authorization queue...")
        
        # Get all existing pending loans
        cursor.execute("""
            SELECT la.*, u.full_name as customer_name
            FROM loan_applications la
            LEFT JOIN accounts a ON la.account_number = a.account_number
            LEFT JOIN users u ON a.user_id = u.user_id
            WHERE la.status = 'PENDING'
        """)
        
        pending_loans = cursor.fetchall()
        print(f"📋 Found {len(pending_loans)} pending loans to migrate")
        
        for loan in pending_loans:
            # Create operation data
            operation_data = {
                "application_id": loan['application_id'],
                "account_number": loan['account_number'],
                "customer_type": loan.get('customer_type', 'individual'),
                "loan_type": loan['loan_type'],
                "loan_amount": float(loan['loan_amount']) if loan['loan_amount'] else 0.0,
                "interest_rate": float(loan['interest_rate']) if loan['interest_rate'] else 0.0,
                "tenure_months": loan['tenure_months'] if loan['tenure_months'] else 12,
                "purpose": loan.get('purpose', ''),
                "monthly_payment": float(loan['monthly_payment']) if loan.get('monthly_payment') else 0.0,
                "processing_fee": float(loan['processing_fee']) if loan.get('processing_fee') else 0.0,
                "created_by": loan.get('created_by', 'SYSTEM'),
                "original_created_at": loan['created_at'].isoformat() if loan.get('created_at') else datetime.now().isoformat()
            }
            
            # Generate queue ID
            queue_id = f"AQ{datetime.now().strftime('%Y%m%d')}{loan['application_id'][-6:]}"
            loan_amount = float(loan['loan_amount']) if loan['loan_amount'] else 0.0
            priority = 'HIGH' if loan_amount > 100000 else 'MEDIUM'
            
            # Check if already in queue
            cursor.execute("SELECT queue_id FROM authorization_queue WHERE reference_id = %s", (loan['application_id'],))
            existing = cursor.fetchone()
            
            if not existing:
                # Add to authorization queue
                cursor.execute("""
                    INSERT INTO authorization_queue 
                    (queue_id, transaction_type, reference_id, maker_id, maker_name, 
                     amount, description, branch_code, status, priority, operation_data, created_at)
                    VALUES (%s, 'LOAN_APPLICATION', %s, %s, %s, %s, %s, %s, 'PENDING', %s, %s, %s)
                """, (
                    queue_id, loan['application_id'], 
                    loan.get('created_by', 'SYSTEM'), 
                    loan.get('customer_name', 'Unknown Customer'),
                    loan_amount, 
                    f"Loan Application - {loan['loan_type']} for Account {loan['account_number']}",
                    'MAIN', priority, str(operation_data), 
                    loan.get('created_at', datetime.now())
                ))
                
                print(f"✅ Migrated loan {loan['application_id']} to queue {queue_id}")
            else:
                print(f"⚠️ Loan {loan['application_id']} already in queue")
        
        # Remove the pending loans from loan_applications table
        # They will be recreated when approved
        cursor.execute("DELETE FROM loan_applications WHERE status = 'PENDING'")
        deleted_count = cursor.rowcount
        
        print(f"🗑️ Removed {deleted_count} pending loans from loan_applications table")
        print("📋 These loans will be recreated when supervisor approves them")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Migration completed successfully!")
        print("\n📊 Summary:")
        print(f"- ✅ {len(pending_loans)} loans migrated to authorization queue")
        print(f"- 🗑️ {deleted_count} pending loans removed from loan_applications")
        print("- 📋 Loans will be recreated upon supervisor approval")
        print("- 🔄 Personal banking portal now uses authorization queue")
        
    except Exception as e:
        print(f"❌ Error migrating loans: {e}")

if __name__ == "__main__":
    migrate_existing_loans_to_queue()