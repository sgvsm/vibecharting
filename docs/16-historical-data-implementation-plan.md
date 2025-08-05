# 📋 **Historical Data Ingestion Implementation Plan**

## 🎯 **Objective**
Create an EC2 script to backfill **30 days** of daily historical data for all 35 Solana pools, then return Lambda to regular daily/hourly ingestion.

## 🔍 **API Research Results**

Based on research from [CoinGecko API documentation](https://docs.coingecko.com/v3.0.1/reference/introduction):

### **Rate Limits** ([Source](https://docs.coingecko.com/reference/common-errors-rate-limit))
- **Free Tier (Demo Plan)**: ~30 calls per minute
- **Variable rate**: Depends on traffic size
- **API Key**: Required for Demo plan (via header: `x-cg-demo-api-key`)

### **Historical Data Endpoints** ([Source](https://docs.coingecko.com/reference/pool-ohlcv-contract-address))
**OHLCV Pool Endpoint:**
```
GET /api/v3/onchain/networks/solana/pools/{pool_address}/ohlcv/day
```

**Parameters:**
- `network`: `solana`
- `pool_address`: Pool contract address 
- `timeframe`: `day` (for daily data)
- `limit`: 30 (for 30 days of data)
- `before_timestamp`: Unix timestamp for pagination (if needed)

### **Data Granularity** ([Source](https://docs.coingecko.com/docs/2-get-historical-data))
- **Daily data**: For periods above 90 days (automatic)
- **30-day scope**: Perfect for daily granularity
- **Data availability**: Most pools should have 30+ days of history

## 📊 **Updated Implementation Strategy**

### **Reduced Scope Benefits:**
- **30 days × 35 pools = 1,050 data points** (vs 3,150 for 90 days)
- **API calls**: 35 requests total (vs 105+ for 90 days)
- **Execution time**: ~70 seconds (vs 210+ seconds)
- **Rate limit safety**: Well under 30 req/min limit
- **Sufficient data**: 30 points per coin for meaningful trend analysis

### **Phase 1: File Structure**

**EC2 Script Files:**
```
historical_backfill/
├── historical_client.py      # CoinGecko OHLCV client with 30-day scope
├── database_client.py        # Database operations
├── main_script.py           # Main execution script
├── config.py                # API keys and settings
├── requirements.txt         # Python dependencies
└── README.md                # Execution instructions
```

### **Phase 2: Rate Limit Strategy**

**Optimized Execution Plan:**
- **Total API calls**: 35 requests (one per pool)
- **Delay between requests**: 2 seconds (safety margin)
- **Total execution time**: ~70 seconds
- **Rate limit compliance**: 30 req/min = well under limit
- **Error handling**: Continue on individual pool failures

### **Phase 3: API Implementation**

**Historical Client Features:**
```python
class CoinGeckoHistoricalClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.coingecko.com/api/v3"
        self.rate_limit_delay = 2  # seconds between requests
        self.days_to_fetch = 30   # 30 days of historical data
    
    def get_pool_historical_data(self, pool_address):
        """Fetch 30 days of daily OHLCV data for a pool"""
        url = f"{self.base_url}/onchain/networks/solana/pools/{pool_address}/ohlcv/day"
        headers = {"x-cg-demo-api-key": self.api_key}
        params = {"limit": 30}  # 30 days of daily data
        
        # Make request with rate limiting
        response = requests.get(url, headers=headers, params=params)
        time.sleep(self.rate_limit_delay)
        
        return self.transform_ohlcv_data(response.json())
    
    def transform_ohlcv_data(self, api_response):
        """Transform OHLCV data to price_data format"""
        # Transform: [timestamp, open, high, low, close, volume]
        # To: price_data table format
```

**Database Client Features:**
```python
class HistoricalDatabaseClient:
    def __init__(self):
        # Use same database configuration as Lambda
        self.load_database_config()
    
    def check_existing_historical_data(self, pool_id, days=30):
        """Check if pool already has sufficient historical data"""
        # Count existing records for past 30 days
        # Return True if already has enough data
    
    def store_historical_data(self, crypto_id, historical_data):
        """Store historical OHLCV data in price_data table"""
        # Insert with historical timestamps
        # Use existing unique constraints to prevent duplicates
    
    def get_active_pools(self):
        """Get list of active Solana pools from cryptocurrencies table"""
        # Return list of pools with coingecko_id
```

### **Phase 4: Main Script Implementation**

**Execution Flow:**
```python
def main():
    print("=== Historical Data Backfill - 30 Days ===")
    
    # 1. Initialize clients
    api_client = CoinGeckoHistoricalClient(api_key)
    db_client = HistoricalDatabaseClient()
    
    # 2. Get active pools
    active_pools = db_client.get_active_pools()
    print(f"Found {len(active_pools)} active pools")
    
    # 3. Process each pool
    successful_pools = 0
    failed_pools = []
    
    for pool in active_pools:
        try:
            # Check if already has data
            if db_client.check_existing_historical_data(pool['id']):
                print(f"Pool {pool['symbol']} already has historical data, skipping")
                continue
            
            # Fetch 30 days of historical data
            print(f"Fetching historical data for {pool['symbol']}...")
            historical_data = api_client.get_pool_historical_data(pool['coingecko_id'])
            
            # Store in database
            db_client.store_historical_data(pool['id'], historical_data)
            successful_pools += 1
            print(f"✅ Successfully processed {pool['symbol']}")
            
        except Exception as e:
            print(f"❌ Failed to process {pool['symbol']}: {str(e)}")
            failed_pools.append(pool['symbol'])
            continue
    
    # 4. Generate completion report
    print(f"\n=== Backfill Complete ===")
    print(f"Successful pools: {successful_pools}")
    print(f"Failed pools: {len(failed_pools)}")
    if failed_pools:
        print(f"Failed pool symbols: {', '.join(failed_pools)}")
```

## 🔧 **EC2 Deployment Guide**

### **Step 1: File Preparation**

**Create script files locally:**
```bash
# Create directory structure
mkdir -p historical_backfill
cd historical_backfill

# Files will be created:
# - historical_client.py
# - database_client.py  
# - main_script.py
# - config.py
# - requirements.txt
# - README.md
```

### **Step 2: Upload to EC2**
```bash
# Upload entire directory to EC2
scp -r historical_backfill/ ec2-user@your-ec2-ip:/home/ec2-user/

# Or upload individual files
scp historical_backfill/* ec2-user@your-ec2-ip:/home/ec2-user/historical_backfill/
```

### **Step 3: EC2 Execution**
```bash
# SSH to EC2 instance
ssh ec2-user@your-ec2-ip

# Navigate to script directory
cd historical_backfill

# Install Python dependencies
pip3 install -r requirements.txt

# Run historical backfill script
python3 main_script.py
```

### **Step 4: Monitor Progress**
```bash
# Expected output:
=== Historical Data Backfill - 30 Days ===
Found 35 active pools
Fetching historical data for SOL...
✅ Successfully processed SOL
Fetching historical data for BONK...
✅ Successfully processed BONK
...
=== Backfill Complete ===
Successful pools: 35
Failed pools: 0
```

## 📊 **Expected Outcomes**

### **Data Collection Results:**
- **30 days × 35 pools = 1,050 historical data points**
- **Daily granularity** sufficient for trend analysis
- **OHLCV format**: Open, High, Low, Close, Volume data
- **Historical timestamps** from API responses

### **Performance Metrics:**
- **Total API calls**: 35 requests
- **Execution time**: ~70 seconds
- **Rate limit compliance**: Well under 30 req/min
- **Memory usage**: Minimal (processing one pool at a time)
- **Success rate**: Expected >90% success

### **Database Integration:**
- **Table**: Existing `price_data` table
- **Timestamps**: Historical dates from API
- **Duplicates**: Prevented by existing unique constraints
- **Format**: Consistent with current Lambda data

## ✅ **Validation Checklist**

### **Pre-Execution:**
- [ ] EC2 instance accessible via SSH
- [ ] Database connection from EC2 verified
- [ ] CoinGecko Demo API key obtained
- [ ] Script files uploaded and tested

### **Post-Execution:**
- [ ] Verify 30 data points per pool in database
- [ ] Check data quality and timestamp accuracy
- [ ] Confirm no duplicate records created
- [ ] Test trend analysis with historical data
- [ ] Validate Lambda continues normal operation

### **SQL Validation Queries:**
```sql
-- Check historical data count per pool
SELECT 
    c.symbol,
    COUNT(pd.id) as historical_records,
    MIN(pd.timestamp) as earliest_data,
    MAX(pd.timestamp) as latest_data
FROM cryptocurrencies c
LEFT JOIN price_data pd ON c.id = pd.crypto_id
WHERE c.is_active = true
GROUP BY c.id, c.symbol
ORDER BY c.symbol;

-- Verify 30-day coverage
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as pools_with_data
FROM price_data
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

## 🚀 **Implementation Timeline**

### **Phase 1: Development (30 minutes)**
- Create all script files
- Test database connection
- Validate API endpoint

### **Phase 2: Deployment (10 minutes)**
- Upload files to EC2
- Install dependencies
- Configure environment

### **Phase 3: Execution (5 minutes)**
- Run historical backfill script
- Monitor progress
- Verify completion

### **Phase 4: Validation (15 minutes)**
- Check database results
- Validate data quality
- Test trend analysis readiness

**Total time**: ~60 minutes for complete implementation

## 🎯 **Success Criteria**

### **Technical Success:**
- ✅ 30 days of historical data for each active pool
- ✅ No rate limit violations during execution
- ✅ No duplicate records in database
- ✅ Proper timestamp handling

### **Business Success:**
- ✅ Sufficient data for meaningful trend analysis
- ✅ Trend analysis functions work with historical baseline
- ✅ Lambda function continues normal operation
- ✅ Ready for production trend analysis

## 📝 **Next Steps**

1. **Create script files** with 30-day implementation
2. **Test locally** with sample pool (if possible)
3. **Upload to EC2** and execute
4. **Validate results** and data quality
5. **Enable trend analysis** with historical baseline

**Ready to proceed with 30-day historical data implementation!**