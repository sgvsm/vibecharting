-- Migration: 002_create_price_data.sql
-- Description: Create price_data table to store historical price and volume data
-- Date: 2025-01-01

BEGIN;

-- Create price_data table
CREATE TABLE price_data (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    price_usd DECIMAL(20, 8) NOT NULL,
    volume_24h DECIMAL(20, 2),
    market_cap DECIMAL(20, 2),
    percent_change_1h DECIMAL(10, 4),
    percent_change_24h DECIMAL(10, 4),
    percent_change_7d DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(crypto_id, timestamp)
);

-- Create indexes for time-series queries
CREATE INDEX idx_price_data_crypto_timestamp ON price_data(crypto_id, timestamp DESC);
CREATE INDEX idx_price_data_timestamp ON price_data(timestamp DESC);
CREATE INDEX idx_price_data_crypto_id ON price_data(crypto_id);

-- Optional: Partition by month for better performance
-- Uncomment if needed for large datasets
-- ALTER TABLE price_data PARTITION BY RANGE (timestamp);

COMMIT; 