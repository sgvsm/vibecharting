-- Updated cryptocurrency seed data with CoinGecko IDs
-- Tokens from Tokens.txt and Tokens2.txt

BEGIN;

-- Clear existing data
DELETE FROM cryptocurrencies;

-- Insert updated cryptocurrency data
INSERT INTO cryptocurrencies (symbol, name, cmc_id, coingecko_id, rank, is_active) VALUES
-- From Tokens.txt (actual CoinGecko token IDs)
('SOL', 'Solana', 5426, '6VKwjoZgzQjfXpxJ9SMo7BYRxHh71xtSLuxzbJ8LXoeF', 1, true),
('BONK', 'Bonk', NULL, 'CN5L4sc6NJEHYGcLX2Rdz9qk4FgTdphJVLWgjNGGovYQ', 2, true),
('JUP', 'Jupiter', NULL, '9Row6Eng2stcho8Cwan6MpaaqQZyJRYyr1UgKDiWWMev', 3, true),
('RAY', 'Raydium', NULL, '8KkFJLYsP4pKRitNXE8XMkAejgtVqtM3qjNV6gTvHXTZ', 4, true),
('SRM', 'Serum', NULL, 'EnWUqfjgAPPQgrmTkeTvRs7FmjgZWReWenUz6SwontGq', 5, true),
('ORCA', 'Orca', NULL, 'C1qmybyyTboDm5A7SmtWcoiqgEYbHBUxxsZUtFj8bgcq', 6, true),
('MNGO', 'Mango', NULL, '7k4KW5SyoaCPoqv9mszRLAqnK1Dtz7ojdWUt8RhSUk7X', 7, true),
('SAMO', 'Samoyedcoin', NULL, 'J2s7qLUqXwa8y4JPZy9wC2Pg3JjBm2Ykj4thonEkKG2Y', 8, true),
('COPE', 'Cope', NULL, '9MTTqM6r7MKM9CGi2DzxR7yA4RhunNn2xeAFn3mDZ6Tm', 9, true),
('FIDA', 'Bonfida', NULL, 'H4uj7z5LExamnP127jAQ5zsk2uqhLrqB3JttMMmZLdNx', 10, true),
('STEP', 'Step', NULL, '4Azvn3yEFb3gUkf47S7k9yq3dLVoX2dGrKdtPmzSFQXK', 11, true),
('ALEPH', 'Aleph.im', NULL, 'Fn1pbVqR1jXhSTaR5t4ZX6eJkqYNQEtCeAu1df6bbLLg', 12, true),
('ATLAS', 'Star Atlas', NULL, 'avapdsss6zgepjje7ppznzmjtkcmn3zu6qwyzfgnhshf', 13, true),
('POLIS', 'Star Atlas DAO', NULL, 'fesficbdffpxdasedo4ybegqde6bbgpztsqmt6enmhdc', 14, true),
('MEDIA', 'Media Network', NULL, 'B1JkXQH1yvTQtRavmAStwoy2Pu54SsjLqfWphL9VwpGu', 15, true),
('AUDIO', 'Audius', NULL, 'Gp5AUb3RUyzevHmtKzfaigHL4ZPh247RFZ76qUsyuyCE', 16, true),
('HNT', 'Helium', NULL, 'GEsHMzMRrDddh2i7dHHHxDKBiN17XHmtHkWoTJrqnKJ8', 17, true),
('IOT', 'Helium IOT', NULL, 'AkePSMmyZ3hg85WyDMFUp1svEhzkbvbmwkSR5JPtbBLV', 18, true),
('MOBILE', 'Helium Mobile', NULL, '966sLyXCxj1HedfdFQsv2LiNHUaUhMNadBcD4kDcJ1MP', 19, true),
('HIVE', 'Hive', NULL, 'yrrustgpugdp8bbfosqdefssen6sa75zs1qjvgnhtmy', 20, true),
('STEEM', 'Steem', NULL, 'ede4v78zjo54dfhcbwm8nmfrlwstvggbcjg8uwh5fsdv', 21, true),
('SBD', 'Steem Dollars', NULL, '34qhkhrhyningwruftqjnb2vfv8oqyqd5tvdwwde1man', 22, true),
('WAX', 'WAX', NULL, '4sx1nlrqik4b9fdlke2dhq9fhvrzjhzkn3lod6brepnf', 23, true),

-- From Tokens2.txt (actual CoinGecko token IDs)
('GST', 'Green Satoshi Token', NULL, 'Gc2diG37yKXgbrEqfaHWBDA3JHaWAxJRcXZ6zASt5sw5', 24, true),
('GMT', 'Green Metaverse Token', NULL, 'DrGtaHdxcGfmsQDWio8EVjVvDeW6RKpx3NXd919irBLV', 25, true),
('STEPN', 'STEPN', NULL, 'Gp5AUb3RUyzevHmtKzfaigHL4ZPh247RFZ76qUsyuyCE', 26, true),
('GST2', 'Green Satoshi Token (BSC)', NULL, '98nocLbiDi9ykAjwAUJW9fnYZsf4L4KLCfH7U2LFXDsv', 27, true),
('GMT2', 'Green Metaverse Token (BSC)', NULL, '4nor6joBE27cv6GQ7nnrAcSL7yQ6H8sKhbM7ctJDmhrN', 28, true),
('STEPN2', 'STEPN (BSC)', NULL, 'AVp673JcMJcX7XMZ64s1tW4SUdy8zuvbqBqiQHeGMwUT', 29, true),
('GST3', 'Green Satoshi Token (Polygon)', NULL, '8biqsLDiRPaPM11S42zKtNaC3WWKF64PNoPG9htzy99n', 30, true),
('GMT3', 'Green Metaverse Token (Polygon)', NULL, 'Fn1pbVqR1jXhSTaR5t4ZX6eJkqYNQEtCeAu1df6bbLLg', 31, true),
('STEPN3', 'STEPN (Polygon)', NULL, 'AMEm6cMirRuHqK7QpoxNSYVc3mAuF7Dxhx5rger8kZaz', 32, true),
('GST4', 'Green Satoshi Token (Avalanche)', NULL, 'Cbiwpjnrc21UAbJqK9CXrJzQxGDp4JHTnFxgkQTeEkFQ', 33, true),
('GMT4', 'Green Metaverse Token (Avalanche)', NULL, 'C1qmybyyTboDm5A7SmtWcoiqgEYbHBUxxsZUtFj8bgcq', 34, true),
('STEPN4', 'STEPN (Avalanche)', NULL, 'ArQNTJtmxuWQ77KB7a1PmoZc5Zd25jXmXPDWBX8qVoux', 35, true);

COMMIT;

-- Verify data insertion
SELECT COUNT(*) as total_cryptocurrencies FROM cryptocurrencies WHERE is_active = true;
SELECT symbol, name, coingecko_id FROM cryptocurrencies WHERE is_active = true ORDER BY rank; 