#!/usr/bin/env python3
"""
Database client for historical data backfill operations
"""

import pg8000
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from config import config

class HistoricalDatabaseClient:
    """Database client for historical data operations"""
    
    def __init__(self):
        self.conn = None
        self.db_config = config.get_db_config()
    
    def connect(self) -> None:
        """Establish database connection"""
        try:
            self.conn = pg8000.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port']
            )
            print("✅ Database connection established successfully")
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            raise
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")
    
    def get_active_pools(self) -> List[Dict[str, Any]]:
        """Get all active cryptocurrencies with Solana pool IDs"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, symbol, coingecko_id, is_active
                    FROM cryptocurrencies 
                    WHERE is_active = true 
                    AND coingecko_id IS NOT NULL
                    ORDER BY name
                """)
                results = cur.fetchall()
                
                # Convert to list of dictionaries
                pools = []
                for row in results:
                    pools.append({
                        'id': row[0],
                        'name': row[1],
                        'symbol': row[2],
                        'coingecko_id': row[3],
                        'is_active': row[4]
                    })
                
                print(f"✅ Found {len(pools)} active pools")
                return pools
                
        except Exception as e:
            print(f"❌ Error fetching active pools: {e}")
            raise
    
    def check_existing_historical_data(self, crypto_id: int, days: int = 30, start_date: str = None, end_date: str = None) -> bool:
        """Check if pool already has sufficient historical data"""
        try:
            with self.conn.cursor() as cur:
                if start_date and end_date:
                    # Check for data in specific date range
                    from datetime import datetime
                    start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                    end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                    
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM price_data 
                        WHERE crypto_id = %s 
                        AND DATE(timestamp) BETWEEN %s AND %s
                    """, (crypto_id, start_date, end_date))
                    
                    count = cur.fetchone()[0]
                    expected_days = (end_dt - start_dt).days + 1
                    has_sufficient_data = count >= (expected_days * 0.8)  # Allow for 80% coverage
                    
                    if has_sufficient_data:
                        print(f"   Pool ID {crypto_id} already has {count} historical records for {start_date} to {end_date} (sufficient)")
                    else:
                        print(f"   Pool ID {crypto_id} has {count} historical records for {start_date} to {end_date} (insufficient, fetching)")
                    
                    return has_sufficient_data
                else:
                    # Check for data in the last N days
                    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                    
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM price_data 
                        WHERE crypto_id = %s 
                        AND timestamp >= %s
                    """, (crypto_id, cutoff_date))
                    
                    count = cur.fetchone()[0]
                    has_sufficient_data = count >= (days * 0.8)  # Allow for 80% coverage
                    
                    if has_sufficient_data:
                        print(f"   Pool ID {crypto_id} already has {count} historical records (sufficient)")
                    else:
                        print(f"   Pool ID {crypto_id} has {count} historical records (insufficient, fetching)")
                    
                    return has_sufficient_data
                
        except Exception as e:
            print(f"❌ Error checking existing data for crypto_id {crypto_id}: {e}")
            return False
    
    def store_historical_data(self, crypto_id: int, historical_data: List[Dict[str, Any]]) -> int:
        """Store historical OHLCV data in price_data table"""
        if not historical_data:
            print(f"   No historical data to store for crypto_id {crypto_id}")
            return 0
        
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                INSERT INTO price_data (
                    crypto_id, timestamp, price_usd, volume_24h, market_cap,
                    percent_change_1h, percent_change_24h, percent_change_7d
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (crypto_id, timestamp) DO UPDATE SET
                    price_usd = EXCLUDED.price_usd,
                    volume_24h = EXCLUDED.volume_24h,
                    market_cap = EXCLUDED.market_cap,
                    percent_change_1h = EXCLUDED.percent_change_1h,
                    percent_change_24h = EXCLUDED.percent_change_24h,
                    percent_change_7d = EXCLUDED.percent_change_7d,
                    created_at = CURRENT_TIMESTAMP
                """
                
                # Prepare data tuples
                data_tuples = []
                for data_point in historical_data:
                    data_tuple = (
                        crypto_id,
                        data_point['timestamp'],
                        data_point['price_usd'],
                        data_point.get('volume_24h'),
                        data_point.get('market_cap'),
                        data_point.get('percent_change_1h'),
                        data_point.get('percent_change_24h'),
                        data_point.get('percent_change_7d')
                    )
                    data_tuples.append(data_tuple)
                
                # Execute batch insert
                cur.executemany(insert_query, data_tuples)
                self.conn.commit()
                
                inserted_count = len(data_tuples)
                print(f"   ✅ Stored {inserted_count} historical records for crypto_id {crypto_id}")
                return inserted_count
                
        except Exception as e:
            print(f"   ❌ Error storing historical data for crypto_id {crypto_id}: {e}")
            self.conn.rollback()
            raise
    
    def log_backfill_progress(self, pool_symbol: str, status: str, records_processed: int = 0, error_message: str = None) -> None:
        """Log backfill progress for monitoring"""
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                INSERT INTO analysis_runs (
                    run_type, status, records_processed, error_message, 
                    started_at, completed_at, notes
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                
                current_time = datetime.now(timezone.utc)
                notes = f"Historical backfill for pool: {pool_symbol}"
                
                cur.execute(insert_query, (
                    'data_ingestion',
                    status,
                    records_processed,
                    error_message,
                    current_time,
                    current_time if status in ['completed', 'failed'] else None,
                    notes
                ))
                
                self.conn.commit()
                
        except Exception as e:
            print(f"   ⚠️ Warning: Could not log progress for {pool_symbol}: {e}")
            # Don't raise - logging failure shouldn't stop the backfill
    
    def get_backfill_summary(self) -> Dict[str, Any]:
        """Get summary of stored historical data"""
        try:
            with self.conn.cursor() as cur:
                # Get total records per pool
                cur.execute("""
                    SELECT 
                        c.symbol,
                        c.name,
                        COUNT(pd.id) as record_count,
                        MIN(pd.timestamp) as earliest_data,
                        MAX(pd.timestamp) as latest_data
                    FROM cryptocurrencies c
                    LEFT JOIN price_data pd ON c.id = pd.crypto_id
                    WHERE c.is_active = true
                    GROUP BY c.id, c.symbol, c.name
                    ORDER BY c.symbol
                """)
                
                results = cur.fetchall()
                
                summary = {
                    'pools': [],
                    'total_pools': len(results),
                    'total_records': 0
                }
                
                for row in results:
                    pool_info = {
                        'symbol': row[0],
                        'name': row[1],
                        'record_count': row[2],
                        'earliest_data': row[3],
                        'latest_data': row[4]
                    }
                    summary['pools'].append(pool_info)
                    summary['total_records'] += row[2]
                
                return summary
                
        except Exception as e:
            print(f"❌ Error getting backfill summary: {e}")
            raise