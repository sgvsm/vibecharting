# Database Migrations

## Overview

This directory contains all database migrations for the Vibe Charting project. Migrations are applied in order based on their numeric prefix.

## Migration Files

1. `001_create_cryptocurrencies.sql` - Base table for cryptocurrency metadata
2. `002_create_price_data.sql` - Historical price and volume data
3. `003_create_trend_analysis.sql` - Trend analysis results
4. `004_create_signal_events.sql` - Market signal detection events
5. `005_create_analysis_runs.sql` - Analysis job execution tracking
6. `006_create_query_logs.sql` - User query logging
7. `007_create_cleanup_jobs.sql` - Data retention cleanup functions
8. `008_create_indexes.sql` - Performance optimization indexes

## Running Migrations

### Prerequisites

1. PostgreSQL database connection details:
   ```
   DB_HOST=your-db-host
   DB_NAME=vibe_charting
   DB_USER=your-username
   DB_PASSWORD=your-password
   ```

2. Python requirements:
   ```
   psycopg2-binary>=2.9.9
   ```

### Running Migrations

1. **Set environment variables:**
   ```bash
   export DB_HOST=your-db-host
   export DB_NAME=vibe_charting
   export DB_USER=your-username
   export DB_PASSWORD=your-password
   ```

2. **Run migration script:**
   ```bash
   python 000_migration_runner.py
   ```

The script will:
- Create a migrations tracking table if it doesn't exist
- Apply any new migrations in order
- Skip already applied migrations
- Roll back failed migrations

### Adding New Migrations

1. Create a new file with format: `NNN_description.sql`
2. Start file with:
   ```sql
   -- Migration: NNN_description.sql
   -- Description: What this migration does
   -- Date: YYYY-MM-DD
   
   BEGIN;
   
   -- Your SQL here
   
   COMMIT;
   ```
3. Test migration locally before committing

### Rollback

Each migration should be manually rolled back in reverse order if needed:

```sql
-- Example rollback for 001_create_cryptocurrencies.sql
BEGIN;
DROP TABLE IF EXISTS cryptocurrencies CASCADE;
DELETE FROM migrations WHERE migration_name = '001_create_cryptocurrencies.sql';
COMMIT;
```

## Data Retention

- Price data: 30 days
- Trend analysis: 90 days
- Signal events: 90 days
- Analysis runs: 30 days
- Query logs: 7 days

Cleanup jobs run automatically via the `run_all_cleanup_jobs()` function.

## Performance

- Indexes are optimized for time-series queries
- Partial indexes for recent data
- Statistics hints for query planner
- Consider enabling partitioning for `price_data` if dataset grows large

## Security

- All timestamps use `WITH TIME ZONE`
- Proper foreign key constraints
- Check constraints on numeric fields
- No raw user input in table/column names 