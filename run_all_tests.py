#!/usr/bin/env python3
"""
Master Testing Script for Wekeza DFS Platform
Run this script to test all components of your system.
"""

import subprocess
import sys
import time
import os

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        # Run the test script
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              cwd=os.path.dirname(os.path.abspath(__file__)))
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED")
            return False
            
    except FileNotFoundError:
        print(f"❌ Test script '{script_name}' not found")
        return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def check_prerequisites():
    """Check if required packages are installed"""
    print("🔍 Checking Prerequisites...")
    
    required_packages = ['requests', 'mysql.connector']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All prerequisites satisfied")
    return True

def show_summary(results):
    """Show test results summary"""
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print(f"{'='*60}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print(f"\nDetailed Results:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! Your Wekeza DFS Platform is working correctly!")
        print("\nYou can now:")
        print("• Register users and test banking features")
        print("• Apply for loans and insurance policies") 
        print("• Process business transactions")
        print("• Monitor system activity via admin portal")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Check the output above for details.")
        print("\nCommon solutions:")
        print("• Ensure MySQL is running and database is created")
        print("• Start all services using the provided startup scripts")
        print("• Check that all required ports (8000, 8502, 8503, 8504) are available")

def main():
    """Run all tests in sequence"""
    print("🚀 WEKEZA DFS PLATFORM - COMPREHENSIVE TESTING")
    print("=" * 60)
    print("This script will test all components of your banking platform")
    print("=" * 60)
    
    # Check prerequisites first
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please install missing packages first.")
        return
    
    # Define tests to run
    tests = {
        "Database Connectivity": "test_database.py",
        "API Functionality": "test_api.py", 
        "Portal Accessibility": "test_portals.py"
    }
    
    results = {}
    
    # Run each test
    for test_name, script_name in tests.items():
        success = run_test_script(script_name, test_name)
        results[test_name] = success
        
        # Small delay between tests
        time.sleep(2)
    
    # Show final summary
    show_summary(results)
    
    print(f"\n📋 Next Steps:")
    if all(results.values()):
        print("• Your system is ready for production testing!")
        print("• Try the end-to-end user journeys described in TESTING_GUIDE.md")
        print("• Monitor system performance under load")
    else:
        print("• Fix the failed components using the guidance above")
        print("• Re-run individual test scripts to verify fixes")
        print("• Check TESTING_GUIDE.md for detailed troubleshooting")
    
    print(f"\n📚 Documentation:")
    print("• TESTING_GUIDE.md - Comprehensive testing procedures")
    print("• LOCAL_DEV_GUIDE.md - Development setup instructions")
    print("• TEST_RESULTS.md - Code quality and syntax test results")

if __name__ == "__main__":
    main()