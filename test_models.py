#!/usr/bin/env python3
"""
Test the models to see what's causing the SQLAlchemy error
"""

import sys
import os

# Add the app directory to Python path
app_dir = os.path.join(os.path.dirname(__file__), '03_Source_Code', 'backend_api', 'app')
sys.path.insert(0, app_dir)

try:
    print("Testing model imports...")
    import database
    print("✅ Database imported")
    
    import models
    print("✅ Models imported")
    
    # Try to create tables
    print("Testing table creation...")
    models.Base.metadata.create_all(bind=database.engine)
    print("✅ Tables created successfully")
    
    print("🎉 Models are working correctly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()