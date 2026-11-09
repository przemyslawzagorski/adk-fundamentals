#!/usr/bin/env python3
"""
Debug script to check query history file reading.
"""

import os
import json

# Check current directory
print(f"Current directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# Try to import and check
try:
    from database_tools import QUERY_HISTORY_FILE, get_query_history
    
    print(f"\n📁 Query history file path: {QUERY_HISTORY_FILE}")
    print(f"📁 File exists: {os.path.exists(QUERY_HISTORY_FILE)}")
    
    if os.path.exists(QUERY_HISTORY_FILE):
        print(f"📁 File size: {os.path.getsize(QUERY_HISTORY_FILE)} bytes")
        
        # Try to read directly
        print("\n🔍 Reading file directly:")
        with open(QUERY_HISTORY_FILE, 'r') as f:
            content = f.read()
            print(f"File content length: {len(content)} chars")
            data = json.loads(content)
            print(f"Number of queries in file: {len(data)}")
            if data:
                print(f"First query: {data[0]['function']} at {data[0]['timestamp']}")
        
        # Try using get_query_history()
        print("\n🔍 Using get_query_history():")
        queries = get_query_history()
        print(f"Number of queries returned: {len(queries)}")
        if queries:
            print(f"First query: {queries[0]['function']} at {queries[0]['timestamp']}")
        else:
            print("❌ get_query_history() returned empty list!")
    else:
        print("❌ File does not exist!")
        
        # Check if there's a file in current directory
        local_file = "query_history.json"
        if os.path.exists(local_file):
            print(f"\n⚠️  Found {local_file} in current directory!")
            with open(local_file, 'r') as f:
                data = json.load(f)
                print(f"   It has {len(data)} queries")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

