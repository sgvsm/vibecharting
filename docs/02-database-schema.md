# Database Schema Design

## Overview

The PostgreSQL database stores cryptocurrency price data, analysis results, and metadata required for the trend analysis chatbot. The schema is designed for time-series data with efficient querying for trend analysis.

## Schema Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   cryptocurrencies    │    price_data        │   trend_analysis     │
│                 │    │                 │    │                 │
│ id (PK)         │◄───┤ crypto_id (FK)  │    │ id (PK)         │
│ symbol          │    │ timestamp       │    │ crypto_id (FK)  │◄──┐
│ name            │    │ price_usd       │    │ timeframe       │   │
│ cmc_id          │    │ volume_24h      │    │ trend_type      │   │
│ rank            │    │ market_cap      │    │ confidence      │   │
│ is_active       │    │ created_at      │    │ start_time      │   │
│ created_at      │    └─────────────────┘    │ end_time        │   │
│ updated_at      │                           │ created_at      │   │
└─────────────────┘                           └─────────────────┘   │
                                                        │            │
┌─────────────────┐    ┌─────────────────┐             │            │
│   signal_events      │   query_logs         │             │            │
│                 │    │                 │             │            │
│ id (PK)         │    │ id (PK)         │             │            │
│ crypto_id (FK)  │◄───┤ query_text      │             │            │
│ signal_type     │    │ intent          │             │            │
│ detected_at     │    │ response_count  │             │            │
│ confidence      │    │ execution_time  │             │            │
│ metadata        │    │ created_at      │             │            │
│ created_at      │    └─────────────────┘             │            │
└─────────────────┘                                    │            │
         ▲                                             │            │
         └─────────────────────────────────────────────┘            │
                                                                    │
┌─────────────────┐                                                │
│   analysis_runs      │                                                │
│                 │                                                │
│ id (PK)         │                                                │
│ run_type        │◄───────────────────────────────────────────────┘
│ started_at      │
│ completed_at    │
│ status          │
│ processed_count │
│ error_message   │
└─────────────────┘
```

## Table Definitions

### 1. cryptocurrencies

Stores metadata about supported cryptocurrencies.

```sql
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

