-- Migration: 009_add_coingecko_support.sql
-- Description: Add CoinGecko ID support while maintaining CMC compatibility
-- Date: 2025-01-15

BEGIN;

-- Add coingecko_id column to cryptocurrencies table
ALTER TABLE cryptocurrencies 
ADD COLUMN coingecko_id VARCHAR(100);

-- Create index for coingecko_id
CREATE INDEX idx_cryptocurrencies_coingecko_id ON cryptocurrencies(coingecko_id);

-- Update signal_events enum to include new signal types
ALTER TYPE signal_type_enum ADD VALUE 'parabolic_rise';
ALTER TYPE signal_type_enum ADD VALUE 'capitulation_drop';
ALTER TYPE signal_type_enum ADD VALUE 'low_volume_drift';
ALTER TYPE signal_type_enum ADD VALUE 'gradual_uptrend';
ALTER TYPE signal_type_enum ADD VALUE 'macro_downtrend';

COMMIT; 