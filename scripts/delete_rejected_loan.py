#!/usr/bin/env python3

import mysql.connector

def delete_rejected_loan():
    """Delete the rejected loan from authorization queue table"""
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🗑️ Deleting rejected loan from authorization queue...")
        
        # Delete the specific rejected loan entry
        cursor.execute("""
            DELETE FROM authorization_queue 
            WHERE queue_id = 'AQ20260104104014' AND status = 'REJECTED'
        """)
        
        deleted_count = cursor.rowcount
        
        if deleted_count > 0:
            print(f"✅ Deleted {deleted_count} rejected loan entry from authorization_queue")
            print("   Queue ID: AQ20260104104014")
            print("   Reference: LA20260104014")
            print("   Status: REJECTED")
        else:
            print("❌ No matching rejected loan found to delete")
        
        # Also check if there's a corresponding entry in loan_applications table
        cursor.execute("""
            SELECT * FROM loan_applications 
            WHERE application_id = 'LA20260104014'
        """)
        
        loan_app = cursor.fetchone()
        if loan_app:
            print("\n🔍 Found corresponding loan_applications entry:")
            print(f"   Application ID: {loan_app[0]}")
            print(f"   Status: {loan_app[10]}")  # status column
            
            # Delete from loan_applications too if it exists
            cursor.execute("""
                DELETE FROM loan_applications 
                WHERE application_id = 'LA20260104014'
            """)
            
            deleted_loan_count = cursor.rowcount
            if deleted_loan_count > 0:
                print(f"✅ Also deleted {deleted_loan_count} entry from loan_applications table")
        else:
            print("ℹ️ No corresponding entry found in loan_applications table")
        
        conn.commit()
        conn.close()
        
        print("\n🎯 CLEANUP COMPLETE!")
        print("✅ Rejected loan entries removed from database")
        print("🔄 Now you can create a new loan application to test the new unique ID system")
        print("📋 The new loan should get a unique Queue ID like: AQ20260104HHMMSSXXXXXX")
        
    except Exception as e:
        print(f"❌ Error deleting rejected loan: {e}")

if __name__ == "__main__":
    delete_rejected_loan()