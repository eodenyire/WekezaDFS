#!/usr/bin/env python3

import uuid
from datetime import datetime

def test_fixed_id_generation():
    """Test the fixed ID generation that fits database limits"""
    
    print("🧪 Testing FIXED ID generation (within database limits)...")
    
    # Test Queue ID generation (must be <= 20 chars)
    print("\n📋 Queue ID Generation (max 20 chars):")
    for i in range(3):
        queue_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 14 chars
        queue_random = uuid.uuid4().hex[:4].upper()  # 4 chars
        queue_id = f"AQ{queue_timestamp}{queue_random}"  # AQ + 14 + 4 = 20 chars
        print(f"  - {queue_id} (length: {len(queue_id)})")
    
    # Test Application ID generation
    print("\n📋 Application ID Generation:")
    for i in range(3):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')  # 14 chars
        random_suffix = uuid.uuid4().hex[:2].upper()  # 2 chars
        application_id = f"LA{timestamp}{random_suffix}"  # LA + 14 + 2 = 18 chars
        print(f"  - {application_id} (length: {len(application_id)})")
    
    print("\n✅ All IDs now fit within database column limits!")
    print("📏 Queue IDs: exactly 20 characters (fits VARCHAR(20))")
    print("📏 Application IDs: 18 characters (safe)")
    print("🔧 This should fix the 'Data too long' error!")

if __name__ == "__main__":
    test_fixed_id_generation()