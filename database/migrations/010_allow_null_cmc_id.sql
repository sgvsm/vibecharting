-- Migration: 010_allow_null_cmc_id.sql
-- Description: Allow NULL values in cmc_id column to support CoinGecko-only tokens
-- Date: 2025-01-15

BEGIN;

-- Drop the NOT NULL constraint from cmc_id column
ALTER TABLE cryptocurrencies 
ALTER COLUMN cmc_id DROP NOT NULL;

-- Drop the UNIQUE constraint from cmc_id (since we can have multiple NULL values)
ALTER TABLE cryptocurrencies 
DROP CONSTRAINT IF EXISTS cryptocurrencies_cmc_id_key;

-- Recreate the UNIQUE constraint to allow multiple NULL values
CREATE UNIQUE INDEX cryptocurrencies_cmc_id_unique 
ON cryptocurrencies (cmc_id) 
WHERE cmc_id IS NOT NULL;

COMMIT; 