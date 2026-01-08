#!/usr/bin/env python3
"""
Fix branch operations alignment with other portals
"""

import mysql.connector
import os
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
        print(f"❌ Database connection failed: {e}")
        return None

def create_customers_table():
    """Create customers table for CIF management"""
    print("🔧 Creating customers table...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SHOW TABLES LIKE 'customers'")
        if cursor.fetchone():
            print("✅ customers table already exists")
            conn.close()
            return True
        
        # Create customers table
        create_table_sql = """
        CREATE TABLE customers (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            cif_number VARCHAR(20) UNIQUE NOT NULL,
            full_name VARCHAR(255) NOT NULL,
            national_id VARCHAR(20) UNIQUE NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            email VARCHAR(255),
            date_of_birth DATE,
            physical_address TEXT,
            postal_address VARCHAR(255),
            kyc_tier ENUM('TIER_1', 'TIER_2', 'TIER_3') DEFAULT 'TIER_1',
            occupation VARCHAR(255),
            employer VARCHAR(255),
            monthly_income DECIMAL(15,2) DEFAULT 0.00,
            customer_type ENUM('individual', 'business') DEFAULT 'individual',
            status ENUM('ACTIVE', 'INACTIVE', 'SUSPENDED') DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            created_by VARCHAR(50),
            INDEX idx_cif_number (cif_number),
            INDEX idx_national_id (national_id),
            INDEX idx_phone_number (phone_number),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """
        
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ customers table created successfully")
        
        # Insert some test customers for alignment
        test_customers = [
            ('CIF123456', 'John Doe', '12345678', '+254712345678', 'john@email.com', '1990-01-15', 'Nairobi', 'P.O. Box 123', 'TIER_2', 'Engineer', 'Tech Corp', 75000.00),
            ('CIF789012', 'Alice Wanjiku', '87654321', '+254723456789', 'alice@email.com', '1985-05-20', 'Mombasa', 'P.O. Box 456', 'TIER_2', 'Teacher', 'School', 45000.00),
            ('CIF555666', 'Peter Kamau', '11223344', '+254734567890', 'peter@email.com', '1992-08-10', 'Kisumu', 'P.O. Box 789', 'TIER_1', 'Trader', 'Self', 30000.00)
        ]
        
        for customer in test_customers:
            cursor.execute("""
                INSERT INTO customers (cif_number, full_name, national_id, phone_number, email, 
                                     date_of_birth, physical_address, postal_address, kyc_tier, 
                                     occupation, employer, monthly_income, created_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'SYSTEM_INIT')
            """, customer)
        
        conn.commit()
        print("✅ Test customers inserted")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating customers table: {e}")
        conn.close()
        return False

def main():
    """Main function"""
    print("🔧 FIXING BRANCH OPERATIONS ALIGNMENT")
    print("=" * 50)
    
    success = create_customers_table()
    
    if success:
        print("\n✅ Branch operations alignment fixes completed!")
        print("📋 Next steps:")
        print("1. Update branch operations CIF creation to use database")
        print("2. Update CIF search to query database")
        print("3. Ensure all portals use same customer data")
    else:
        print("\n❌ Branch operations alignment fixes failed!")
    
    return success

if __name__ == "__main__":
    main()