-- ============================================================================
-- Database Setup for Hotel Search Agent
-- ============================================================================
-- This script creates the hotels table and populates it with sample data.
-- Run this in your PostgreSQL database (e.g., Neon.tech, Supabase, etc.)
-- ============================================================================

-- Drop table if exists (for clean setup)
DROP TABLE IF EXISTS hotels;

-- Create hotels table
CREATE TABLE hotels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(100) NOT NULL,
    rating DECIMAL(2,1) CHECK (rating >= 0 AND rating <= 5),
    price_per_night INTEGER,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data - Polish hotels
INSERT INTO hotels (name, location, rating, price_per_night, description) VALUES
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
    ('Grand Hotel', 'Sopot', 4.9, 550, 'Iconic beachfront luxury hotel');

-- Create indexes for better query performance
CREATE INDEX idx_hotels_location ON hotels(location);
CREATE INDEX idx_hotels_name ON hotels(name);
CREATE INDEX idx_hotels_price ON hotels(price_per_night);

-- Verify data
SELECT COUNT(*) as total_hotels FROM hotels;

-- Show sample data
SELECT name, location, rating, price_per_night 
FROM hotels 
ORDER BY rating DESC 
LIMIT 5;

-- ============================================================================
-- Success! Your database is ready.
-- ============================================================================
-- Next steps:
-- 1. Copy the connection string from your PostgreSQL provider
-- 2. Update toolbox.yaml with the connection string
-- 3. Run the toolbox and agent
-- ============================================================================