-- Indexes
CREATE INDEX idx_cryptocurrencies_symbol ON cryptocurrencies(symbol);
CREATE INDEX idx_cryptocurrencies_cmc_id ON cryptocurrencies(cmc_id);
CREATE INDEX idx_cryptocurrencies_active ON cryptocurrencies(is_active) WHERE is_active = true;
```

### 2. price_data

Stores historical price and volume data for each cryptocurrency.

```sql
CREATE TABLE price_data (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    price_usd DECIMAL(20, 8) NOT NULL,
    volume_24h DECIMAL(20, 2),
    market_cap DECIMAL(20, 2),
    percent_change_1h DECIMAL(10, 4),
    percent_change_24h DECIMAL(10, 4),
    percent_change_7d DECIMAL(10, 4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(crypto_id, timestamp)
);

-- Indexes for time-series queries
CREATE INDEX idx_price_data_crypto_timestamp ON price_data(crypto_id, timestamp DESC);
CREATE INDEX idx_price_data_timestamp ON price_data(timestamp DESC);
CREATE INDEX idx_price_data_crypto_id ON price_data(crypto_id);

-- Partition by month for better performance (optional)
-- ALTER TABLE price_data PARTITION BY RANGE (timestamp);
```

### 3. trend_analysis

Stores pre-computed trend analysis results for different timeframes.

```sql
CREATE TYPE trend_type_enum AS ENUM ('uptrend', 'downtrend', 'sideways');
CREATE TYPE timeframe_enum AS ENUM ('1h', '24h', '7d', '30d');

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

-- Indexes
CREATE INDEX idx_trend_analysis_crypto_timeframe ON trend_analysis(crypto_id, timeframe);
CREATE INDEX idx_trend_analysis_type ON trend_analysis(trend_type);
CREATE INDEX idx_trend_analysis_time ON trend_analysis(start_time DESC);
CREATE INDEX idx_trend_analysis_metadata ON trend_analysis USING GIN(metadata);
```

### 4. signal_events

Stores detected market signals (pump & dump, bottomed out, etc.).

```sql
CREATE TYPE signal_type_enum AS ENUM ('pump_and_dump', 'bottomed_out', 'breakout', 'breakdown');

CREATE TABLE signal_events (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    signal_type signal_type_enum NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    confidence DECIMAL(5, 4) CHECK (confidence >= 0 AND confidence <= 1),
    trigger_price DECIMAL(20, 8),
    volume_spike_ratio DECIMAL(10, 4), -- For pump & dump detection
    metadata JSONB, -- Signal-specific data
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_signal_events_crypto_type ON signal_events(crypto_id, signal_type);
CREATE INDEX idx_signal_events_detected_at ON signal_events(detected_at DESC);
CREATE INDEX idx_signal_events_active ON signal_events(is_active) WHERE is_active = true;
CREATE INDEX idx_signal_events_metadata ON signal_events USING GIN(metadata);
```

### 5. analysis_runs

Tracks analysis job executions for monitoring and debugging.

```sql
CREATE TYPE run_status_enum AS ENUM ('running', 'completed', 'failed', 'cancelled');
CREATE TYPE run_type_enum AS ENUM ('data_ingestion', 'trend_analysis', 'signal_detection');

CREATE TABLE analysis_runs (
    id SERIAL PRIMARY KEY,
    run_type run_type_enum NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status run_status_enum DEFAULT 'running',
    processed_count INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB
);

-- Indexes
CREATE INDEX idx_analysis_runs_type_status ON analysis_runs(run_type, status);
CREATE INDEX idx_analysis_runs_started_at ON analysis_runs(started_at DESC);
```

### 6. query_logs

Logs user queries for analytics and system improvement.

```sql
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    intent VARCHAR(50), -- detected intent (uptrend, downtrend, etc.)
    response_count INTEGER,
    execution_time_ms INTEGER,
    user_session_id VARCHAR(100), -- For future user tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_query_logs_intent ON query_logs(intent);
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at DESC);
```

## Data Retention Policies

### Automated Cleanup Jobs

```sql
-- Clean up old price data (keep 30 days)
DELETE FROM price_data 
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '30 days';

-- Clean up old query logs (keep 7 days)
DELETE FROM query_logs 
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';

-- Clean up old analysis results (keep 90 days)
DELETE FROM trend_analysis 
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';

DELETE FROM signal_events 
WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '90 days';

-- Clean up old analysis runs (keep 30 days)
DELETE FROM analysis_runs 
WHERE started_at < CURRENT_TIMESTAMP - INTERVAL '30 days';
```

## Sample Data Queries

### Most Recent Price Data
```sql
SELECT c.symbol, pd.price_usd, pd.timestamp
FROM price_data pd
JOIN cryptocurrencies c ON pd.crypto_id = c.id
WHERE pd.timestamp = (
    SELECT MAX(timestamp) 
    FROM price_data pd2 
    WHERE pd2.crypto_id = pd.crypto_id
)
ORDER BY c.symbol;
```

### Current Uptrends (24h)
```sql
SELECT c.symbol, ta.confidence, ta.price_change_percent
FROM trend_analysis ta
JOIN cryptocurrencies c ON ta.crypto_id = c.id
WHERE ta.timeframe = '24h' 
  AND ta.trend_type = 'uptrend'
  AND ta.end_time >= CURRENT_TIMESTAMP - INTERVAL '2 hours'
ORDER BY ta.confidence DESC;
```

### Recent Signal Events
```sql
SELECT c.symbol, se.signal_type, se.detected_at, se.confidence
FROM signal_events se
JOIN cryptocurrencies c ON se.crypto_id = c.id
WHERE se.detected_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
  AND se.is_active = true
ORDER BY se.detected_at DESC;
```

## Performance Considerations

1. **Partitioning**: Consider partitioning `price_data` by month for large datasets
2. **Indexing**: Composite indexes on frequently queried columns
3. **Archival**: Move old data to cheaper storage after retention period
4. **Connection Pooling**: Use connection pooling in Lambda functions
5. **Query Optimization**: Regular ANALYZE and VACUUM operations 