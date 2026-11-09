"""
Test script to demonstrate query logging.

This script runs some test queries and shows how they are logged.
You can run this while query_monitor.py is running to see real-time updates.
"""

from database_tools import (
    search_hotels_by_name,
    search_hotels_by_location,
    search_hotels_by_price_range,
    get_hotel_by_id,
    get_query_history
)
import time

def main():
    print("🧪 Testing Query Logging")
    print("=" * 60)
    print("\nRunning test queries...\n")
    
    # Test 1: Search by name
    print("1️⃣ Searching for 'Hilton' hotels...")
    results = search_hotels_by_name('Hilton')
    print(f"   Found {len(results)} hotels\n")
    time.sleep(1)
    
    # Test 2: Search by location
    print("2️⃣ Searching for hotels in 'Warsaw'...")
    results = search_hotels_by_location('Warsaw')
    print(f"   Found {len(results)} hotels\n")
    time.sleep(1)
    
    # Test 3: Search by price range
    print("3️⃣ Searching for hotels between 300-400 PLN...")
    results = search_hotels_by_price_range(300, 400)
    print(f"   Found {len(results)} hotels\n")
    time.sleep(1)
    
    # Test 4: Get by ID
    print("4️⃣ Getting hotel with ID 1...")
    hotel = get_hotel_by_id(1)
    print(f"   Found: {hotel['name'] if hotel else 'None'}\n")
    time.sleep(1)
    
    # Show query history
    print("=" * 60)
    print("📊 Query History Summary")
    print("=" * 60)
    
    history = get_query_history()
    print(f"\nTotal queries executed: {len(history)}")
    print(f"\nDetailed log:\n")
    
    for i, entry in enumerate(history, 1):
        print(f"{i}. {entry['function']}")
        print(f"   Time: {entry['timestamp']}")
        print(f"   Query: {entry['query'][:80]}...")
        print(f"   Params: {entry['params']}")
        print(f"   Results: {entry['result_count']} rows")
        print()
    
    print("=" * 60)
    print("✅ Test complete!")
    print("\n💡 Tip: If you have query_monitor.py running,")
    print("   refresh http://localhost:5001 to see these queries!")
    print("=" * 60)

if __name__ == '__main__':
    main()

