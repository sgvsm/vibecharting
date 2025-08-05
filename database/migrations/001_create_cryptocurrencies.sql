-- Migration: 001_create_cryptocurrencies.sql
-- Description: Create cryptocurrencies table to store supported token metadata
-- Date: 2025-01-01

BEGIN;

-- Create cryptocurrencies table
CREATE TABLE cryptocurrencies (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    cmc_id INTEGER NOT NULL UNIQUE, -- CoinMarketCap ID
    rank INTEGER,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_cryptocurrencies_symbol ON cryptocurrencies(symbol);
CREATE INDEX idx_cryptocurrencies_cmc_id ON cryptocurrencies(cmc_id);
CREATE INDEX idx_cryptocurrencies_active ON cryptocurrencies(is_active) WHERE is_active = true;

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for updated_at
CREATE TRIGGER update_cryptocurrencies_updated_at 
    BEFORE UPDATE ON cryptocurrencies 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

COMMIT; 