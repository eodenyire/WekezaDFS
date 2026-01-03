#!/usr/bin/env python3
"""
Reset Database - Clear everything and recreate tables
"""

import mysql.connector
import sys

def reset_database():
    """Clear all data and recreate tables"""
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🗑️ Clearing all existing data...")
        
        # Drop all tables in correct order (foreign keys first)
        tables_to_drop = [
            'transactions',
            'user_policies', 
            'loans',
            'risk_scores',
            'bulk_transfers',
            'accounts',
            'users',
            'businesses'
        ]
        
        for table in tables_to_drop:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                print(f"   ✅ Dropped {table}")
            except Exception as e:
                print(f"   ⚠️ {table}: {e}")
        
        print("\n🏗️ Creating fresh table structure...")
        
        # Create businesses table
        cursor.execute("""
        CREATE TABLE businesses (
            business_id INT AUTO_INCREMENT PRIMARY KEY,
            business_name VARCHAR(100) NOT NULL,
            registration_no VARCHAR(50) UNIQUE NOT NULL,
            kra_pin VARCHAR(20) UNIQUE NOT NULL,
            sector VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        print("   ✅ Created businesses table")
        
        # Create users table
        cursor.execute("""
        CREATE TABLE users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            full_name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            phone_number VARCHAR(15) UNIQUE,
            national_id VARCHAR(20) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            kyc_tier ENUM('TIER_1', 'TIER_2', 'TIER_3') DEFAULT 'TIER_1',
            is_active BOOLEAN DEFAULT TRUE,
            business_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses(business_id)
        )
        """)
        print("   ✅ Created users table")
        
        # Create accounts table
        cursor.execute("""
        CREATE TABLE accounts (
            account_id INT AUTO_INCREMENT PRIMARY KEY,
            account_number VARCHAR(20) UNIQUE NOT NULL,
            balance DECIMAL(15,2) DEFAULT 0.00,
            currency VARCHAR(3) DEFAULT 'KES',
            status ENUM('ACTIVE', 'FROZEN', 'DISABLED', 'DORMANT') DEFAULT 'ACTIVE',
            user_id INT NULL,
            business_id INT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (business_id) REFERENCES businesses(business_id)
        )
        """)
        print("   ✅ Created accounts table")
        
        # Create loans table
        cursor.execute("""
        CREATE TABLE loans (
            loan_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            principal_amount DECIMAL(15,2) NOT NULL,
            total_due_amount DECIMAL(15,2) NOT NULL,
            balance_remaining DECIMAL(15,2) NOT NULL,
            status ENUM('PENDING', 'ACTIVE', 'PAID', 'DEFAULTED', 'APPROVED', 'REJECTED') DEFAULT 'PENDING',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        print("   ✅ Created loans table")
        
        # Create user_policies table
        cursor.execute("""
        CREATE TABLE user_policies (
            policy_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            business_id INT NULL,
            product_code VARCHAR(20) NOT NULL,
            policy_number VARCHAR(50) UNIQUE NOT NULL,
            premium_paid DECIMAL(15,2) DEFAULT 0.00,
            cover_amount DECIMAL(15,2) DEFAULT 0.00,
            status VARCHAR(20) DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (business_id) REFERENCES businesses(business_id)
        )
        """)
        print("   ✅ Created user_policies table")
        
        # Create transactions table
        cursor.execute("""
        CREATE TABLE transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            account_id INT NOT NULL,
            txn_type VARCHAR(50) NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            reference_code VARCHAR(50) UNIQUE NOT NULL,
            description VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id)
        )
        """)
        print("   ✅ Created transactions table")
        
        # Create risk_scores table
        cursor.execute("""
        CREATE TABLE risk_scores (
            score_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            credit_score INT NOT NULL,
            decision VARCHAR(20) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        print("   ✅ Created risk_scores table")
        
        # Create bulk_transfers table
        cursor.execute("""
        CREATE TABLE bulk_transfers (
            batch_id INT AUTO_INCREMENT PRIMARY KEY,
            business_id INT NOT NULL,
            total_amount DECIMAL(15,2) NOT NULL,
            status VARCHAR(20) DEFAULT 'PENDING',
            description VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (business_id) REFERENCES businesses(business_id)
        )
        """)
        print("   ✅ Created bulk_transfers table")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Database reset complete!")
        print("✅ All tables created with proper structure")
        print("✅ Database is clean and ready for use")
        
    except Exception as e:
        print(f"❌ Database reset failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    reset_database()