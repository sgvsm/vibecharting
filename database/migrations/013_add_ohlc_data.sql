-- Migration: 013_add_ohlc_data.sql
-- Description: Add OHLC (Open, High, Low, Close) columns to price_data table
-- Date: 2025-01-11

BEGIN;

-- Add OHLC columns
ALTER TABLE price_data 
ADD COLUMN IF NOT EXISTS open DECIMAL(20, 8),
ADD COLUMN IF NOT EXISTS high DECIMAL(20, 8),
ADD COLUMN IF NOT EXISTS low DECIMAL(20, 8),
ADD COLUMN IF NOT EXISTS close DECIMAL(20, 8);

-- Migrate existing price_usd data to close column for backward compatibility
UPDATE price_data 
SET close = price_usd 
WHERE close IS NULL AND price_usd IS NOT NULL;

-- For initial migration, set OHLC values to be the same as close
-- This allows the system to work with existing data
UPDATE price_data 
SET 
    open = COALESCE(open, close),
    high = COALESCE(high, close),
    low = COALESCE(low, close)
WHERE close IS NOT NULL;

-- Add comment explaining the columns
COMMENT ON COLUMN price_data.open IS 'Opening price for the period';
COMMENT ON COLUMN price_data.high IS 'Highest price during the period';
COMMENT ON COLUMN price_data.low IS 'Lowest price during the period';
COMMENT ON COLUMN price_data.close IS 'Closing price for the period (same as price_usd for backward compatibility)';

-- Create index on close column for efficient queries
CREATE INDEX IF NOT EXISTS idx_price_data_close ON price_data(crypto_id, timestamp DESC, close);

COMMIT;