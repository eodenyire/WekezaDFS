#!/usr/bin/env python3
"""
Script to create the fixed_deposits table if it doesn't exist
"""

import mysql.connector
from datetime import datetime

def get_db_connection():
    """Get database connection"""
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def create_fixed_deposits_table():
    """Create fixed_deposits table if it doesn't exist"""
    try:
        conn = get_db_connection()
        if not conn:
            return False
        
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'fixed_deposits'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            print("✅ fixed_deposits table already exists")
            conn.close()
            return True
        
        # Create the table
        create_table_sql = """
        CREATE TABLE fixed_deposits (
            fd_id INT AUTO_INCREMENT PRIMARY KEY,
            fd_number VARCHAR(50) UNIQUE NOT NULL,
            account_id INT NOT NULL,
            principal_amount DECIMAL(15,2) NOT NULL,
            interest_rate DECIMAL(5,2) NOT NULL,
            term_months INT NOT NULL,
            start_date DATE NOT NULL,
            maturity_date DATE NOT NULL,
            maturity_amount DECIMAL(15,2) NOT NULL,
            auto_renew BOOLEAN DEFAULT FALSE,
            status ENUM('ACTIVE', 'MATURED', 'CLOSED', 'RENEWED') DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (account_id) REFERENCES accounts(account_id) ON DELETE CASCADE,
            INDEX idx_fd_number (fd_number),
            INDEX idx_account_id (account_id),
            INDEX idx_status (status),
            INDEX idx_maturity_date (maturity_date)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        
        print("✅ fixed_deposits table created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error creating fixed_deposits table: {e}")
        return False

if __name__ == "__main__":
    print("Creating fixed_deposits table...")
    success = create_fixed_deposits_table()
    if success:
        print("✅ Database setup completed successfully")
    else:
        print("❌ Database setup failed")