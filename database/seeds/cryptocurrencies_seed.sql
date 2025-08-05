-- Cryptocurrency Seed Data
-- Description: Insert supported cryptocurrencies into the database
-- Note: Update this list with your specific cryptocurrency selections
-- Date: 2025-01-01

BEGIN;

-- Clear existing data (optional, uncomment if needed)
-- DELETE FROM cryptocurrencies;

-- Insert cryptocurrency data
-- Replace these with your specific cryptocurrency list
-- To find CoinMarketCap IDs, visit: https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyMap

INSERT INTO cryptocurrencies (symbol, name, cmc_id, rank, is_active) VALUES
-- Example entries (replace with your specific list):
('BTC', 'Bitcoin', 1, 1, true),
('ETH', 'Ethereum', 1027, 2, true),
('BNB', 'BNB', 1839, 3, true),
('XRP', 'XRP', 52, 4, true),
('ADA', 'Cardano', 2010, 5, true),
('SOL', 'Solana', 5426, 6, true),
('DOGE', 'Dogecoin', 74, 7, true),
('DOT', 'Polkadot', 6636, 8, true),
('AVAX', 'Avalanche', 5805, 9, true),
('MATIC', 'Polygon', 3890, 10, true),
('LTC', 'Litecoin', 2, 11, true),
('UNI', 'Uniswap', 7083, 12, true),
('LINK', 'Chainlink', 1975, 13, true),
('ATOM', 'Cosmos', 3794, 14, true),
('NEAR', 'NEAR Protocol', 6535, 15, true),
('ALGO', 'Algorand', 4030, 16, true),
('XLM', 'Stellar', 512, 17, true),
('VET', 'VeChain', 3077, 18, true),
('ICP', 'Internet Computer', 8916, 19, true),
('FIL', 'Filecoin', 2280, 20, true);

-- Add your additional cryptocurrencies here following the same pattern:
-- ('SYMBOL', 'Full Name', cmc_id, rank, true),

-- Note: To get CoinMarketCap IDs for your tokens:
-- 1. Visit https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyMap
-- 2. Use the API endpoint: https://pro-api.coinmarketcap.com/v1/cryptocurrency/map
-- 3. Or check individual coin pages on CoinMarketCap.com

COMMIT;

-- Query to verify data insertion
SELECT COUNT(*) as total_cryptocurrencies FROM cryptocurrencies WHERE is_active = true; 