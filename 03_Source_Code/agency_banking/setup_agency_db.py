"""
Database setup script for Agency Banking System
Creates all necessary tables and initial data
"""

import mysql.connector
from datetime import datetime
import hashlib

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='wekeza_dfs_db'
    )

def create_agency_tables():
    """Create all agency banking tables"""
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Agents table - Core agent information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id VARCHAR(20) PRIMARY KEY,
            agent_name VARCHAR(100) NOT NULL,
            national_id VARCHAR(20) UNIQUE NOT NULL,
            phone_number VARCHAR(15) UNIQUE NOT NULL,
            email VARCHAR(100),
            business_name VARCHAR(100) NOT NULL,
            business_location TEXT,
            agent_type ENUM('SUPER_AGENT', 'SUB_AGENT', 'RETAILER') NOT NULL,
            parent_agent_id VARCHAR(20),
            pin_hash VARCHAR(64) NOT NULL,
            daily_limit DECIMAL(15,2) DEFAULT 500000.00,
            transaction_limit DECIMAL(15,2) DEFAULT 50000.00,
            float_balance DECIMAL(15,2) DEFAULT 0.00,
            commission_rate DECIMAL(5,4) DEFAULT 0.0050,
            status ENUM('PENDING_APPROVAL', 'ACTIVE', 'SUSPENDED', 'TERMINATED') DEFAULT 'PENDING_APPROVAL',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_by VARCHAR(50),
            approved_by VARCHAR(50),
            approved_at TIMESTAMP NULL,
            suspended_by VARCHAR(50),
            suspended_at TIMESTAMP NULL,
            last_login TIMESTAMP NULL,
            INDEX idx_agent_type (agent_type),
            INDEX idx_status (status),
            INDEX idx_parent (parent_agent_id),
            FOREIGN KEY (parent_agent_id) REFERENCES agents(agent_id) ON DELETE SET NULL
        )
    """)
    
    # 2. Agent devices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_devices (
            device_id VARCHAR(50) PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            device_type ENUM('POS', 'MOBILE', 'TABLET', 'WEB') NOT NULL,
            device_model VARCHAR(100),
            serial_number VARCHAR(100),
            is_active BOOLEAN DEFAULT TRUE,
            last_location_lat DECIMAL(10,8),
            last_location_lng DECIMAL(11,8),
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP NULL,
            INDEX idx_agent_device (agent_id),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
        )
    """)
    
    # 3. Agent KYC documents
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_kyc_documents (
            document_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            document_type ENUM('NATIONAL_ID', 'BUSINESS_PERMIT', 'TAX_PIN', 'BANK_STATEMENT', 'OTHER') NOT NULL,
            document_number VARCHAR(50),
            document_path VARCHAR(255),
            verified BOOLEAN DEFAULT FALSE,
            verified_by VARCHAR(50),
            verified_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_agent_kyc (agent_id),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
        )
    """)
    
    # 4. Agency transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agency_transactions (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            transaction_ref VARCHAR(50) UNIQUE NOT NULL,
            agent_id VARCHAR(20) NOT NULL,
            customer_account VARCHAR(20),
            transaction_type ENUM('CASH_IN', 'CASH_OUT', 'BALANCE_INQUIRY', 'MINI_STATEMENT', 
                                 'BILL_PAYMENT', 'FUND_TRANSFER', 'ACCOUNT_OPENING') NOT NULL,
            amount DECIMAL(15,2) DEFAULT 0.00,
            fee DECIMAL(10,2) DEFAULT 0.00,
            status ENUM('PENDING', 'COMPLETED', 'FAILED', 'REVERSED') DEFAULT 'PENDING',
            device_id VARCHAR(50),
            location_lat DECIMAL(10,8),
            location_lng DECIMAL(11,8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP NULL,
            INDEX idx_agent_txn (agent_id),
            INDEX idx_customer_txn (customer_account),
            INDEX idx_txn_type (transaction_type),
            INDEX idx_txn_date (created_at),
            INDEX idx_txn_status (status),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE RESTRICT
        )
    """)
    
    # 5. Agent commissions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_commissions (
            commission_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            transaction_ref VARCHAR(50) NOT NULL,
            commission_amount DECIMAL(10,2) NOT NULL,
            commission_type VARCHAR(50) NOT NULL,
            status ENUM('PENDING', 'PAID', 'REVERSED') DEFAULT 'PENDING',
            paid_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_agent_commission (agent_id),
            INDEX idx_commission_status (status),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE RESTRICT,
            FOREIGN KEY (transaction_ref) REFERENCES agency_transactions(transaction_ref) ON DELETE RESTRICT
        )
    """)
    
    # 6. Agent float transactions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_float_transactions (
            float_txn_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            transaction_type ENUM('CREDIT', 'DEBIT', 'INITIAL_CREDIT') NOT NULL,
            amount DECIMAL(15,2) NOT NULL,
            reference VARCHAR(50) NOT NULL,
            old_balance DECIMAL(15,2),
            new_balance DECIMAL(15,2),
            processed_by VARCHAR(50) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_agent_float (agent_id),
            INDEX idx_float_type (transaction_type),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE RESTRICT
        )
    """)
    
    # 7. Agent settlement accounts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_settlement_accounts (
            settlement_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            account_number VARCHAR(20) UNIQUE NOT NULL,
            balance DECIMAL(15,2) DEFAULT 0.00,
            currency VARCHAR(3) DEFAULT 'KES',
            status ENUM('ACTIVE', 'SUSPENDED', 'CLOSED') DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_agent_settlement (agent_id),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE RESTRICT
        )
    """)
    
    # 8. Agent authentication logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_auth_logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            device_id VARCHAR(50),
            auth_type ENUM('PIN', 'BIOMETRIC', 'OTP') NOT NULL,
            status ENUM('SUCCESS', 'FAILED') NOT NULL,
            session_token VARCHAR(64),
            ip_address VARCHAR(45),
            location_lat DECIMAL(10,8),
            location_lng DECIMAL(11,8),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_agent_auth (agent_id),
            INDEX idx_auth_status (status),
            INDEX idx_auth_date (created_at)
        )
    """)
    
    # 9. Agent status logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_status_logs (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            old_status VARCHAR(20),
            new_status VARCHAR(20) NOT NULL,
            changed_by VARCHAR(50) NOT NULL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_agent_status_log (agent_id),
            FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE
        )
    """)
    
    # 10. Agent audit logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agency_audit_logs (
            audit_id INT AUTO_INCREMENT PRIMARY KEY,
            agent_id VARCHAR(20) NOT NULL,
            transaction_type VARCHAR(50),
            transaction_data TEXT,
            result_data TEXT,
            ip_address VARCHAR(45),
            device_id VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_agent_audit (agent_id),
            INDEX idx_audit_date (created_at)
        )
    """)
    
    conn.commit()
    print("✅ All agency banking tables created successfully!")
    
    return cursor, conn

