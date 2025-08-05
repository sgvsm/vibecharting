-- Migration: 003_create_trend_analysis.sql
-- Description: Create trend_analysis table to store trend analysis results
-- Date: 2025-01-01

BEGIN;

-- Create trend type enum
CREATE TYPE trend_type_enum AS ENUM ('uptrend', 'downtrend', 'sideways');
CREATE TYPE timeframe_enum AS ENUM ('1h', '24h', '7d', '30d');

-- Create trend_analysis table
CREATE TABLE trend_analysis (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    timeframe timeframe_enum NOT NULL,
    trend_type trend_type_enum NOT NULL,
    confidence DECIMAL(5, 4) CHECK (confidence >= 0 AND confidence <= 1),
    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
    price_change_percent DECIMAL(10, 4),
    metadata JSONB, -- Additional analysis data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(crypto_id, timeframe, start_time)
);

-- Create indexes
CREATE INDEX idx_trend_analysis_crypto_timeframe ON trend_analysis(crypto_id, timeframe);
CREATE INDEX idx_trend_analysis_type ON trend_analysis(trend_type);
CREATE INDEX idx_trend_analysis_time ON trend_analysis(start_time DESC);
CREATE INDEX idx_trend_analysis_metadata ON trend_analysis USING GIN(metadata);

COMMIT; 