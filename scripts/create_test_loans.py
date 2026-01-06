#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def create_test_loans():
    """Create test loan applications for ACC1000014"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root', 
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔄 Creating test loan applications...")
        
        # Create test loan applications for ACC1000014
        test_loans = [
            {
                'application_id': f'LA{datetime.now().strftime("%Y%m%d")}001',
                'account_number': 'ACC1000014',
                'loan_type': 'Personal Loan',
                'loan_amount': 50000,
                'interest_rate': 12.5,
                'tenure_months': 12,
                'purpose': 'Business Capital',
                'monthly_payment': 4500,
                'processing_fee': 2500
            },
            {
                'application_id': f'LA{datetime.now().strftime("%Y%m%d")}002', 
                'account_number': 'ACC1000014',
                'loan_type': 'Emergency Loan',
                'loan_amount': 25000,
                'interest_rate': 15.0,
                'tenure_months': 6,
                'purpose': 'Medical Emergency',
                'monthly_payment': 4500,
                'processing_fee': 1250
            },
            {
                'application_id': f'LA{datetime.now().strftime("%Y%m%d")}003',
                'account_number': 'ACC1000014', 
                'loan_type': 'Asset Finance',
                'loan_amount': 100000,
                'interest_rate': 14.0,
                'tenure_months': 24,
                'purpose': 'Equipment Purchase',
                'monthly_payment': 5200,
                'processing_fee': 5000
            }
        ]
        
        for loan in test_loans:
            cursor.execute("""
                INSERT INTO loan_applications (
                    application_id, account_number, customer_type, loan_type, loan_amount,
                    interest_rate, tenure_months, purpose, monthly_payment, processing_fee,
                    status, created_by, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                loan['application_id'], loan['account_number'], 'individual', 
                loan['loan_type'], loan['loan_amount'], loan['interest_rate'],
                loan['tenure_months'], loan['purpose'], loan['monthly_payment'],
                loan['processing_fee'], 'PENDING', 'CUSTOMER_14', datetime.now()
            ))
            print(f"✅ Created loan application: {loan['application_id']}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Created {len(test_loans)} test loan applications!")
        
    except Exception as e:
        print(f"❌ Error creating test loans: {e}")

if __name__ == "__main__":
    create_test_loans()