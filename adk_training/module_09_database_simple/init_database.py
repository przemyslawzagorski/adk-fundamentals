"""
Initialize SQLite database with sample hotel data.
This script creates a hotels.db file with sample data for testing.
"""

import sqlite3
import os

def init_database():
    """Create and populate the hotels database."""
    
    # Remove existing database if it exists
    db_path = os.path.join(os.path.dirname(__file__), 'hotels.db')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create new database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create hotels table
    cursor.execute('''
        CREATE TABLE hotels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            rating REAL,
            price_per_night INTEGER,
            description TEXT
        )
    ''')
    
    # Insert sample data - Polish hotels
    sample_hotels = [
        ('Hotel Bristol', 'Warsaw', 4.8, 450, 'Luxury 5-star hotel in the heart of Warsaw'),
        ('Hotel Marriott', 'Warsaw', 4.5, 380, 'Modern business hotel with great amenities'),
        ('Novotel Centrum', 'Warsaw', 4.2, 320, 'Comfortable hotel near central station'),
        ('Hotel Stary', 'Krakow', 4.9, 520, 'Boutique hotel in historic Old Town'),
        ('Hotel Copernicus', 'Krakow', 4.7, 480, 'Elegant hotel with medieval charm'),
        ('Radisson Blu', 'Krakow', 4.4, 350, 'Modern hotel near Wawel Castle'),
        ('Hilton', 'Gdansk', 4.6, 400, 'Waterfront hotel with sea views'),
        ('Sofitel Grand', 'Gdansk', 4.8, 460, 'Historic luxury hotel'),
        ('Hampton by Hilton', 'Gdansk', 4.3, 280, 'Affordable hotel near Old Town'),
        ('Hotel Monopol', 'Wroclaw', 4.5, 340, 'Art Nouveau hotel in city center'),
        ('DoubleTree by Hilton', 'Wroclaw', 4.4, 310, 'Modern hotel near Market Square'),
        ('Mercure', 'Poznan', 4.2, 290, 'Comfortable hotel in business district'),
        ('Sheraton', 'Poznan', 4.6, 380, 'Upscale hotel with conference facilities'),
        ('Hotel Zamek', 'Zakopane', 4.7, 420, 'Mountain resort with stunning views'),
        ('Grand Hotel', 'Sopot', 4.9, 550, 'Iconic beachfront luxury hotel'),
    ]
    
    cursor.executemany(
        'INSERT INTO hotels (name, location, rating, price_per_night, description) VALUES (?, ?, ?, ?, ?)',
        sample_hotels
    )
    
    conn.commit()
    
    # Verify data
    cursor.execute('SELECT COUNT(*) FROM hotels')
    count = cursor.fetchone()[0]
    print(f"✅ Database created successfully: {db_path}")
    print(f"✅ Inserted {count} hotels")
    
    # Show sample data
    print("\n📊 Sample data:")
    cursor.execute('SELECT name, location, rating FROM hotels LIMIT 5')
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]}) - Rating: {row[2]}")
    
    conn.close()

if __name__ == '__main__':
    init_database()

