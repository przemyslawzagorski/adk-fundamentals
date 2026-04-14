"""
Query Logger - Simple, reliable query logging using SQLite.

This module provides thread-safe and process-safe query logging
using a separate SQLite database.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any

# Query log database (separate from hotels.db)
QUERY_LOG_DB = os.path.join(os.path.dirname(__file__), 'query_log.db')


def _init_query_log_db():
    """Initialize query log database if it doesn't exist."""
    conn = sqlite3.connect(QUERY_LOG_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            function_name TEXT NOT NULL,
            query TEXT NOT NULL,
            params TEXT NOT NULL,
            result_count INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create index for faster queries
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON query_log(timestamp DESC)
    ''')
    conn.commit()
    conn.close()


def log_query(function_name: str, query: str, params: tuple, result_count: int):
    """
    Log SQL query execution to database.
    
    This is thread-safe and process-safe thanks to SQLite's built-in locking.
    """
    try:
        _init_query_log_db()
        
        conn = sqlite3.connect(QUERY_LOG_DB, timeout=10.0)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO query_log (timestamp, function_name, query, params, result_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            function_name,
            query.strip(),
            json.dumps(params),  # Store params as JSON string
            result_count
        ))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"⚠️  Failed to log query: {e}")
        return False


def get_query_history(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get logged queries from database.
    
    Args:
        limit: Maximum number of queries to return (default: 100)
        
    Returns:
        List of query log entries, newest first
    """
    try:
        if not os.path.exists(QUERY_LOG_DB):
            return []
        
        conn = sqlite3.connect(QUERY_LOG_DB, timeout=10.0)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, function_name as function, query, params, result_count
            FROM query_log
            ORDER BY id DESC
            LIMIT ?
        ''', (limit,))
        
        results = []
        for row in cursor.fetchall():
            entry = dict(row)
            # Parse params back from JSON
            try:
                entry['params'] = json.loads(entry['params'])
            except:
                entry['params'] = entry['params']  # Keep as string if parse fails
            results.append(entry)
        
        conn.close()
        return results
        
    except Exception as e:
        print(f"⚠️  Failed to read query history: {e}")
        return []


def get_query_stats() -> Dict[str, Any]:
    """Get statistics about logged queries."""
    try:
        if not os.path.exists(QUERY_LOG_DB):
            return {'total_queries': 0, 'unique_functions': 0, 'total_results': 0}
        
        conn = sqlite3.connect(QUERY_LOG_DB, timeout=10.0)
        cursor = conn.cursor()
        
        # Total queries
        cursor.execute('SELECT COUNT(*) FROM query_log')
        total_queries = cursor.fetchone()[0]
        
        # Unique functions
        cursor.execute('SELECT COUNT(DISTINCT function_name) FROM query_log')
        unique_functions = cursor.fetchone()[0]
        
        # Total results
        cursor.execute('SELECT SUM(result_count) FROM query_log')
        total_results = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_queries': total_queries,
            'unique_functions': unique_functions,
            'total_results': total_results
        }
        
    except Exception as e:
        print(f"⚠️  Failed to get query stats: {e}")
        return {'total_queries': 0, 'unique_functions': 0, 'total_results': 0}


def clear_query_history():
    """Clear all logged queries."""
    try:
        if os.path.exists(QUERY_LOG_DB):
            conn = sqlite3.connect(QUERY_LOG_DB)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM query_log')
            conn.commit()
            conn.close()
            return True
    except Exception as e:
        print(f"⚠️  Failed to clear query history: {e}")
        return False

