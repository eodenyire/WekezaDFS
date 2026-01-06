#!/usr/bin/env python3
"""
Portal Accessibility Testing Script for Wekeza DFS Platform
Run this script to test if your Streamlit portals are accessible.
"""

import requests
import time
import webbrowser
from urllib.parse import urlparse

PORTALS = {
    "Backend API": "http://localhost:8000/docs",
    "Customer Portal": "http://localhost:8502",
    "Admin Portal": "http://localhost:8503", 
    "Business Portal": "http://localhost:8504"
}

def test_portal_accessibility(name, url):
    """Test if a portal is accessible"""
    print(f"🔍 Testing {name}...")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {name} is accessible at {url}")
            return True
        else:
            print(f"❌ {name} returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to {name} - Make sure it's running")
        return False
    except requests.exceptions.Timeout:
        print(f"⚠️  {name} is slow to respond (might still be starting)")
        return False
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")
        return False

def open_working_portals(working_portals):
    """Open working portals in browser"""
    if not working_portals:
        print("\n❌ No portals are accessible")
        return
    
    print(f"\n🌐 Opening {len(working_portals)} working portal(s) in browser...")
    
    for name, url in working_portals.items():
        try:
            webbrowser.open(url)
            print(f"   Opened: {name}")
            time.sleep(1)  # Small delay between opening tabs
        except Exception as e:
            print(f"   Failed to open {name}: {e}")

def show_startup_commands():
    """Show commands to start services"""
    print("\n📋 Service Startup Commands:")
    print("=" * 40)
    
    commands = {
        "Backend API": [
            "cd 03_Source_Code\\backend_api",
            "venv\\Scripts\\activate",
            "uvicorn app.main:app --reload --port 8000"
        ],
        "Customer Portal": [
            "cd 03_Source_Code\\web_portal_customer", 
            "streamlit run customer_app.py --server.port 8502"
        ],
        "Admin Portal": [
            "cd 03_Source_Code\\web_portal_admin",
            "streamlit run admin_dashboard.py --server.port 8503"
        ],
        "Business Portal": [
            "cd 03_Source_Code\\web_portal_business",
            "streamlit run business_app.py --server.port 8504"
        ]
    }
    
    for service, cmds in commands.items():
        print(f"\n{service}:")
        for cmd in cmds:
            print(f"  {cmd}")

def main():
    """Run portal accessibility tests"""
    print("🚀 Wekeza DFS Platform Portal Testing")
    print("=" * 50)
    
    working_portals = {}
    failed_portals = {}
    
    # Test each portal
    for name, url in PORTALS.items():
        if test_portal_accessibility(name, url):
            working_portals[name] = url
        else:
            failed_portals[name] = url
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"✅ Working: {len(working_portals)}")
    print(f"❌ Failed: {len(failed_portals)}")
    
    if working_portals:
        print(f"\n✅ Working Portals:")
        for name, url in working_portals.items():
            print(f"   {name}: {url}")
    
    if failed_portals:
        print(f"\n❌ Failed Portals:")
        for name, url in failed_portals.items():
            print(f"   {name}: {url}")
        
        show_startup_commands()
    
    # Offer to open working portals
    if working_portals:
        print(f"\n🌐 Would you like to open the working portals in your browser?")
        print("   (This will open new browser tabs)")
        
        # For automated testing, we'll skip the input prompt
        # In manual testing, user can uncomment the next lines:
        # response = input("Open portals? (y/n): ").lower().strip()
        # if response in ['y', 'yes']:
        #     open_working_portals(working_portals)
        
        print("   Run this script interactively to open portals automatically")
    
    print(f"\n🎉 Portal Testing Complete!")
    
    if len(working_portals) == len(PORTALS):
        print("🌟 All portals are running successfully!")
        print("\nYou can now test the full system functionality:")
        print("1. Register/login users in Customer Portal")
        print("2. Apply for loans and insurance")
        print("3. Monitor activities in Admin Portal")
        print("4. Test business features in Business Portal")
    else:
        print(f"⚠️  {len(failed_portals)} portal(s) need to be started")
        print("Use the startup commands shown above")

if __name__ == "__main__":
    main()