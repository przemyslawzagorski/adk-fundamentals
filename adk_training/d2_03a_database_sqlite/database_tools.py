"""
Database tools for hotel search.
These functions will be used as tools by the ADK agent.

All SQL queries are logged for monitoring and debugging.
"""

import sqlite3
import os
import logging
from typing import List, Dict, Any
from datetime import datetime

# Import query logger
from query_logger import log_query as _log_query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'hotels.db')


def log_query(function_name: str, query: str, params: tuple, result_count: int):
    """Log SQL query execution (wrapper for query_logger)."""
    # Log to console
    logger.info(f"🔍 SQL Query from {function_name}:")
    logger.info(f"   Query: {query.strip()}")
    logger.info(f"   Params: {params}")
    logger.info(f"   Results: {result_count} rows")

    # Log to database (thread-safe, process-safe)
    _log_query(function_name, query, params, result_count)


def search_hotels_by_name(name: str) -> List[Dict[str, Any]]:
    """
    Search for hotels based on name.

    Args:
        name: The name of the hotel to search for (partial match supported)

    Returns:
        List of hotels matching the search criteria
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    cursor = conn.cursor()

    query = '''
        SELECT id, name, location, rating, price_per_night, description
        FROM hotels
        WHERE name LIKE ?
        ORDER BY rating DESC
    '''

    params = (f'%{name}%',)
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]

    # Log the query
    log_query('search_hotels_by_name', query, params, len(results))

    conn.close()

    return results


def search_hotels_by_location(location: str) -> List[Dict[str, Any]]:
    """
    Search for hotels based on location.

    Args:
        location: The location/city to search for hotels in

    Returns:
        List of hotels in the specified location
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT id, name, location, rating, price_per_night, description
        FROM hotels
        WHERE location LIKE ?
        ORDER BY rating DESC
    '''

    params = (f'%{location}%',)
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]

    # Log the query
    log_query('search_hotels_by_location', query, params, len(results))

    conn.close()

    return results


def search_hotels_by_price_range(min_price: int, max_price: int) -> List[Dict[str, Any]]:
    """
    Search for hotels within a price range.

    Args:
        min_price: Minimum price per night
        max_price: Maximum price per night

    Returns:
        List of hotels within the price range
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT id, name, location, rating, price_per_night, description
        FROM hotels
        WHERE price_per_night BETWEEN ? AND ?
        ORDER BY price_per_night ASC
    '''

    params = (min_price, max_price)
    cursor.execute(query, params)
    results = [dict(row) for row in cursor.fetchall()]

    # Log the query
    log_query('search_hotels_by_price_range', query, params, len(results))

    conn.close()

    return results


def get_hotel_by_id(hotel_id: int) -> Dict[str, Any]:
    """
    Get detailed information about a specific hotel.

    Args:
        hotel_id: The unique ID of the hotel

    Returns:
        Hotel details or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = '''
        SELECT id, name, location, rating, price_per_night, description
        FROM hotels
        WHERE id = ?
    '''

    params = (hotel_id,)
    cursor.execute(query, params)
    result = cursor.fetchone()

    # Log the query
    log_query('get_hotel_by_id', query, params, 1 if result else 0)

    conn.close()

    return dict(result) if result else None


# Test functions
if __name__ == '__main__':
    print("🔍 Testing database tools...\n")
    
    # Test search by name
    print("1. Search hotels by name 'Hilton':")
    results = search_hotels_by_name('Hilton')
    for hotel in results:
        print(f"   - {hotel['name']} in {hotel['location']} (${hotel['price_per_night']}/night)")
    
    # Test search by location
    print("\n2. Search hotels in 'Warsaw':")
    results = search_hotels_by_location('Warsaw')
    for hotel in results:
        print(f"   - {hotel['name']} - Rating: {hotel['rating']}")
    
    # Test search by price range
    print("\n3. Search hotels between $300-$400:")
    results = search_hotels_by_price_range(300, 400)
    for hotel in results:
        print(f"   - {hotel['name']} in {hotel['location']} (${hotel['price_per_night']}/night)")
    
    # Test get by ID
    print("\n4. Get hotel by ID (1):")
    hotel = get_hotel_by_id(1)
    if hotel:
        print(f"   - {hotel['name']}: {hotel['description']}")

