#!/usr/bin/env python3
"""
Database Testing Script for Wekeza DFS Platform
Run this script to test database connectivity and table creation.
"""

import mysql.connector
from mysql.connector import Error
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wekeza_dfs_db'
}

EXPECTED_TABLES = [
    'users',
    'accounts', 
    'loans',
    'transactions',
    'user_policies',
    'businesses'
]

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing Database Connection...")
    
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            print("✅ Successfully connected to MySQL database")
            
            # Get database info
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"   MySQL Version: {version[0]}")
            
            cursor.execute("SELECT DATABASE()")
            db_name = cursor.fetchone()
            print(f"   Current Database: {db_name[0]}")
            
            return connection
        else:
            print("❌ Failed to connect to database")
            return None
            
    except Error as e:
        print(f"❌ Database connection error: {e}")
        return None

def test_database_exists(connection):
    """Test if the wekeza_dfs_db database exists"""
    print("\n🔍 Testing Database Existence...")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES LIKE 'wekeza_dfs_db'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Database 'wekeza_dfs_db' exists")
            return True
        else:
            print("❌ Database 'wekeza_dfs_db' does not exist")
            print("   Create it with: CREATE DATABASE IF NOT EXISTS wekeza_dfs_db;")
            return False
            
    except Error as e:
        print(f"❌ Error checking database existence: {e}")
        return False

def test_tables_exist(connection):
    """Test if expected tables exist"""
    print("\n🔍 Testing Table Existence...")
    
    try:
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        print(f"   Found {len(existing_tables)} tables in database")
        
        missing_tables = []
        for table in EXPECTED_TABLES:
            if table in existing_tables:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (missing)")
                missing_tables.append(table)
        
        if not existing_tables:
            print("\n⚠️  No tables found. This is normal if you haven't started the backend API yet.")
            print("   Tables will be created automatically when you start the FastAPI backend.")
        elif missing_tables:
            print(f"\n⚠️  {len(missing_tables)} expected tables are missing.")
            print("   Start the backend API to create missing tables automatically.")
        else:
            print(f"\n✅ All expected tables exist!")
        
        return len(missing_tables) == 0
        
    except Error as e:
        print(f"❌ Error checking tables: {e}")
        return False

def test_sample_data(connection):
    """Test if there's any sample data"""
    print("\n🔍 Testing Sample Data...")
    
    try:
        cursor = connection.cursor()
        
        # Check users table
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"   Users: {user_count} records")
        except:
            print("   Users: Table not accessible")
        
        # Check accounts table  
        try:
            cursor.execute("SELECT COUNT(*) FROM accounts")
            account_count = cursor.fetchone()[0]
            print(f"   Accounts: {account_count} records")
        except:
            print("   Accounts: Table not accessible")
            
        # Check loans table
        try:
            cursor.execute("SELECT COUNT(*) FROM loans") 
            loan_count = cursor.fetchone()[0]
            print(f"   Loans: {loan_count} records")
        except:
            print("   Loans: Table not accessible")
            
        # Check transactions table
        try:
            cursor.execute("SELECT COUNT(*) FROM transactions")
            txn_count = cursor.fetchone()[0] 
            print(f"   Transactions: {txn_count} records")
        except:
            print("   Transactions: Table not accessible")
            
        return True
        
    except Error as e:
        print(f"❌ Error checking sample data: {e}")
        return False

def show_database_setup_instructions():
    """Show instructions for database setup"""
    print("\n📋 Database Setup Instructions:")
    print("=" * 40)
    print("1. Ensure MySQL Server is running")
    print("2. Open MySQL Workbench or command line")
    print("3. Run: CREATE DATABASE IF NOT EXISTS wekeza_dfs_db;")
    print("4. Verify connection settings:")
    print(f"   Host: {DB_CONFIG['host']}")
    print(f"   User: {DB_CONFIG['user']}")
    print(f"   Password: {DB_CONFIG['password']}")
    print(f"   Database: {DB_CONFIG['database']}")

def main():
    """Run all database tests"""
    print("🚀 Wekeza DFS Platform Database Testing")
    print("=" * 50)
    
    # Test 1: Database Connection
    connection = test_database_connection()
    if not connection:
        show_database_setup_instructions()
        return
    
    try:
        # Test 2: Database Exists
        db_exists = test_database_exists(connection)
        if not db_exists:
            show_database_setup_instructions()
            return
        
        # Test 3: Tables Exist
        tables_exist = test_tables_exist(connection)
        
        # Test 4: Sample Data
        test_sample_data(connection)
        
        print("\n" + "=" * 50)
        print("🎉 Database Testing Complete!")
        
        if tables_exist:
            print("✅ Database is fully set up and ready!")
        else:
            print("⚠️  Database exists but tables need to be created.")
            print("   Start the backend API to auto-create tables:")
            print("   cd 03_Source_Code\\backend_api")
            print("   uvicorn app.main:app --reload --port 8000")
        
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n🔌 Database connection closed")

if __name__ == "__main__":
    main()