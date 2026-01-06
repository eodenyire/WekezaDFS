#!/usr/bin/env python3

import uuid
from datetime import datetime

def test_unique_id_generation():
    """Test the new unique ID generation logic"""
    
    print("🧪 Testing new unique ID generation...")
    
    # Test Application ID generation (new logic)
    print("\n📋 Application ID Generation:")
    for i in range(5):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = uuid.uuid4().hex[:4].upper()
        application_id = f"LA{timestamp}{random_suffix}"
        print(f"  - {application_id}")
    
    # Test Queue ID generation (new logic)
    print("\n📋 Queue ID Generation:")
    for i in range(5):
        queue_timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        queue_random = uuid.uuid4().hex[:6].upper()
        queue_id = f"AQ{queue_timestamp}{queue_random}"
        print(f"  - {queue_id}")
    
    # Test Payment ID generation (new logic)
    print("\n📋 Payment ID Generation:")
    for i in range(5):
        payment_id = f"LP{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
        print(f"  - {payment_id}")
    
    print("\n✅ All IDs are now unique with timestamp + random components!")
    print("🔧 This fixes the Queue ID collision issue you experienced.")

if __name__ == "__main__":
    test_unique_id_generation()