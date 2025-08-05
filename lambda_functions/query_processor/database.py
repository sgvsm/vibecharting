import psycopg
from psycopg.rows import dict_row
import psycopg.types.json
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class DatabaseClient:
    """Database client for query processor operations"""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize database connection
        
        Args:
            db_config: Dictionary containing database connection parameters
        """
        self.conn = None
        try:
            self.conn = psycopg.connect(
                host=db_config['host'],
                dbname=db_config['database'],
                user=db_config['username'],
                password=db_config['password'],
                port=db_config.get('port', 5432),
                connect_timeout=30
            )
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def get_results_for_intent(self, intent: Dict[str, Any], 
                              timeframe: str = '24h',
                              min_confidence: float = 0.7,
                              limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get results based on detected intent
        
        Args:
            intent: Detected intent from query parser
            timeframe: Time period to search
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
            
        Returns:
            List of matching results
        """
        try:
            intent_type = intent.get('type')
            cryptocurrencies = intent.get('cryptocurrencies', [])
            
            logger.info(f"Getting results for intent: {intent_type}")
            
            # Route to appropriate handler
            if intent_type == 'pump_and_dump':
                return self._get_pump_dump_signals(cryptocurrencies, timeframe, min_confidence, limit)
            elif intent_type == 'bottomed_out':
                return self._get_bottomed_out_signals(cryptocurrencies, timeframe, min_confidence, limit)
            elif intent_type in ['uptrend', 'downtrend']:
                return self._get_trend_analysis(intent_type, cryptocurrencies, timeframe, min_confidence, limit)
            elif intent_type == 'high_volatility':
                return self._get_high_volatility_analysis(cryptocurrencies, timeframe, limit)
            elif intent_type == 'volume_spike':
                return self._get_volume_anomalies(cryptocurrencies, timeframe, min_confidence, limit)
            elif intent_type == 'trending':
                return self._get_trending_analysis(timeframe, limit)
            elif intent_type == 'performance':
                return self._get_performance_analysis(cryptocurrencies, timeframe, limit)
            else:
                logger.warning(f"Unknown intent type: {intent_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting results for intent: {str(e)}")
            return []
    
    def _get_pump_dump_signals(self, cryptocurrencies: List[str], 
                              timeframe: str, min_confidence: float, limit: int) -> List[Dict[str, Any]]:
        """Get pump and dump signals"""
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                query = """
                SELECT 
                    se.id,
                    c.symbol,
                    c.name,
                    se.signal_type,
                    se.detected_at,
                    se.confidence,
                    se.trigger_price,
                    se.volume_spike_ratio,
                    se.metadata,
                    pd.price_usd as current_price
                FROM signal_events se
                JOIN cryptocurrencies c ON se.crypto_id = c.id
                LEFT JOIN LATERAL (
                    SELECT price_usd 
                    FROM price_data 
                    WHERE crypto_id = se.crypto_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) pd ON true
                WHERE se.signal_type = 'pump_and_dump'
                  AND se.confidence >= %s
                  AND se.detected_at >= %s
                """
                
                params = [min_confidence, self._get_timeframe_cutoff(timeframe)]
                
                if cryptocurrencies:
                    query += " AND c.symbol = ANY(%s)"
                    params.append(cryptocurrencies)
                
                query += " ORDER BY se.detected_at DESC, se.confidence DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'id': row['id'],
                        'cryptocurrency': {
                            'symbol': row['symbol'],
                            'name': row['name']
                        },
                        'signal_type': row['signal_type'],
                        'detected_at': row['detected_at'].isoformat(),
                        'confidence': float(row['confidence']),
                        'trigger_price': float(row['trigger_price']) if row['trigger_price'] else None,
                        'current_price': float(row['current_price']) if row['current_price'] else None,
                        'volume_spike_ratio': float(row['volume_spike_ratio']) if row['volume_spike_ratio'] else None,
                        'metadata': row['metadata'] or {}
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error getting pump dump signals: {str(e)}")
            return []
    
    def _get_bottomed_out_signals(self, cryptocurrencies: List[str],
                                 timeframe: str, min_confidence: float, limit: int) -> List[Dict[str, Any]]:
        """Get bottomed out signals"""
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                query = """
                SELECT 
                    se.id,
                    c.symbol,
                    c.name,
                    se.signal_type,
                    se.detected_at,
                    se.confidence,
                    se.trigger_price,
                    se.metadata,
                    pd.price_usd as current_price
                FROM signal_events se
                JOIN cryptocurrencies c ON se.crypto_id = c.id
                LEFT JOIN LATERAL (
                    SELECT price_usd 
                    FROM price_data 
                    WHERE crypto_id = se.crypto_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) pd ON true
                WHERE se.signal_type = 'bottomed_out'
                  AND se.confidence >= %s
                  AND se.detected_at >= %s
                """
                
                params = [min_confidence, self._get_timeframe_cutoff(timeframe)]
                
                if cryptocurrencies:
                    query += " AND c.symbol = ANY(%s)"
                    params.append(cryptocurrencies)
                
                query += " ORDER BY se.detected_at DESC, se.confidence DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results
                formatted_results = []
                for row in results:
                    metadata = row['metadata'] or {}
                    recovery_percent = metadata.get('recovery_percent', 0)
                    
                    formatted_results.append({
                        'id': row['id'],
                        'cryptocurrency': {
                            'symbol': row['symbol'],
                            'name': row['name']
                        },
                        'signal_type': row['signal_type'],
                        'detected_at': row['detected_at'].isoformat(),
                        'confidence': float(row['confidence']),
                        'trigger_price': float(row['trigger_price']) if row['trigger_price'] else None,
                        'current_price': float(row['current_price']) if row['current_price'] else None,
                        'recovery_percent': recovery_percent,
                        'metadata': metadata
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error getting bottomed out signals: {str(e)}")
            return []
    
    def _get_trend_analysis(self, trend_type: str, cryptocurrencies: List[str],
                           timeframe: str, min_confidence: float, limit: int) -> List[Dict[str, Any]]:
        """Get trend analysis results"""
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                query = """
                SELECT 
                    ta.id,
                    c.symbol,
                    c.name,
                    ta.trend_type,
                    ta.timeframe,
                    ta.confidence,
                    ta.price_change_percent,
                    ta.start_time,
                    ta.end_time,
                    ta.metadata,
                    ta.created_at,
                    pd.price_usd as current_price
                FROM trend_analysis ta
                JOIN cryptocurrencies c ON ta.crypto_id = c.id
                LEFT JOIN LATERAL (
                    SELECT price_usd 
                    FROM price_data 
                    WHERE crypto_id = ta.crypto_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) pd ON true
                WHERE ta.trend_type = %s
                  AND ta.confidence >= %s
                  AND ta.created_at >= %s
                  AND ta.timeframe = %s
                """
                
                params = [trend_type, min_confidence, self._get_timeframe_cutoff(timeframe), timeframe]
                
                if cryptocurrencies:
                    query += " AND c.symbol = ANY(%s)"
                    params.append(cryptocurrencies)
                
                query += " ORDER BY ta.created_at DESC, ta.confidence DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'id': row['id'],
                        'cryptocurrency': {
                            'symbol': row['symbol'],
                            'name': row['name']
                        },
                        'trend_type': row['trend_type'],
                        'timeframe': row['timeframe'],
                        'confidence': float(row['confidence']),
                        'price_change_percent': float(row['price_change_percent']),
                        'current_price': float(row['current_price']) if row['current_price'] else None,
                        'analysis_period': {
                            'start_time': row['start_time'].isoformat(),
                            'end_time': row['end_time'].isoformat()
                        },
                        'detected_at': row['created_at'].isoformat(),
                        'metadata': row['metadata'] or {}
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error getting trend analysis: {str(e)}")
            return []
    
    def _get_high_volatility_analysis(self, cryptocurrencies: List[str],
                                    timeframe: str, limit: int) -> List[Dict[str, Any]]:
        """Get high volatility analysis"""
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                # Calculate volatility from recent price data
                query = """
                WITH price_stats AS (
                    SELECT 
                        pd.crypto_id,
                        c.symbol,
                        c.name,
                        STDDEV(pd.price_usd) / AVG(pd.price_usd) * 100 as volatility,
                        AVG(pd.price_usd) as avg_price,
                        MAX(pd.price_usd) as max_price,
                        MIN(pd.price_usd) as min_price,
                        COUNT(*) as data_points
                    FROM price_data pd
                    JOIN cryptocurrencies c ON pd.crypto_id = c.id
                    WHERE pd.timestamp >= %s
                      AND c.is_active = true
                """
                
                params = [self._get_timeframe_cutoff(timeframe)]
                
                if cryptocurrencies:
                    query += " AND c.symbol = ANY(%s)"
                    params.append(cryptocurrencies)
                
                query += """
                    GROUP BY pd.crypto_id, c.symbol, c.name
                    HAVING COUNT(*) >= 5
                )
                SELECT 
                    ps.*,
                    pd.price_usd as current_price
                FROM price_stats ps
                LEFT JOIN LATERAL (
                    SELECT price_usd 
                    FROM price_data 
                    WHERE crypto_id = ps.crypto_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) pd ON true
                WHERE ps.volatility > 5  -- Minimum 5% volatility
                ORDER BY ps.volatility DESC
                LIMIT %s
                """
                params.append(limit)
                
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'cryptocurrency': {
                            'symbol': row['symbol'],
                            'name': row['name']
                        },
                        'volatility_percent': round(float(row['volatility']), 2),
                        'price_range': {
                            'min': float(row['min_price']),
                            'max': float(row['max_price']),
                            'avg': round(float(row['avg_price']), 8)
                        },
                        'current_price': float(row['current_price']) if row['current_price'] else None,
                        'data_points': row['data_points'],
                        'timeframe': timeframe
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error getting volatility analysis: {str(e)}")
            return []
    
    def _get_volume_anomalies(self, cryptocurrencies: List[str],
                             timeframe: str, min_confidence: float, limit: int) -> List[Dict[str, Any]]:
        """Get volume anomaly signals"""
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                query = """
                SELECT 
                    se.id,
                    c.symbol,
                    c.name,
                    se.signal_type,
                    se.detected_at,
                    se.confidence,
                    se.trigger_price,
                    se.volume_spike_ratio,
                    se.metadata,
                    pd.price_usd as current_price
                FROM signal_events se
                JOIN cryptocurrencies c ON se.crypto_id = c.id
                LEFT JOIN LATERAL (
                    SELECT price_usd 
                    FROM price_data 
                    WHERE crypto_id = se.crypto_id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) pd ON true
                WHERE se.signal_type = 'volume_anomaly'
                  AND se.confidence >= %s
                  AND se.detected_at >= %s
                """
                
                params = [min_confidence, self._get_timeframe_cutoff(timeframe)]
                
                if cryptocurrencies:
                    query += " AND c.symbol = ANY(%s)"
                    params.append(cryptocurrencies)
                
                query += " ORDER BY se.detected_at DESC, se.volume_spike_ratio DESC LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'id': row['id'],
                        'cryptocurrency': {
                            'symbol': row['symbol'],
                            'name': row['name']
                        },
                        'signal_type': row['signal_type'],
                        'detected_at': row['detected_at'].isoformat(),
                        'confidence': float(row['confidence']),
                        'trigger_price': float(row['trigger_price']) if row['trigger_price'] else None,
                        'current_price': float(row['current_price']) if row['current_price'] else None,
                        'volume_spike_ratio': float(row['volume_spike_ratio']) if row['volume_spike_ratio'] else None,
                        'metadata': row['metadata'] or {}
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error getting volume anomalies: {str(e)}")
            return []
    
    def _get_trending_analysis(self, timeframe: str, limit: int) -> List[Dict[str, Any]]:
        """Get trending cryptocurrencies based on recent activity"""
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                # Get trending based on recent signals and trends
                query = """
                WITH trending_scores AS (
                    SELECT 
                        c.id,
                        c.symbol,
                        c.name,
                        COALESCE(signal_count, 0) + COALESCE(trend_count, 0) as activity_score,
                        COALESCE(signal_count, 0) as recent_signals,
                        COALESCE(trend_count, 0) as recent_trends
                    FROM cryptocurrencies c
                    LEFT JOIN (
                        SELECT 
                            crypto_id,
                            COUNT(*) as signal_count
                        FROM signal_events 
                        WHERE detected_at >= %s
                        GROUP BY crypto_id
                    ) signals ON c.id = signals.crypto_id
                    LEFT JOIN (
                        SELECT 
                            crypto_id,
                            COUNT(*) as trend_count
                        FROM trend_analysis 
                        WHERE created_at >= %s
                        GROUP BY crypto_id
                    ) trends ON c.id = trends.crypto_id
                    WHERE c.is_active = true
                      AND (COALESCE(signal_count, 0) + COALESCE(trend_count, 0)) > 0
                )
                SELECT 
                    ts.*,
                    pd.price_usd as current_price,
                    pd.percent_change_24h
                FROM trending_scores ts
                LEFT JOIN LATERAL (
                    SELECT price_usd, percent_change_24h
                    FROM price_data 
                    WHERE crypto_id = ts.id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) pd ON true
                ORDER BY ts.activity_score DESC, ts.recent_signals DESC
                LIMIT %s
                """
                
                cutoff_time = self._get_timeframe_cutoff(timeframe)
                params = [cutoff_time, cutoff_time, limit]
                
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'cryptocurrency': {
                            'symbol': row['symbol'],
                            'name': row['name']
                        },
                        'activity_score': row['activity_score'],
                        'recent_signals': row['recent_signals'],
                        'recent_trends': row['recent_trends'],
                        'current_price': float(row['current_price']) if row['current_price'] else None,
                        'price_change_24h': float(row['percent_change_24h']) if row['percent_change_24h'] else None,
                        'timeframe': timeframe
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error getting trending analysis: {str(e)}")
            return []
    
    def _get_performance_analysis(self, cryptocurrencies: List[str],
                                timeframe: str, limit: int) -> List[Dict[str, Any]]:
        """Get performance analysis (best/worst performers)"""
        try:
            with self.conn.cursor(row_factory=dict_row) as cur:
                # Get performance based on price changes
                query = """
                SELECT 
                    c.symbol,
                    c.name,
                    pd.price_usd as current_price,
                    pd.percent_change_1h,
                    pd.percent_change_24h,
                    pd.percent_change_7d,
                    pd.volume_24h,
                    pd.market_cap
                FROM cryptocurrencies c
                LEFT JOIN LATERAL (
                    SELECT 
                        price_usd, 
                        percent_change_1h,
                        percent_change_24h,
                        percent_change_7d,
                        volume_24h,
                        market_cap
                    FROM price_data 
                    WHERE crypto_id = c.id 
                    ORDER BY timestamp DESC 
                    LIMIT 1
                ) pd ON true
                WHERE c.is_active = true
                  AND pd.price_usd IS NOT NULL
                """
                
                params = []
                
                if cryptocurrencies:
                    query += " AND c.symbol = ANY(%s)"
                    params.append(cryptocurrencies)
                
                # Order based on timeframe
                if timeframe == '1h':
                    query += " ORDER BY pd.percent_change_1h DESC NULLS LAST"
                elif timeframe == '7d':
                    query += " ORDER BY pd.percent_change_7d DESC NULLS LAST"
                else:  # Default to 24h
                    query += " ORDER BY pd.percent_change_24h DESC NULLS LAST"
                
                query += " LIMIT %s"
                params.append(limit)
                
                cur.execute(query, params)
                results = [dict(row) for row in cur.fetchall()]
                
                # Format results
                formatted_results = []
                for row in results:
                    formatted_results.append({
                        'cryptocurrency': {
                            'symbol': row['symbol'],
                            'name': row['name']
                        },
                        'current_price': float(row['current_price']) if row['current_price'] else None,
                        'performance': {
                            'change_1h': float(row['percent_change_1h']) if row['percent_change_1h'] else None,
                            'change_24h': float(row['percent_change_24h']) if row['percent_change_24h'] else None,
                            'change_7d': float(row['percent_change_7d']) if row['percent_change_7d'] else None
                        },
                        'volume_24h': float(row['volume_24h']) if row['volume_24h'] else None,
                        'market_cap': float(row['market_cap']) if row['market_cap'] else None,
                        'timeframe': timeframe
                    })
                
                return formatted_results
                
        except Exception as e:
            logger.error(f"Error getting performance analysis: {str(e)}")
            return []
    
    def _get_timeframe_cutoff(self, timeframe: str) -> datetime:
        """Get cutoff datetime for timeframe"""
        now = datetime.now(timezone.utc)
        
        if timeframe == '1h':
            return now - timedelta(hours=1)
        elif timeframe == '24h':
            return now - timedelta(hours=24)
        elif timeframe == '7d':
            return now - timedelta(days=7)
        elif timeframe == '30d':
            return now - timedelta(days=30)
        else:
            return now - timedelta(hours=24)  # Default
    
    def log_query(self, query_text: str, intent: Dict[str, Any], 
                 result_count: int, execution_time_ms: int):
        """
        Log query for analytics
        
        Args:
            query_text: Original query text
            intent: Detected intent
            result_count: Number of results returned
            execution_time_ms: Execution time in milliseconds
        """
        try:
            with self.conn.cursor() as cur:
                insert_query = """
                INSERT INTO query_logs (
                    query_text, intent_type, intent_confidence, 
                    result_count, execution_time_ms, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s)
                """
                
                cur.execute(insert_query, (
                    query_text,
                    intent.get('type'),
                    intent.get('confidence'),
                    result_count,
                    execution_time_ms,
                    psycopg.types.json.Json(intent)
                ))
                
                self.conn.commit()
                
        except Exception as e:
            logger.error(f"Error logging query: {str(e)}")
            # Don't fail the main request if logging fails
            pass
    
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