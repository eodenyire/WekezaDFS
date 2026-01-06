#!/usr/bin/env python3

import mysql.connector
from datetime import datetime

def create_loan_tables():
    """Create loan-related tables in the database"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🏦 Creating loan-related tables...")
        
        # 1. Loan Applications Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_applications (
                application_id VARCHAR(20) PRIMARY KEY,
                account_number VARCHAR(20) NOT NULL,
                customer_type ENUM('individual', 'business') DEFAULT 'individual',
                loan_type VARCHAR(100) NOT NULL,
                loan_amount DECIMAL(15,2) NOT NULL,
                interest_rate DECIMAL(5,2) NOT NULL,
                tenure_months INT NOT NULL,
                purpose TEXT,
                collateral_type VARCHAR(100),
                monthly_payment DECIMAL(15,2),
                processing_fee DECIMAL(15,2),
                status ENUM('PENDING', 'APPROVED', 'REJECTED', 'DISBURSED') DEFAULT 'PENDING',
                created_by VARCHAR(20),
                approved_by VARCHAR(20),
                approved_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_account (account_number),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            )
        """)
        print("✅ Created loan_applications table")
        
        # 2. Loan Accounts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_accounts (
                loan_id VARCHAR(20) PRIMARY KEY,
                application_id VARCHAR(20),
                account_number VARCHAR(20) NOT NULL,
                customer_name VARCHAR(255) NOT NULL,
                loan_type VARCHAR(100) NOT NULL,
                principal_amount DECIMAL(15,2) NOT NULL,
                outstanding_balance DECIMAL(15,2) NOT NULL,
                interest_rate DECIMAL(5,2) NOT NULL,
                tenure_months INT NOT NULL,
                monthly_payment DECIMAL(15,2) NOT NULL,
                next_payment_date DATE,
                disbursement_date DATE,
                maturity_date DATE,
                status ENUM('ACTIVE', 'CLOSED', 'DEFAULTED', 'RESTRUCTURED') DEFAULT 'ACTIVE',
                days_overdue INT DEFAULT 0,
                created_by VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (application_id) REFERENCES loan_applications(application_id),
                INDEX idx_account (account_number),
                INDEX idx_status (status),
                INDEX idx_next_payment (next_payment_date)
            )
        """)
        print("✅ Created loan_accounts table")
        
        # 3. Loan Payments Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_payments (
                payment_id VARCHAR(20) PRIMARY KEY,
                loan_id VARCHAR(20) NOT NULL,
                payment_amount DECIMAL(15,2) NOT NULL,
                principal_amount DECIMAL(15,2) NOT NULL,
                interest_amount DECIMAL(15,2) NOT NULL,
                penalty_amount DECIMAL(15,2) DEFAULT 0,
                payment_method VARCHAR(50),
                payment_date DATE NOT NULL,
                processed_by VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (loan_id) REFERENCES loan_accounts(loan_id),
                INDEX idx_loan (loan_id),
                INDEX idx_payment_date (payment_date)
            )
        """)
        print("✅ Created loan_payments table")
        
        # 4. Loan Products Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_products (
                product_id VARCHAR(20) PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                target_customer ENUM('individual', 'business', 'both') DEFAULT 'both',
                min_amount DECIMAL(15,2) NOT NULL,
                max_amount DECIMAL(15,2) NOT NULL,
                base_interest_rate DECIMAL(5,2) NOT NULL,
                max_tenure_months INT NOT NULL,
                processing_fee_rate DECIMAL(5,2) NOT NULL,
                min_income DECIMAL(15,2),
                min_age INT,
                max_age INT,
                min_credit_score INT,
                required_documents TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_by VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_target (target_customer),
                INDEX idx_active (is_active)
            )
        """)
        print("✅ Created loan_products table")
        
        # 5. Loan Restructuring Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS loan_restructuring (
                restructure_id VARCHAR(20) PRIMARY KEY,
                loan_id VARCHAR(20) NOT NULL,
                old_balance DECIMAL(15,2) NOT NULL,
                new_balance DECIMAL(15,2) NOT NULL,
                old_interest_rate DECIMAL(5,2) NOT NULL,
                new_interest_rate DECIMAL(5,2) NOT NULL,
                old_tenure_months INT NOT NULL,
                new_tenure_months INT NOT NULL,
                old_monthly_payment DECIMAL(15,2) NOT NULL,
                new_monthly_payment DECIMAL(15,2) NOT NULL,
                grace_period_months INT DEFAULT 0,
                restructure_reason VARCHAR(255) NOT NULL,
                processed_by VARCHAR(20),
                processed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (loan_id) REFERENCES loan_accounts(loan_id),
                INDEX idx_loan (loan_id),
                INDEX idx_processed_at (processed_at)
            )
        """)
        print("✅ Created loan_restructuring table")
        
        # Insert sample loan products
        print("\n📦 Inserting sample loan products...")
        
        # Individual loan products
        individual_products = [
            ('PROD001', 'Personal Loan', 'individual', 5000, 500000, 15.0, 60, 2.5, 20000, 21, 65, 600),
            ('PROD002', 'Salary Advance', 'individual', 1000, 100000, 12.0, 12, 1.5, 15000, 21, 65, 550),
            ('PROD003', 'Emergency Loan', 'individual', 2000, 50000, 18.0, 24, 3.0, 10000, 18, 70, 500),
            ('PROD004', 'Asset Finance', 'individual', 50000, 2000000, 14.0, 84, 2.0, 30000, 25, 65, 650),
            ('PROD005', 'Mortgage Loan', 'individual', 500000, 10000000, 13.5, 300, 1.0, 100000, 25, 65, 700)
        ]
        
        # Business loan products
        business_products = [
            ('PROD006', 'Working Capital Loan', 'business', 50000, 5000000, 16.0, 36, 2.0, 0, 0, 0, 600),
            ('PROD007', 'Trade Finance', 'business', 100000, 10000000, 14.5, 12, 1.5, 0, 0, 0, 650),
            ('PROD008', 'Equipment Finance', 'business', 200000, 20000000, 15.0, 60, 2.5, 0, 0, 0, 650),
            ('PROD009', 'Invoice Discounting', 'business', 50000, 3000000, 17.0, 6, 1.0, 0, 0, 0, 600),
            ('PROD010', 'SME Growth Loan', 'business', 100000, 8000000, 15.5, 48, 2.0, 0, 0, 0, 650)
        ]
        
        for product in individual_products + business_products:
            cursor.execute("""
                INSERT IGNORE INTO loan_products 
                (product_id, product_name, target_customer, min_amount, max_amount, 
                 base_interest_rate, max_tenure_months, processing_fee_rate, 
                 min_income, min_age, max_age, min_credit_score, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'SYSTEM')
            """, product)
        
        print(f"✅ Inserted {len(individual_products + business_products)} loan products")
        
        # Insert sample loan applications
        print("\n📋 Inserting sample loan applications...")
        
        sample_applications = [
            ('LA20260104001', 'ACC1000014', 'individual', 'Personal Loan', 100000, 15.0, 24, 'Home renovation', 'Property Title', 'APPROVED'),
            ('LA20260104002', 'ACC1000015', 'individual', 'Salary Advance', 25000, 12.0, 6, 'Emergency expenses', 'Salary Assignment', 'PENDING'),
            ('LA20260104003', 'ACC1000016', 'business', 'Working Capital Loan', 500000, 16.0, 12, 'Inventory purchase', 'Business Assets', 'APPROVED'),
            ('LA20260104004', 'ACC1000017', 'individual', 'Asset Finance', 200000, 14.0, 36, 'Vehicle purchase', 'Vehicle Logbook', 'DISBURSED')
        ]
        
        for app in sample_applications:
            cursor.execute("""
                INSERT IGNORE INTO loan_applications 
                (application_id, account_number, customer_type, loan_type, loan_amount, 
                 interest_rate, tenure_months, purpose, collateral_type, status, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'SYSTEM')
            """, app)
        
        print(f"✅ Inserted {len(sample_applications)} sample loan applications")
        
        # Insert sample active loans
        print("\n💰 Inserting sample active loans...")
        
        sample_loans = [
            ('LN20260104001', 'LA20260104001', 'ACC1000014', 'Emmanuel Odenyire Anyira', 'Personal Loan', 100000, 85000, 15.0, 24, 4850.50, '2026-01-15', '2026-01-04', '2028-01-04'),
            ('LN20260104002', 'LA20260104003', 'ACC1000016', 'Business Customer Ltd', 'Working Capital Loan', 500000, 450000, 16.0, 12, 45238.50, '2026-01-20', '2026-01-03', '2027-01-03'),
            ('LN20260104003', 'LA20260104004', 'ACC1000017', 'Mary Wanjiku', 'Asset Finance', 200000, 175000, 14.0, 36, 6789.25, '2026-01-25', '2026-01-02', '2029-01-02')
        ]
        
        for loan in sample_loans:
            cursor.execute("""
                INSERT IGNORE INTO loan_accounts 
                (loan_id, application_id, account_number, customer_name, loan_type, 
                 principal_amount, outstanding_balance, interest_rate, tenure_months, 
                 monthly_payment, next_payment_date, disbursement_date, maturity_date, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'SYSTEM')
            """, loan)
        
        print(f"✅ Inserted {len(sample_loans)} sample active loans")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 All loan tables created successfully!")
        print("\n📊 Summary:")
        print("- ✅ loan_applications table")
        print("- ✅ loan_accounts table") 
        print("- ✅ loan_payments table")
        print("- ✅ loan_products table")
        print("- ✅ loan_restructuring table")
        print("- ✅ Sample data inserted")
        
    except Exception as e:
        print(f"❌ Error creating loan tables: {e}")

if __name__ == "__main__":
    create_loan_tables()