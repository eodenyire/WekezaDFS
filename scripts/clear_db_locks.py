#!/usr/bin/env python3
"""
Clear database locks and reset connections
"""

import mysql.connector

def clear_db_locks():
    """Clear any hanging database locks"""
    
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',
            database='wekeza_dfs_db'
        )
        cursor = conn.cursor()
        
        print("🔓 Clearing database locks...")
        
        # Show current processes
        cursor.execute("SHOW PROCESSLIST")
        processes = cursor.fetchall()
        
        print(f"📋 Found {len(processes)} active processes")
        
        # Kill any long-running processes (except our own)
        for process in processes:
            process_id, user, host, db, command, time_val, state, info = process
            
            # Skip system processes and our own connection
            if user == 'root' and time_val > 30 and command != 'Sleep':
                print(f"   🔪 Killing process {process_id} (running for {time_val}s)")
                try:
                    cursor.execute(f"KILL {process_id}")
                except:
                    pass
        
        # Reset any table locks
        cursor.execute("UNLOCK TABLES")
        
        # Commit and close
        conn.commit()
        conn.close()
        
        print("✅ Database locks cleared!")
        
    except Exception as e:
        print(f"❌ Error clearing locks: {e}")

if __name__ == "__main__":
    clear_db_locks()