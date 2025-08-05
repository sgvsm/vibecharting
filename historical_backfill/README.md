# 🏛️ Historical Data Backfill Script

## 📋 Overview

This script fetches 30 days of historical daily OHLCV data for all active Solana pools from CoinGecko's On-Chain DEX API and stores them in the database for trend analysis.

## 📊 What It Does

- Fetches **30 days** of daily historical data for **35 Solana pools**
- Uses CoinGecko's On-Chain DEX API (OHLCV endpoint)
- Stores data in existing `price_data` table
- Respects rate limits (30 req/min)
- Skips pools that already have sufficient data
- Provides detailed progress logging

## 🚀 Quick Start

### Prerequisites

1. **Environment Variables** (same as Lambda function):
   ```bash
   export COINGECKO_API_KEY="your_coingecko_api_key"
   export DB_HOST="your_db_host"
   export DB_NAME="vibe_charting"
   export DB_USERNAME="vibecharting"
   export DB_PASSWORD="your_password"
   export DB_PORT="5432"
   
   # Optional: Date range mode
   export START_DATE="2024-12-01"
   export END_DATE="2024-12-31"
   ```

2. **Python Dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

### Execution

```bash
# Run the historical backfill (last 30 days)
python3 main_script.py

# Run with specific date range
export START_DATE="2024-12-01"
export END_DATE="2024-12-31"
python3 main_script.py
```

## 📁 File Structure

```
historical_backfill/
├── main_script.py          # Main execution script
├── config.py               # Configuration and environment variables
├── database_client.py      # Database operations
├── historical_client.py    # CoinGecko On-Chain DEX API client
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `COINGECKO_API_KEY` | CoinGecko API key (used for GeckoTerminal) | `your_coingecko_api_key` |
| `DB_HOST` | Database host | `vibe-charting-db.c9qmo8w2y0a1.us-east-2.rds.amazonaws.com` |
| `DB_NAME` | Database name | `vibe_charting` |
| `DB_USERNAME` | Database username | `vibecharting` |
| `DB_PASSWORD` | Database password | `your_password` |
| `DB_PORT` | Database port | `5432` |
| `START_DATE` | Start date for data range (optional) | `2024-12-01` |
| `END_DATE` | End date for data range (optional) | `2024-12-31` |

### Script Configuration

In `config.py`:
- **Rate limit delay**: 2 seconds between requests
- **Days to fetch**: 30 days (default)
- **Max retries**: 3 attempts per request
- **Skip existing**: Skip pools with sufficient data
- **Date range mode**: Optional START_DATE/END_DATE environment variables

## 📊 Expected Output

```
============================================================
🏛️  HISTORICAL DATA BACKFILL - 30 DAYS
============================================================
Started at: 2025-01-15 10:30:00 UTC
Target: 30 days of daily OHLCV data
Rate limit: 2s between requests
============================================================

🔍 Validating environment...
✅ Database connection: OK
✅ CoinGecko API connection: OK
✅ Environment validation passed

🔧 Initializing clients...
✅ Configuration loaded successfully
   - Database: your-db-host/vibe_charting
   - API Key: Present
   - Historical period: 30 days
   - Rate limit delay: 2 seconds

📋 Fetching active pools...
✅ Found 35 active pools

🎯 Processing 35 active pools...

[1/35] Processing SOL...
   Fetching historical data for SOL (6VKwjoZg...)
   API response received: 30 data points
   ✅ Stored 30 historical records for crypto_id 1
   ✅ Successfully processed SOL: 30 records

[2/35] Processing BONK...
   Pool ID 2 already has 28 historical records (sufficient)
   ⏭️  Skipping BONK - already has sufficient historical data

... (continues for all pools)

============================================================
📊 BACKFILL SUMMARY
============================================================
✅ Successful pools: 33
⏭️  Skipped pools (had data): 2
❌ Failed pools: 0
📊 Total records stored: 990
⏱️  Total execution time: 75.45 seconds

============================================================

🎉 All pools processed successfully!
🏁 Backfill completed at: 2025-01-15 10:31:15 UTC
```

## 🔧 Features

### Smart Skipping
- Checks existing data before fetching
- Skips pools with 80%+ coverage (24+ records for 30 days)
- Prevents duplicate work on re-runs

### Error Handling
- Continues processing other pools if one fails
- Retries failed requests (up to 3 times)
- Logs all failures for review

### Rate Limit Compliance
- 2-second delay between API requests
- Respects CoinGecko's 30 req/min limit
- Handles 429 rate limit responses gracefully

### Progress Tracking
- Real-time progress updates
- Detailed logging per pool
- Summary report at completion
- Database progress logging

## 📈 Data Format

Historical data is stored in the same format as current price data:

```sql
INSERT INTO price_data (
    crypto_id,           -- Internal pool ID
    timestamp,           -- Historical date from API
    price_usd,           -- Close price from OHLCV
    volume_24h,          -- Volume from OHLCV
    market_cap,          -- NULL (not in OHLCV)
    percent_change_1h,   -- NULL (not in OHLCV)
    percent_change_24h,  -- NULL (not in OHLCV)  
    percent_change_7d    -- NULL (not in OHLCV)
);
```

## 🚨 Troubleshooting

### Common Issues

1. **"COINGECKO_API_KEY environment variable required"**
   - Solution: Set the `COINGECKO_API_KEY` environment variable

2. **"Missing required database environment variables"**
   - Solution: Set all database environment variables (DB_HOST, DB_NAME, etc.)

3. **"API connection test failed"**
   - Check API key validity
   - Verify internet connection
   - Check CoinGecko API status

4. **"Database connection failed"**
   - Verify database credentials
   - Check database accessibility from EC2
   - Ensure database is running

### Rate Limiting

If you hit rate limits:
- Script automatically handles 429 responses
- Increases delay for rate-limited requests
- Consider reducing concurrent operations

### Memory Issues

Script processes one pool at a time to minimize memory usage:
- ~30 data points per pool × 35 pools = ~1,050 total points
- Minimal memory footprint
- Should run fine on basic EC2 instances

## 📊 Validation

After completion, validate results:

```sql
-- Check data coverage per pool
SELECT 
    c.symbol,
    COUNT(pd.id) as record_count,
    MIN(pd.timestamp) as earliest_data,
    MAX(pd.timestamp) as latest_data
FROM cryptocurrencies c
LEFT JOIN price_data pd ON c.id = pd.crypto_id
WHERE c.is_active = true
GROUP BY c.id, c.symbol
ORDER BY c.symbol;

-- Check daily coverage
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as pools_with_data
FROM price_data
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## 🎯 Success Criteria

- ✅ 30 days of historical data for each active pool
- ✅ No rate limit violations
- ✅ No duplicate records in database
- ✅ Proper timestamp handling
- ✅ Sufficient data for trend analysis (20+ records per pool)

## 🔧 Important Fix (August 2025)

The CoinGecko API response structure was updated. The OHLCV data is now located at:
```
data.data.attributes.ohlcv_list
```

Previously, the code was looking for it at:
```
data.data.ohlcv_list  # This path no longer works
```

This fix has been applied to `historical_client.py` in the `transform_ohlcv_data` method.

---

**Ready for historical data backfill!** 🚀