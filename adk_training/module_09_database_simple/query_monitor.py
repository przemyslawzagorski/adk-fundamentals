"""
Query Monitor - Simple web server to view SQL queries in real-time.

This Flask app provides a web interface to monitor all SQL queries
executed by the database_tools.

Usage:
    python query_monitor.py
    
Then open: http://localhost:5001
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os

# Import query logger
from query_logger import get_query_history, get_query_stats, clear_query_history

print("=" * 60)
print("🔍 SQL Query Monitor - Starting")
print("=" * 60)

app = Flask(__name__)

# HTML template for the dashboard
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SQL Query Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        h1 {
            color: #333;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }
        .stat-card .value {
            font-size: 32px;
            font-weight: bold;
        }
        .query-list {
            margin-top: 30px;
        }
        .query-item {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 5px;
        }
        .query-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .function-name {
            font-weight: bold;
            color: #667eea;
            font-size: 16px;
        }
        .timestamp {
            color: #666;
            font-size: 12px;
        }
        .query-sql {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 12px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            overflow-x: auto;
            margin: 10px 0;
        }
        .query-params {
            color: #666;
            font-size: 13px;
            margin: 5px 0;
        }
        .result-count {
            display: inline-block;
            background: #28a745;
            color: white;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
        }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-left: 10px;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
        .no-queries {
            text-align: center;
            padding: 40px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>
            🔍 SQL Query Monitor
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
        </h1>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total Queries</h3>
                <div class="value">{{ total_queries }}</div>
            </div>
            <div class="stat-card">
                <h3>Functions Used</h3>
                <div class="value">{{ unique_functions }}</div>
            </div>
            <div class="stat-card">
                <h3>Total Results</h3>
                <div class="value">{{ total_results }}</div>
            </div>
        </div>
        
        <div class="query-list">
            <h2>Recent Queries</h2>
            {% if queries %}
                {% for query in queries %}
                <div class="query-item">
                    <div class="query-header">
                        <span class="function-name">{{ query.function }}</span>
                        <span class="timestamp">{{ query.timestamp }}</span>
                    </div>
                    <div class="query-sql">{{ query.query }}</div>
                    <div class="query-params">
                        <strong>Parameters:</strong> {{ query.params }}
                    </div>
                    <div>
                        <span class="result-count">{{ query.result_count }} results</span>
                    </div>
                </div>
                {% endfor %}
            {% else %}
                <div class="no-queries">
                    <h3>No queries yet</h3>
                    <p>Run some queries through the agent to see them here!</p>
                </div>
            {% endif %}
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main dashboard page."""
    # Get queries (already sorted newest first)
    queries = get_query_history(limit=100)

    # Get stats
    stats = get_query_stats()

    return render_template_string(
        HTML_TEMPLATE,
        queries=queries,
        total_queries=stats['total_queries'],
        unique_functions=stats['unique_functions'],
        total_results=stats['total_results']
    )

@app.route('/api/queries')
def api_queries():
    """JSON API endpoint for queries."""
    limit = request.args.get('limit', 100, type=int)
    return jsonify(get_query_history(limit=limit))

@app.route('/api/stats')
def api_stats():
    """JSON API endpoint for statistics."""
    return jsonify(get_query_stats())

@app.route('/api/clear', methods=['POST'])
def api_clear():
    """Clear all query history."""
    success = clear_query_history()
    return jsonify({'success': success})

if __name__ == '__main__':
    print("🔍 SQL Query Monitor")
    print("=" * 60)
    print("Starting web server on http://localhost:5001")
    print("Open this URL in your browser to see SQL queries in real-time!")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=True)

