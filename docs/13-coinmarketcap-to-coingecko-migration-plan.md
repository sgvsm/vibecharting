# CoinMarketCap to CoinGecko Migration Plan

## Overview

This document outlines the step-by-step plan to migrate from CoinMarketCap API to CoinGecko API and enhance trend detection patterns. The migration includes database schema updates, API client changes, and new trend detection algorithms.

## Current State Analysis

### Database Schema
- `cryptocurrencies` table has `cmc_id` field (CoinMarketCap ID)
- `price_data` table stores price information
- `trend_analysis` table stores trend analysis results
- `signal_events` table stores market signals

### Current Trend Detection (4/15 patterns supported)
✅ **Already Supported:**
- Sideways trend
- Bottoming out  
- Pump and dump
- Volatility spike

🟡 **Quick Wins (2/15):**
- Gradual uptrend
- Macro downtrend

⭐ **Medium Effort (3/15):**
- Parabolic rise
- Capitulation drop
- Low-volume drift

## Migration Plan

### Phase 1: Database Schema Updates

#### 1.1 Create Migration Script
```sql
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
```

#### 1.2 Update Seed Data
Create new seed file with CoinGecko token IDs from Tokens.txt and Tokens2.txt:

```sql
-- Updated seed data with CoinGecko IDs
INSERT INTO cryptocurrencies (symbol, name, cmc_id, coingecko_id, rank, is_active) VALUES
('SOL', 'Solana', 5426, 'solana', 1, true),
('BONK', 'Bonk', NULL, 'bonk', 2, true),
('JUP', 'Jupiter', NULL, 'jupiter', 3, true),
-- Add all tokens from Tokens.txt and Tokens2.txt
```

### Phase 2: API Client Migration

#### 2.1 Create CoinGecko Client
Replace `cmc_client.py` with `coingecko_client.py`:

```python
class CoinGeckoClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = 'https://api.coingecko.com/api/v3'
        self.session = requests.Session()
        
    def get_latest_quotes(self, coingecko_ids: List[str]) -> Dict[str, Any]:
        """Fetch latest quotes for specified CoinGecko IDs"""
        # Implementation for CoinGecko API
```

#### 2.2 Update Handler
Modify `handler.py` to use CoinGecko client:

```python
# Replace CMC client with CoinGecko client
coingecko_client = CoinGeckoClient()  # CoinGecko has free tier
```

### Phase 3: Enhanced Trend Detection

#### 3.1 Update Trend Analyzer
Add new trend detection methods:

```python
def detect_gradual_uptrend(self, price_data: List[Dict]) -> Optional[Dict]:
    """Detect gradual uptrend vs sharp rises"""
    
def detect_macro_downtrend(self, price_data: List[Dict]) -> Optional[Dict]:
    """Detect long-term downtrends with duration analysis"""
    
def detect_parabolic_rise(self, price_data: List[Dict]) -> Optional[Dict]:
    """Detect exponential price increases"""
    
def detect_capitulation_drop(self, price_data: List[Dict]) -> Optional[Dict]:
    """Detect panic selling events"""
    
def detect_low_volume_drift(self, price_data: List[Dict]) -> Optional[Dict]:
    """Detect quiet price movements with low volume"""
```

#### 3.2 Update Signal Detector
Add new signal detection methods:

```python
def _detect_parabolic_rise(self, price_data: List[Dict], crypto_id: int) -> List[Dict]:
    """Detect parabolic price increases"""
    
def _detect_capitulation_drop(self, price_data: List[Dict], crypto_id: int) -> List[Dict]:
    """Detect capitulation selling patterns"""
    
def _detect_low_volume_drift(self, price_data: List[Dict], crypto_id: int) -> List[Dict]:
    """Detect low-volume price movements"""
```

### Phase 4: AWS Configuration Updates

#### 4.1 Update Secrets Manager
1. Create new secret for CoinGecko API key (optional, free tier available)
2. Update environment variables in Lambda functions

#### 4.2 Update Lambda Functions
1. Upload new code with CoinGecko client
2. Update requirements.txt if needed
3. Test functions in AWS Console

## Implementation Steps

### Step 1: Database Migration (AWS CLI)

```bash
# Connect to RDS instance
psql -h [DB_ENDPOINT] -U vibecharting -d vibe_charting

# Run migration
\i 009_add_coingecko_support.sql

# Update seed data
\i updated_cryptocurrencies_seed.sql
```

### Step 2: Update Lambda Functions

#### 2.1 Data Ingestion Function
1. Replace `cmc_client.py` with `coingecko_client.py`
2. Update `handler.py` to use CoinGecko client
3. Update `database.py` to handle CoinGecko IDs
4. Upload to AWS Lambda

#### 2.2 Trend Analysis Function
1. Update `trend_analyzer.py` with new detection methods
2. Update `signal_detector.py` with new signal types
3. Upload to AWS Lambda

### Step 3: Test and Deploy

1. Test data ingestion with new API
2. Test trend analysis with new patterns
3. Monitor CloudWatch logs
4. Verify data quality

## Risk Assessment

### Low Risk
- Database schema changes are additive (backward compatible)
- CoinGecko has free tier with generous limits
- New trend detection is additive

### Medium Risk
- API response format differences
- Rate limiting differences
- Data quality variations

### Mitigation
- Maintain CMC compatibility during transition
- Implement proper error handling
- Add monitoring for data quality

## Timeline

- **Week 1**: Database migration and schema updates
- **Week 2**: API client development and testing
- **Week 3**: Enhanced trend detection implementation
- **Week 4**: AWS deployment and testing

## Success Criteria

1. ✅ Data ingestion working with CoinGecko API
2. ✅ All existing trend detection patterns working
3. ✅ New trend detection patterns implemented
4. ✅ No data loss during migration
5. ✅ Performance maintained or improved

## Rollback Plan

If issues arise:
1. Revert Lambda functions to CMC client
2. Keep database schema changes (additive)
3. Disable new trend detection patterns
4. Monitor and fix issues before re-deployment 