def create_sample_agents(cursor, conn):
    """Create sample agents for testing"""
    
    # Sample agents data
    sample_agents = [
        {
            'agent_id': 'AG20240101SUPER1',
            'agent_name': 'Nairobi Super Agent Ltd',
            'national_id': '12345678',
            'phone_number': '254700000001',
            'email': 'super@nairobisuperagent.com',
            'business_name': 'Nairobi Super Agent Ltd',
            'business_location': 'Nairobi CBD, Kenya',
            'agent_type': 'SUPER_AGENT',
            'parent_agent_id': None,
            'pin': '1234',
            'daily_limit': 5000000.00,
            'transaction_limit': 500000.00,
            'float_balance': 1000000.00,
            'commission_rate': 0.003
        },
        {
            'agent_id': 'AG20240101SUB001',
            'agent_name': 'Westlands Electronics',
            'national_id': '87654321',
            'phone_number': '254700000002',
            'email': 'info@westlandselec.com',
            'business_name': 'Westlands Electronics Shop',
            'business_location': 'Westlands, Nairobi',
            'agent_type': 'SUB_AGENT',
            'parent_agent_id': 'AG20240101SUPER1',
            'pin': '5678',
            'daily_limit': 1000000.00,
            'transaction_limit': 100000.00,
            'float_balance': 200000.00,
            'commission_rate': 0.005
        },
        {
            'agent_id': 'AG20240101RET001',
            'agent_name': 'Mama Mboga Shop',
            'national_id': '11223344',
            'phone_number': '254700000003',
            'email': 'mama@mbogashop.com',
            'business_name': 'Mama Mboga General Store',
            'business_location': 'Kibera, Nairobi',
            'agent_type': 'RETAILER',
            'parent_agent_id': 'AG20240101SUB001',
            'pin': '9999',
            'daily_limit': 500000.00,
            'transaction_limit': 50000.00,
            'float_balance': 50000.00,
            'commission_rate': 0.007
        }
    ]
    
    for agent in sample_agents:
        # Hash PIN
        pin_hash = hashlib.sha256(agent['pin'].encode()).hexdigest()
        
        cursor.execute("""
            INSERT IGNORE INTO agents (
                agent_id, agent_name, national_id, phone_number, email,
                business_name, business_location, agent_type, parent_agent_id,
                pin_hash, daily_limit, transaction_limit, float_balance,
                commission_rate, status, created_at, approved_by, approved_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            agent['agent_id'], agent['agent_name'], agent['national_id'],
            agent['phone_number'], agent['email'], agent['business_name'],
            agent['business_location'], agent['agent_type'], agent['parent_agent_id'],
            pin_hash, agent['daily_limit'], agent['transaction_limit'],
            agent['float_balance'], agent['commission_rate'], 'ACTIVE',
            datetime.now(), 'SYSTEM', datetime.now()
        ))
        
        # Create settlement account
        settlement_account = f"AGNT{agent['agent_id'][2:]}"
        cursor.execute("""
            INSERT IGNORE INTO agent_settlement_accounts (
                agent_id, account_number, balance, currency, status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            agent['agent_id'], settlement_account, 0, 'KES', 'ACTIVE', datetime.now()
        ))
        
        # Register sample devices
        device_id = f"POS{agent['agent_id'][-3:]}"
        cursor.execute("""
            INSERT IGNORE INTO agent_devices (
                device_id, agent_id, device_type, device_model,
                is_active, registered_at
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            device_id, agent['agent_id'], 'POS', 'Ingenico iWL250',
            True, datetime.now()
        ))
    
    conn.commit()
    print("✅ Sample agents created successfully!")
    
    # Print agent credentials
    print("\n📋 Sample Agent Credentials:")
    print("=" * 50)
    for agent in sample_agents:
        print(f"Agent ID: {agent['agent_id']}")
        print(f"Name: {agent['agent_name']}")
        print(f"PIN: {agent['pin']}")
        print(f"Type: {agent['agent_type']}")
        print(f"Float Balance: KES {agent['float_balance']:,.2f}")
        print("-" * 30)

def main():
    """Main setup function"""
    print("🏪 Setting up Wekeza Agency Banking Database...")
    print("=" * 50)
    
    try:
        # Create tables
        cursor, conn = create_agency_tables()
        
        # Create sample data
        create_sample_agents(cursor, conn)
        
        # Close connection
        cursor.close()
        conn.close()
        
        print("\n🎉 Agency Banking Database Setup Complete!")
        print("\nNext Steps:")
        print("1. Start the agency portal: python ui/agent_portal.py")
        print("2. Use sample agent credentials above to login")
        print("3. Test transactions with existing customer accounts")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()