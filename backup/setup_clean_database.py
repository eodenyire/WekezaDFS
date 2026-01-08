#!/usr/bin/env python3
"""
Setup Clean Database - Clear data and ensure proper table structure
"""

import mysql.connector
import sys

def setup_clean_database():
    """Clear data and ensure proper table structure"""
    
    try:
        # Connect to MySQL
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🧹 Setting up clean database...")
        
        # Step 1: Clear all data (in correct order due to foreign keys)
        print("\n1️⃣ Clearing existing data...")
        
        # Disable foreign key checks temporarily
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Clear data from all tables
        tables_to_clear = [
            'transactions',
            'user_policies', 
            'loans',
            'risk_scores',
            'bulk_transfers',
            'accounts',
            'users',
            'businesses'
        ]
        
        for table in tables_to_clear:
            try:
                cursor.execute(f"DELETE FROM {table}")
                print(f"   ✅ Cleared {table}")
            except Exception as e:
                print(f"   ⚠️ {table}: {e}")
        
        # Re-enable foreign key checks
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Step 2: Ensure all required tables exist
        print("\n2️⃣ Ensuring table structure...")
        
        # Check if businesses table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'businesses'")
        if not cursor.fetchone():
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
        else:
            print("   ✅ businesses table exists")
        
        # Check if users table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            cursor.execute("""
            CREATE TABLE users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                full_name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(15),
                national_id VARCHAR(20),
                password_hash VARCHAR(255) NOT NULL,
                kyc_tier ENUM('TIER_1', 'TIER_2', 'TIER_3') DEFAULT 'TIER_1',
                is_active BOOLEAN DEFAULT TRUE,
                business_id INT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (business_id) REFERENCES businesses(business_id)
            )
            """)
            print("   ✅ Created users table")
        else:
            print("   ✅ users table exists")
        
        # Check if accounts table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'accounts'")
        if not cursor.fetchone():
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
        else:
            print("   ✅ accounts table exists")
        
        # Check if loans table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'loans'")
        if not cursor.fetchone():
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
        else:
            print("   ✅ loans table exists")
        
        # Check if transactions table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'transactions'")
        if not cursor.fetchone():
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
        else:
            print("   ✅ transactions table exists")
        
        # Check if user_policies table exists, create if not
        cursor.execute("SHOW TABLES LIKE 'user_policies'")
        if not cursor.fetchone():
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
        else:
            print("   ✅ user_policies table exists")
        
        # Step 3: Verify the setup
        print("\n3️⃣ Verifying setup...")
        
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"   📋 Found {len(tables)} tables:")
        
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"      - {table_name}: {count} records")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Database setup complete!")
        print("✅ All data cleared")
        print("✅ All required tables exist")
        print("✅ Ready for admin panel to create users")
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_clean_database()