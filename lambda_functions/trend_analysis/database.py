import pg8000
import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Database client for trend analysis operations"""
    
    def __init__(self):
        """
        Initialize database connection using environment variables
        """
        self.conn = None
        self._load_config()
        self._connect()
    
    def _load_config(self):
        """Load database configuration from environment variables"""
        try:
            self.db_config = {
                'host': os.environ.get('DB_HOST'),
                'database': os.environ.get('DB_NAME'),
                'username': os.environ.get('DB_USERNAME'),
                'password': os.environ.get('DB_PASSWORD'),
                'port': int(os.environ.get('DB_PORT', 5432))
            }
            
            # Validate that all required fields are present
            required_fields = ['host', 'database', 'username', 'password']
            missing_fields = [field for field in required_fields if not self.db_config[field]]
            
            if missing_fields:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
            
            logger.info(f"Database config loaded: host={self.db_config['host']}, database={self.db_config['database']}, user={self.db_config['username']}")
            
        except Exception as e:
            logger.error(f"Error loading database config: {e}")
            raise
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = pg8000.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['username'],
                password=self.db_config['password'],
                port=self.db_config.get('port', 5432)
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def get_active_cryptocurrencies(self) -> List[Dict[str, Any]]:
        """
        Fetch all active cryptocurrencies from the database
        
        Returns:
            List of dictionaries containing cryptocurrency data
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                SELECT id, symbol, name, cmc_id, rank
                FROM cryptocurrencies 
                WHERE is_active = true
                ORDER BY rank ASC
                """
                cur.execute(query)
                cryptos = cur.fetchall()
                
                # Convert to list of dicts
                result = []
                for row in cryptos:
                    result.append({
                        'id': row[0],
                        'symbol': row[1],
                        'name': row[2],
                        'cmc_id': row[3],
                        'rank': row[4]
                    })
                logger.info(f"Retrieved {len(result)} active cryptocurrencies")
                return result
                
        except Exception as e:
            logger.error(f"Error fetching active cryptocurrencies: {str(e)}")
            raise
    
    def get_price_data_for_analysis(self, crypto_id: int, days: int = 30) -> List[Dict[str, Any]]:
        """
        Fetch price data for trend analysis
        
        Args:
            crypto_id: Internal cryptocurrency ID
            days: Number of days of data to fetch
            
        Returns:
            List of price data points sorted by timestamp
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                SELECT 
                    timestamp,
                    price_usd,
                    volume_24h,
                    market_cap,
                    percent_change_1h,
                    percent_change_24h,
                    percent_change_7d,
                    created_at
                FROM price_data 
                WHERE crypto_id = %s 
                  AND timestamp >= %s
                ORDER BY timestamp ASC
                """
                
                cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
                cur.execute(query, (crypto_id, cutoff_date))
                
                rows = cur.fetchall()
                result = []
                for row in rows:
                    result.append({
                        'timestamp': row[0],
                        'price_usd': row[1],
                        'volume_24h': row[2],
                        'market_cap': row[3],
                        'percent_change_1h': row[4],
                        'percent_change_24h': row[5],
                        'percent_change_7d': row[6],
                        'created_at': row[7]
                    })
                logger.info(f"Retrieved {len(result)} price data points for crypto {crypto_id}")
                return result
                
        except Exception as e:
            logger.error(f"Error fetching price data for crypto {crypto_id}: {str(e)}")
            raise
    
    def store_trend_analysis(self, trend_result: Dict[str, Any]) -> int:
        """
        Store trend analysis results in the database
        
        Args:
            trend_result: Dictionary containing trend analysis results
            
        Returns:
            ID of the stored trend analysis record
        """
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                INSERT INTO trend_analysis (
                    crypto_id, timeframe, trend_type, confidence,
                    start_time, end_time, price_change_percent, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (crypto_id, timeframe, start_time) DO UPDATE SET
                    trend_type = EXCLUDED.trend_type,
                    confidence = EXCLUDED.confidence,
                    end_time = EXCLUDED.end_time,
                    price_change_percent = EXCLUDED.price_change_percent,
                    metadata = EXCLUDED.metadata,
                    created_at = CURRENT_TIMESTAMP
                RETURNING id
                """
                
                cur.execute(insert_query, (
                    trend_result['crypto_id'],
                    trend_result['timeframe'],
                    trend_result['trend_type'],
                    trend_result['confidence'],
                    trend_result['start_time'],
                    trend_result['end_time'],
                    trend_result['price_change_percent'],
                    json.dumps(trend_result.get('metadata', {}))
                ))
                
                result_id = cur.fetchone()[0]
                self.conn.commit()
                
                logger.info(f"Stored trend analysis with ID {result_id}")
                return result_id
                
        except Exception as e:
            logger.error(f"Error storing trend analysis: {str(e)}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def store_signal_event(self, signal: Dict[str, Any]) -> int:
        """
        Store signal event in the database
        
        Args:
            signal: Dictionary containing signal event data
            
        Returns:
            ID of the stored signal event record
        """
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                INSERT INTO signal_events (
                    crypto_id, signal_type, detected_at, confidence,
                    trigger_price, volume_spike_ratio, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """
                
                cur.execute(insert_query, (
                    signal['crypto_id'],
                    signal['signal_type'],
                    signal['detected_at'],
                    signal['confidence'],
                    signal.get('trigger_price'),
                    signal.get('volume_spike_ratio'),
                    json.dumps(signal.get('metadata', {}))
                ))
                
                result_id = cur.fetchone()[0]
                self.conn.commit()
                
                logger.info(f"Stored signal event with ID {result_id}")
                return result_id
                
        except Exception as e:
            logger.error(f"Error storing signal event: {str(e)}")
            if self.conn:
                self.conn.rollback()
            raise
    
    def log_analysis_run(self, run_type: str, status: str = 'running', 
                        processed_count: int = 0, error_message: str = None) -> int:
        """
        Log an analysis run
        
        Args:
            run_type: Type of analysis run
            status: Status of the run
            processed_count: Number of items processed
            error_message: Error message if any
            
        Returns:
            ID of the created analysis run record
        """
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                INSERT INTO analysis_runs (run_type, status, records_processed, error_message)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """
                cur.execute(insert_query, (run_type, status, processed_count, error_message))
                run_id = cur.fetchone()[0]
                self.conn.commit()
                return run_id
                
        except Exception as e:
            logger.error(f"Error logging analysis run: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return 0
    
    def update_analysis_run(self, run_id: int, status: str, 
                           processed_count: int = None, error_message: str = None):
        """
        Update an analysis run record
        
        Args:
            run_id: ID of the analysis run
            status: New status
            processed_count: Number of items processed
            error_message: Error message if any
        """
        try:
            with self.conn.cursor() as cur:
                update_query = """
                UPDATE analysis_runs 
                SET status = %s, 
                    completed_at = CURRENT_TIMESTAMP,
                    records_processed = COALESCE(%s, records_processed),
                    error_message = COALESCE(%s, error_message)
                WHERE id = %s
                """
                cur.execute(update_query, (status, processed_count, error_message, run_id))
                self.conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating analysis run {run_id}: {str(e)}")
            if self.conn:
                self.conn.rollback()
    
    def get_latest_analysis_results(self, crypto_id: int = None, 
                                  timeframe: str = None) -> List[Dict[str, Any]]:
        """
        Get latest trend analysis results
        
        Args:
            crypto_id: Optional crypto ID filter
            timeframe: Optional timeframe filter
            
        Returns:
            List of latest trend analysis results
        """
        try:
            with self.conn.cursor() as cur:
                query = """
                SELECT 
                    ta.crypto_id,
                    c.symbol,
                    c.name,
                    ta.timeframe,
                    ta.trend_type,
                    ta.confidence,
                    ta.price_change_percent,
                    ta.start_time,
                    ta.end_time,
                    ta.metadata,
                    ta.created_at
                FROM trend_analysis ta
                JOIN cryptocurrencies c ON ta.crypto_id = c.id
                WHERE ta.created_at >= %s
                """
                
                params = [datetime.now(timezone.utc) - timedelta(hours=2)]
                
                if crypto_id:
                    query += " AND ta.crypto_id = %s"
                    params.append(crypto_id)
                
                if timeframe:
                    query += " AND ta.timeframe = %s"
                    params.append(timeframe)
                
                query += " ORDER BY ta.created_at DESC"
                
                cur.execute(query, params)
                rows = cur.fetchall()
                result = []
                for row in rows:
                    result.append({
                        'crypto_id': row[0],
                        'symbol': row[1],
                        'name': row[2],
                        'timeframe': row[3],
                        'trend_type': row[4],
                        'confidence': row[5],
                        'price_change_percent': row[6],
                        'start_time': row[7],
                        'end_time': row[8],
                        'metadata': row[9],
                        'created_at': row[10]
                    })
                return result
                
        except Exception as e:
            logger.error(f"Error fetching latest analysis results: {str(e)}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 