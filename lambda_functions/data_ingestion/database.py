import pg8000
import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self._load_config()
    
    def _load_config(self):
        """Load database configuration from environment variables"""
        try:
            db_config = {
                'host': os.environ.get('DB_HOST'),
                'database': os.environ.get('DB_NAME'),
                'username': os.environ.get('DB_USERNAME'),
                'password': os.environ.get('DB_PASSWORD'),
                'port': int(os.environ.get('DB_PORT', 5432))
            }
            
            # Validate that all required fields are present
            required_fields = ['host', 'database', 'username', 'password']
            missing_fields = [field for field in required_fields if not db_config[field]]
            
            if missing_fields:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
            
            self.db_config = db_config
            print(f"Database config loaded: host={db_config['host']}, database={db_config['database']}, user={db_config['username']}")
            
        except Exception as e:
            print(f"Error loading database config: {e}")
            raise
    
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = pg8000.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['username'],
                password=self.db_config['password'],
                port=self.db_config.get('port', 5432)
            )
            print("Database connection established successfully")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise
    
    def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def get_cryptocurrencies(self) -> List[Dict[str, Any]]:
        """Get all cryptocurrencies from the database"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name, symbol, cmc_id, coingecko_id, is_active
                    FROM cryptocurrencies 
                    WHERE is_active = true
                    ORDER BY name
                """)
                results = cur.fetchall()
                
                # Convert to list of dictionaries
                cryptocurrencies = []
                for row in results:
                    cryptocurrencies.append({
                        'id': row[0],
                        'name': row[1],
                        'symbol': row[2],
                        'cmc_id': row[3],
                        'coingecko_id': row[4],
                        'is_active': row[5]
                    })
                
                return cryptocurrencies
        except Exception as e:
            print(f"Error fetching cryptocurrencies: {e}")
            raise
    
    def insert_price_data(self, price_records: List[tuple]) -> int:
        """Insert price data records into the database"""
        if not price_records:
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
                
                cur.executemany(insert_query, price_records)
                self.conn.commit()
                
                inserted_count = len(price_records)
                print(f"Successfully inserted {inserted_count} price records")
                return inserted_count
                
        except Exception as e:
            print(f"Error inserting price data: {e}")
            self.conn.rollback()
            raise
    
    def log_ingestion_run(self, source: str, records_processed: int, 
                         success: bool, error_message: str = None) -> int:
        """Log the ingestion run details"""
        try:
            with self.conn.cursor() as cur:
                # Use the actual schema from migration 005_create_analysis_runs.sql
                insert_query = """
                INSERT INTO analysis_runs (
                    run_type, status, records_processed, error_message, completed_at
                ) VALUES (%s, %s, %s, %s, %s)
                RETURNING id
                """
                
                status = 'completed' if success else 'failed'
                
                cur.execute(insert_query, (
                    'data_ingestion',
                    status,
                    records_processed,
                    error_message,
                    datetime.now(timezone.utc)
                ))
                
                run_id = cur.fetchone()[0]
                self.conn.commit()
                
                print(f"Logged ingestion run with ID: {run_id}")
                return run_id
                
        except Exception as e:
            print(f"Error logging ingestion run: {e}")
            self.conn.rollback()
            raise
    
    def get_latest_price_data(self, crypto_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the latest price data for a specific cryptocurrency"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    SELECT timestamp, price_usd, volume_24h, market_cap,
                           percent_change_1h, percent_change_24h, percent_change_7d
                    FROM price_data 
                    WHERE crypto_id = %s
                    ORDER BY timestamp DESC
                    LIMIT %s
                """, (crypto_id, limit))
                
                results = cur.fetchall()
                
                # Convert to list of dictionaries
                price_data = []
                for row in results:
                    price_data.append({
                        'timestamp': row[0],
                        'price_usd': row[1],
                        'volume_24h': row[2],
                        'market_cap': row[3],
                        'percent_change_1h': row[4],
                        'percent_change_24h': row[5],
                        'percent_change_7d': row[6]
                    })
                
                return price_data
                
        except Exception as e:
            print(f"Error fetching latest price data: {e}")
            raise 