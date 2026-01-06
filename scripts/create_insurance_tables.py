#!/usr/bin/env python3

import mysql.connector
from datetime import datetime, timedelta

def create_insurance_tables():
    """Create insurance-related tables in the database"""
    try:
        # Connect to database
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🛡️ Creating additional insurance-related tables...")
        
        # 1. Premium Payments Table (if not exists)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS premium_payments (
                payment_id VARCHAR(20) PRIMARY KEY,
                policy_number VARCHAR(20) NOT NULL,
                payment_amount DECIMAL(15,2) NOT NULL,
                payment_date DATE NOT NULL,
                payment_method VARCHAR(50),
                due_date DATE,
                payment_period VARCHAR(50),
                processed_by VARCHAR(20),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_policy (policy_number),
                INDEX idx_payment_date (payment_date),
                INDEX idx_due_date (due_date)
            )
        """)
        print("✅ Created/verified premium_payments table")
        
        # 2. Agent Commissions Table (if not exists)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_commissions (
                commission_id INT AUTO_INCREMENT PRIMARY KEY,
                agent_code VARCHAR(20) NOT NULL,
                policy_number VARCHAR(20) NOT NULL,
                commission_type ENUM('FIRST_YEAR', 'RENEWAL', 'BONUS') DEFAULT 'FIRST_YEAR',
                commission_rate DECIMAL(5,2) NOT NULL,
                commission_amount DECIMAL(15,2) NOT NULL,
                premium_amount DECIMAL(15,2) NOT NULL,
                payment_date DATE,
                status ENUM('PENDING', 'PAID') DEFAULT 'PENDING',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_agent (agent_code),
                INDEX idx_policy (policy_number),
                INDEX idx_status (status)
            )
        """)
        print("✅ Created/verified agent_commissions table")
        
        # Insert sample policies using existing structure
        print("\n📋 Inserting sample insurance policies...")
        
        sample_policies = [
            ('POL20260104001', 'ACC1000014', 'PROD_LIFE001', 'Life Insurance', 500000, 25000, 'Monthly', 'Direct Debit', 20, '2026-01-04', '2046-01-04', 'Jane Doe', 'Spouse'),
            ('POL20260103002', 'ACC1000015', 'PROD_HEALTH001', 'Health Insurance', 300000, 24000, 'Quarterly', 'Bank Transfer', 10, '2026-01-03', '2036-01-03', 'John Smith Jr', 'Child'),
            ('POL20260102003', 'ACC1000016', 'PROD_EDU001', 'Education Plan', 150000, 9000, 'Annual', 'Cash', 15, '2026-01-02', '2041-01-02', 'Mary Johnson', 'Child'),
            ('POL20260101004', 'ACC1000017', 'PROD_PEN001', 'Pension Plan', 1000000, 40000, 'Monthly', 'Direct Debit', 25, '2026-01-01', '2051-01-01', 'Robert Wilson', 'Spouse')
        ]
        
        for policy in sample_policies:
            cursor.execute("""
                INSERT IGNORE INTO insurance_policies 
                (policy_number, account_number, product_id, policy_type, coverage_amount, 
                 annual_premium, payment_frequency, payment_method, policy_term_years, 
                 start_date, maturity_date, beneficiary_name, beneficiary_relationship, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'SYSTEM')
            """, policy)
        
        print(f"✅ Inserted {len(sample_policies)} sample policies")
        
        # Insert sample premium payments
        print("\n💰 Inserting sample premium payments...")
        
        sample_payments = [
            ('PRM20260104001', 'POL20260104001', 2083.33, '2026-01-04', 'Direct Debit', '2026-01-04', 'January 2026'),
            ('PRM20260103002', 'POL20260103002', 6000.00, '2026-01-03', 'Bank Transfer', '2026-01-03', 'Q1 2026'),
            ('PRM20260102003', 'POL20260102003', 9000.00, '2026-01-02', 'Cash', '2026-01-02', 'Annual 2026'),
            ('PRM20260101004', 'POL20260101004', 3333.33, '2026-01-01', 'Direct Debit', '2026-01-01', 'January 2026')
        ]
        
        for payment in sample_payments:
            cursor.execute("""
                INSERT IGNORE INTO premium_payments 
                (payment_id, policy_number, payment_amount, payment_date, payment_method, 
                 due_date, payment_period, processed_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'SYSTEM')
            """, payment)
        
        print(f"✅ Inserted {len(sample_payments)} sample premium payments")
        
        # Insert sample agent commissions
        print("\n💼 Inserting sample agent commissions...")
        
        sample_commissions = [
            ('SUP001', 'POL20260104001', 'FIRST_YEAR', 10.0, 2500.00, 25000),
            ('SUP001', 'POL20260103002', 'FIRST_YEAR', 8.0, 1920.00, 24000),
            ('SUP001', 'POL20260102003', 'FIRST_YEAR', 12.0, 1080.00, 9000),
            ('SUP001', 'POL20260101004', 'FIRST_YEAR', 15.0, 6000.00, 40000)
        ]
        
        for commission in sample_commissions:
            cursor.execute("""
                INSERT IGNORE INTO agent_commissions 
                (agent_code, policy_number, commission_type, commission_rate, 
                 commission_amount, premium_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, commission)
        
        print(f"✅ Inserted {len(sample_commissions)} sample commissions")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Insurance tables setup completed successfully!")
        print("\n📊 Summary:")
        print("- ✅ premium_payments table")
        print("- ✅ agent_commissions table")
        print("- ✅ Sample policies inserted")
        print("- ✅ Sample payments inserted")
        print("- ✅ Sample commissions inserted")
        
    except Exception as e:
        print(f"❌ Error setting up insurance tables: {e}")

if __name__ == "__main__":
    create_insurance_tables()