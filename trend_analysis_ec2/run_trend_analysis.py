#!/usr/bin/env python3
"""
Direct EC2 Trend Analysis Runner
This script runs the trend analysis directly on EC2 for testing
"""

import os
import sys
import logging
import json
import pg8000
from datetime import datetime, timezone, timedelta
import numpy as np
from scipy import stats

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f'trend_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseClient:
    """Simple database client for EC2 testing"""
    
    def __init__(self):
        self.conn = None
        self._connect()
    
    def _connect(self):
        """Establish database connection using environment variables"""
        try:
            self.conn = pg8000.connect(
                host=os.environ.get('DB_HOST'),
                database=os.environ.get('DB_NAME'),
                user=os.environ.get('DB_USERNAME'),
                password=os.environ.get('DB_PASSWORD'),
                port=int(os.environ.get('DB_PORT', 5432))
            )
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            raise
    
    def get_active_cryptocurrencies(self):
        """Get all active cryptocurrencies"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, symbol, name, cmc_id, rank
                FROM cryptocurrencies 
                WHERE is_active = true
                ORDER BY rank ASC
            """)
            rows = cur.fetchall()
            return [
                {'id': row[0], 'symbol': row[1], 'name': row[2], 
                 'cmc_id': row[3], 'rank': row[4]}
                for row in rows
            ]
    
    def get_price_data(self, crypto_id, days=30):
        """Get price data for analysis"""
        with self.conn.cursor() as cur:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            cur.execute("""
                SELECT timestamp, price_usd, volume_24h
                FROM price_data 
                WHERE crypto_id = %s AND timestamp >= %s
                ORDER BY timestamp ASC
            """, (crypto_id, cutoff_date))
            
            rows = cur.fetchall()
            return [
                {'timestamp': row[0], 'price_usd': float(row[1]), 'volume_24h': float(row[2])}
                for row in rows
            ]
    
    def store_trend_analysis(self, result):
        """Store trend analysis result"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO trend_analysis (
                    crypto_id, timeframe, trend_type, confidence,
                    start_time, end_time, price_change_percent, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (crypto_id, timeframe, start_time) DO UPDATE SET
                    trend_type = EXCLUDED.trend_type,
                    confidence = EXCLUDED.confidence,
                    end_time = EXCLUDED.end_time,
                    price_change_percent = EXCLUDED.price_change_percent,
                    metadata = EXCLUDED.metadata
            """, (
                result['crypto_id'], result['timeframe'], result['trend_type'],
                result['confidence'], result['start_time'], result['end_time'],
                result['price_change_percent'], json.dumps(result.get('metadata', {}))
            ))
            self.conn.commit()
    
    def store_signal_event(self, signal):
        """Store signal event"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO signal_events (
                    crypto_id, signal_type, detected_at, confidence,
                    trigger_price, volume_spike_ratio, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                signal['crypto_id'], signal['signal_type'], signal['detected_at'],
                signal['confidence'], signal.get('trigger_price'),
                signal.get('volume_spike_ratio'), json.dumps(signal.get('metadata', {}))
            ))
            self.conn.commit()
    
    def close(self):
        if self.conn:
            self.conn.close()

def analyze_trend(price_data, timeframe, crypto_id):
    """Improved trend analysis with better thresholds"""
    if timeframe == '24h':
        hours = 24
    elif timeframe == '7d':
        hours = 168
    else:
        hours = 24
    
    # Filter data
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    filtered_data = [p for p in price_data if p['timestamp'] >= cutoff]
    
    if len(filtered_data) < 3:
        return None
    
    # Extract prices and calculate trend
    prices = [p['price_usd'] for p in filtered_data]
    timestamps = [p['timestamp'] for p in filtered_data]
    
    # Linear regression
    x = range(len(prices))
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, prices)
    
    # Calculate metrics
    price_change_percent = ((prices[-1] - prices[0]) / prices[0]) * 100
    volatility = np.std(prices) / np.mean(prices) * 100
    r_squared = r_value ** 2
    
    # Improved trend classification
    if abs(price_change_percent) < 1.0:  # More conservative sideways threshold
        trend_type = 'sideways'
    elif price_change_percent > 5.0:  # Higher threshold for uptrend
        trend_type = 'uptrend'
    elif price_change_percent < -5.0:  # Higher threshold for downtrend
        trend_type = 'downtrend'
    else:
        trend_type = 'sideways'
    
    # Confidence based on R-squared and data points
    confidence = min(r_squared * (len(filtered_data) / 10), 1.0)
    
    return {
        'crypto_id': crypto_id,
        'timeframe': timeframe,
        'trend_type': trend_type,
        'confidence': confidence,
        'start_time': timestamps[0],
        'end_time': timestamps[-1],
        'price_change_percent': price_change_percent,
        'metadata': {
            'slope': float(slope),
            'r_squared': float(r_squared),
            'volatility': float(volatility),
            'data_points': len(filtered_data)
        }
    }

def detect_signals(price_data, crypto_id):
    """Improved signal detection with multiple types and better thresholds"""
    signals = []
    
    if len(price_data) < 14:  # Need at least 2 weeks of data
        return signals
    
    # Sort by timestamp (oldest first for analysis)
    sorted_data = sorted(price_data, key=lambda x: x['timestamp'])
    prices = [p['price_usd'] for p in sorted_data]
    volumes = [p['volume_24h'] for p in sorted_data]
    timestamps = [p['timestamp'] for p in sorted_data]
    
    # 1. PUMP AND DUMP DETECTION (More conservative)
    if len(prices) >= 24:
        # Look for pump in last 12 hours, dump in next 12 hours
        recent_prices = prices[-24:]
        pump_window = recent_prices[:12]
        dump_window = recent_prices[12:]
        
        if len(pump_window) >= 6 and len(dump_window) >= 6:
            pump_start = min(pump_window)
            pump_peak = max(pump_window)
            dump_end = min(dump_window)
            
            pump_percent = ((pump_peak - pump_start) / pump_start) * 100
            dump_percent = ((dump_end - pump_peak) / pump_peak) * 100
            
            # More conservative thresholds
            if pump_percent > 30 and dump_percent < -20:  # Higher pump threshold
                signals.append({
                    'crypto_id': crypto_id,
                    'signal_type': 'pump_and_dump',
                    'detected_at': datetime.now(timezone.utc),
                    'confidence': min((pump_percent + abs(dump_percent)) / 100, 1.0),
                    'trigger_price': pump_peak,
                    'metadata': {
                        'pump_percent': pump_percent,
                        'dump_percent': dump_percent,
                        'pump_start_price': pump_start,
                        'pump_peak_price': pump_peak,
                        'dump_end_price': dump_end
                    }
                })
    
    # 2. VOLUME ANOMALY DETECTION
    if len(volumes) >= 7:
        # Calculate rolling average volume
        recent_volumes = volumes[-7:]
        avg_volume = np.mean(recent_volumes[:-1])
        latest_volume = recent_volumes[-1]
        
        if avg_volume > 0 and latest_volume > avg_volume * 5:  # Higher threshold
            signals.append({
                'crypto_id': crypto_id,
                'signal_type': 'volume_anomaly',
                'detected_at': datetime.now(timezone.utc),
                'confidence': min(latest_volume / (avg_volume * 10), 1.0),
                'volume_spike_ratio': latest_volume / avg_volume,
                'metadata': {
                    'avg_volume': avg_volume,
                    'spike_volume': latest_volume,
                    'volume_increase_percent': ((latest_volume - avg_volume) / avg_volume) * 100
                }
            })
    
    # 3. BOTTOMED OUT DETECTION
    if len(prices) >= 14:
        # Check for 7+ days of downtrend followed by recovery
        week_ago_prices = prices[-14:-7]
        recent_prices = prices[-7:]
        
        if len(week_ago_prices) >= 5 and len(recent_prices) >= 5:
            week_trend = (week_ago_prices[-1] - week_ago_prices[0]) / week_ago_prices[0] * 100
            recent_trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            
            # Downtrend for a week followed by recovery
            if week_trend < -10 and recent_trend > 8:
                signals.append({
                    'crypto_id': crypto_id,
                    'signal_type': 'bottomed_out',
                    'detected_at': datetime.now(timezone.utc),
                    'confidence': min((abs(week_trend) + recent_trend) / 50, 1.0),
                    'trigger_price': recent_prices[-1],
                    'metadata': {
                        'downtrend_percent': week_trend,
                        'recovery_percent': recent_trend,
                        'lowest_price': min(week_ago_prices + recent_prices)
                    }
                })
    
    # 4. PARABOLIC RISE DETECTION
    if len(prices) >= 10:
        # Check for exponential growth pattern
        recent_prices = prices[-10:]
        price_changes = []
        
        for i in range(1, len(recent_prices)):
            change = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1] * 100
            price_changes.append(change)
        
        # Check if changes are accelerating (parabolic)
        if len(price_changes) >= 5:
            # Calculate if changes are increasing
            increasing_changes = sum(1 for i in range(1, len(price_changes)) 
                                if price_changes[i] > price_changes[i-1])
            
            total_rise = sum(price_changes)
            if increasing_changes >= 3 and total_rise > 50:  # Parabolic pattern
                signals.append({
                    'crypto_id': crypto_id,
                    'signal_type': 'parabolic_rise',
                    'detected_at': datetime.now(timezone.utc),
                    'confidence': min(total_rise / 100, 1.0),
                    'trigger_price': recent_prices[-1],
                    'metadata': {
                        'total_rise_percent': total_rise,
                        'increasing_changes': increasing_changes,
                        'avg_daily_change': np.mean(price_changes)
                    }
                })
    
    # 5. CAPITULATION DROP DETECTION
    if len(prices) >= 14:
        # Check for sharp drop after prolonged downtrend
        week_ago_prices = prices[-14:-7]
        recent_prices = prices[-7:]
        
        if len(week_ago_prices) >= 5 and len(recent_prices) >= 5:
            week_trend = (week_ago_prices[-1] - week_ago_prices[0]) / week_ago_prices[0] * 100
            recent_drop = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
            
            # Prolonged downtrend followed by sharp drop
            if week_trend < -15 and recent_drop < -25:
                signals.append({
                    'crypto_id': crypto_id,
                    'signal_type': 'capitulation_drop',
                    'detected_at': datetime.now(timezone.utc),
                    'confidence': min((abs(week_trend) + abs(recent_drop)) / 100, 1.0),
                    'trigger_price': recent_prices[-1],
                    'metadata': {
                        'downtrend_percent': week_trend,
                        'drop_percent': recent_drop,
                        'total_decline': week_trend + recent_drop
                    }
                })
    
    return signals

def run_analysis():
    """Run trend analysis on all cryptocurrencies"""
    print("="*80)
    print("IMPROVED TREND ANALYSIS EC2 TEST RUNNER")
    print("="*80)
    print(f"Start Time: {datetime.now(timezone.utc)}")
    
    # Check environment variables
    required_vars = ['DB_HOST', 'DB_NAME', 'DB_USERNAME', 'DB_PASSWORD']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables: {', '.join(missing_vars)}")
        return 1
    
    start_time = datetime.now(timezone.utc)
    
    try:
        # Initialize database
        db = DatabaseClient()
        
        # Get active cryptocurrencies
        cryptos = db.get_active_cryptocurrencies()
        print(f"\nFound {len(cryptos)} active cryptocurrencies")
        
        total_trends = 0
        total_signals = 0
        processed = 0
        signal_types = {}
        
        # Process each cryptocurrency
        for crypto in cryptos:
            try:
                crypto_id = crypto['id']
                symbol = crypto['symbol']
                
                print(f"\nAnalyzing {symbol}...", end='', flush=True)
                
                # Get price data
                price_data = db.get_price_data(crypto_id)
                
                if len(price_data) < 14:
                    print(" [SKIP: Insufficient data]")
                    continue
                
                # Analyze trends
                trends_found = 0
                for timeframe in ['24h', '7d']:
                    trend = analyze_trend(price_data, timeframe, crypto_id)
                    if trend:
                        db.store_trend_analysis(trend)
                        trends_found += 1
                        total_trends += 1
                
                # Detect signals
                signals = detect_signals(price_data, crypto_id)
                for signal in signals:
                    db.store_signal_event(signal)
                    total_signals += 1
                    signal_type = signal['signal_type']
                    signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
                
                processed += 1
                print(f" [OK: {trends_found} trends, {len(signals)} signals]")
                
            except Exception as e:
                print(f" [ERROR: {str(e)}]")
                logger.error(f"Error processing {symbol}: {str(e)}", exc_info=True)
        
        # Close database
        db.close()
        
        # Calculate duration
        duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"Processed: {processed} cryptocurrencies")
        print(f"Trends stored: {total_trends}")
        print(f"Signals detected: {total_signals}")
        print(f"Duration: {duration:.2f} seconds")
        
        if signal_types:
            print(f"\nSignal breakdown:")
            for signal_type, count in signal_types.items():
                print(f"  {signal_type}: {count}")
        
        print("="*80)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        logger.error("Analysis failed", exc_info=True)
        return 1

if __name__ == "__main__":
    exit_code = run_analysis()
    sys.exit(exit_code)