"""
Quick test to verify the setup is working correctly.
Run this after initializing the database.
"""

import os
import sys

def test_database_exists():
    """Check if database file exists."""
    db_path = os.path.join(os.path.dirname(__file__), 'hotels.db')
    if not os.path.exists(db_path):
        print("❌ FAIL: hotels.db not found")
        print("   Run: python init_database.py")
        return False
    print("✅ PASS: hotels.db exists")
    return True

def test_database_content():
    """Check if database has data."""
    try:
        import sqlite3
        db_path = os.path.join(os.path.dirname(__file__), 'hotels.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='hotels'")
        if not cursor.fetchone():
            print("❌ FAIL: hotels table not found")
            return False
        print("✅ PASS: hotels table exists")
        
        # Check data exists
        cursor.execute("SELECT COUNT(*) FROM hotels")
        count = cursor.fetchone()[0]
        if count == 0:
            print("❌ FAIL: No hotels in database")
            return False
        print(f"✅ PASS: Found {count} hotels in database")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ FAIL: Database error: {e}")
        return False

def test_imports():
    """Check if required modules can be imported."""
    try:
        from database_tools import (
            search_hotels_by_name,
            search_hotels_by_location,
            search_hotels_by_price_range,
            get_hotel_by_id
        )
        print("✅ PASS: All database tools imported successfully")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Import error: {e}")
        return False

def test_database_functions():
    """Test if database functions work."""
    try:
        from database_tools import search_hotels_by_location
        
        results = search_hotels_by_location("Warsaw")
        if not results:
            print("❌ FAIL: No results from search_hotels_by_location")
            return False
        
        print(f"✅ PASS: search_hotels_by_location returned {len(results)} results")
        return True
    except Exception as e:
        print(f"❌ FAIL: Function test error: {e}")
        return False

def test_env_file():
    """Check if .env file exists."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print("⚠️  WARNING: .env file not found")
        print("   Copy .env.template to .env and configure it")
        return False
    print("✅ PASS: .env file exists")
    return True

def main():
    """Run all tests."""
    print("🧪 Testing adk04-simple-database setup...\n")
    
    tests = [
        ("Database file", test_database_exists),
        ("Database content", test_database_content),
        ("Python imports", test_imports),
        ("Database functions", test_database_functions),
        ("Environment file", test_env_file),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📋 Testing: {name}")
        results.append(test_func())
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 SUCCESS! All {total} tests passed!")
        print("\n✅ Your setup is ready!")
        print("   Run: python agent.py")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("\n❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == '__main__':
    main()

