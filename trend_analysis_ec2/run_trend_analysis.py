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
import pandas as pd

# Import new modules for advanced technical analysis
try:
    from technical_indicators import TechnicalIndicators
    from confidence_model import ConfidenceModel
    from adaptive_thresholds import AdaptiveThresholds
    ADVANCED_ANALYSIS_AVAILABLE = True
except ImportError:
    ADVANCED_ANALYSIS_AVAILABLE = False
    logging.warning("Advanced analysis modules not available. Using legacy analysis.")

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
    """Improved trend analysis with better timeframes for 30-day data"""
    if timeframe == '7d':
        days = 7
    elif timeframe == '14d':
        days = 14
    elif timeframe == '30d':
        days = 30
    else:
        days = 7
    
    # Filter data for the specified timeframe
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
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
    
    # Improved trend classification with better thresholds
    if abs(price_change_percent) < 1.0:
        trend_type = 'sideways'
    elif price_change_percent > 5.0:
        trend_type = 'uptrend'
    elif price_change_percent < -5.0:
        trend_type = 'downtrend'
    else:
        trend_type = 'sideways'
    
    # Enhanced confidence calculation for 30-day data
    base_confidence = r_squared
    
    # Boost confidence for longer timeframes (more data)
    timeframe_boost = {
        '7d': 0.1,
        '14d': 0.2,
        '30d': 0.3
    }.get(timeframe, 0.0)
    
    # Adjust for statistical significance
    if p_value < 0.05:
        significance_boost = 0.2
    elif p_value < 0.1:
        significance_boost = 0.1
    else:
        significance_boost = 0.0
    
    # Adjust for volatility
    volatility_penalty = min(volatility / 100, 0.3)
    
    # Calculate final confidence with data quality bonus
    confidence = min(base_confidence + timeframe_boost + significance_boost - volatility_penalty, 1.0)
    confidence = max(confidence, 0.0)
    
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
            'data_points': len(filtered_data),
            'data_coverage_days': days,
            'start_price': round(prices[0], 8),
            'end_price': round(prices[-1], 8)
        }
    }

def detect_signals_sliding_window(price_data, crypto_id):
    """Detect signals using sliding window analysis for better 30-day utilization"""
    signals = []
    
    if len(price_data) < 14:
        return signals
    
    # Sort data by timestamp (oldest first)
    sorted_data = sorted(price_data, key=lambda x: x['timestamp'])
    prices = [p['price_usd'] for p in sorted_data]
    volumes = [p['volume_24h'] for p in sorted_data]
    
    # Sliding window analysis - check multiple time windows
    window_sizes = [7, 14, 21]  # Different window sizes to catch various patterns
    
    for window_size in window_sizes:
        if len(sorted_data) >= window_size:
            # Analyze each window
            for start_idx in range(0, len(sorted_data) - window_size + 1, 3):  # Step by 3 days
                window_data = sorted_data[start_idx:start_idx + window_size]
                
                # Detect signals in this window
                window_signals = detect_signals_in_window(window_data, crypto_id, start_idx)
                signals.extend(window_signals)
    
    # Remove duplicate signals (same type, similar time)
    unique_signals = []
    for signal in signals:
        is_duplicate = False
        for existing in unique_signals:
            if (signal['signal_type'] == existing['signal_type'] and
                abs((signal['detected_at'] - existing['detected_at']).days) < 3):  # Increased to 3 days
                is_duplicate = True
                break
        if not is_duplicate:
            unique_signals.append(signal)
    
    # Additional filtering: limit signals per crypto per week
    filtered_signals = []
    signal_counts = {}
    
    for signal in unique_signals:
        signal_key = f"{signal['crypto_id']}_{signal['signal_type']}"
        week_start = signal['detected_at'] - timedelta(days=signal['detected_at'].weekday())
        
        if signal_key not in signal_counts:
            signal_counts[signal_key] = {}
        
        if week_start not in signal_counts[signal_key]:
            signal_counts[signal_key][week_start] = 0
        
        # Limit to 2 signals per type per week
        if signal_counts[signal_key][week_start] < 2:
            signal_counts[signal_key][week_start] += 1
            filtered_signals.append(signal)
    
    return filtered_signals

def validate_signal_quality(signal):
    """Validate signal meets quality standards"""
    if signal['signal_type'] == 'pump_and_dump':
        # Must have significant price movement
        pump_percent = signal.get('metadata', {}).get('pump_percent', 0)
        dump_percent = signal.get('metadata', {}).get('dump_percent', 0)
        volume_spike = signal.get('volume_spike_ratio', 0)
        
        if pump_percent < 50 or dump_percent > -30 or volume_spike < 3.0:
            return False
    
    elif signal['signal_type'] == 'volume_anomaly':
        # Must have significant volume spike
        if signal.get('volume_spike_ratio', 0) < 5.0:
            return False
    
    elif signal['signal_type'] == 'bottomed_out':
        # Must have significant downtrend and recovery
        downtrend = signal.get('metadata', {}).get('downtrend_percent', 0)
        recovery = signal.get('metadata', {}).get('recovery_percent', 0)
        
        if downtrend > -15 or recovery < 10:
            return False
    
    return True

def analyze_trend_advanced(price_data, timeframe, crypto_id):
    """
    Advanced trend analysis using moving averages and technical indicators
    """
    if not ADVANCED_ANALYSIS_AVAILABLE:
        return analyze_trend(price_data, timeframe, crypto_id)
    
    # Prepare data
    df = TechnicalIndicators.prepare_dataframe(price_data)
    
    if len(df) < 50:  # Need sufficient data for indicators
        return None
    
    # Calculate indicators
    sma_50 = TechnicalIndicators.calculate_sma(df, period=50)
    ema_20 = TechnicalIndicators.calculate_ema(df, period=20)
    adx = TechnicalIndicators.calculate_adx(df)
    atr = TechnicalIndicators.calculate_atr(df)
    
    # Get timeframe-specific data
    if timeframe == '7d':
        days = 7
    elif timeframe == '14d':
        days = 14
    elif timeframe == '30d':
        days = 30
    else:
        days = 7
    
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Filter data for timeframe
    mask = df.index >= cutoff
    filtered_df = df[mask]
    
    if len(filtered_df) < 3:
        return None
    
    # Determine trend based on MA and price position
    current_price = filtered_df['close'].iloc[-1]
    
    # Get MA values for the timeframe
    sma_current = sma_50[mask].iloc[-1] if len(sma_50[mask]) > 0 else None
    ema_current = ema_20[mask].iloc[-1] if len(ema_20[mask]) > 0 else None
    
    # Calculate price change
    price_change_percent = ((filtered_df['close'].iloc[-1] - filtered_df['close'].iloc[0]) / 
                           filtered_df['close'].iloc[0]) * 100
    
    # Determine trend type using MAs
    if sma_current is not None and ema_current is not None:
        if current_price > sma_current and ema_current > sma_current:
            trend_type = 'uptrend'
        elif current_price < sma_current and ema_current < sma_current:
            trend_type = 'downtrend'
        else:
            trend_type = 'sideways'
    else:
        # Fallback to price change if MAs not available
        if abs(price_change_percent) < 3.0:
            trend_type = 'sideways'
        elif price_change_percent > 5.0:
            trend_type = 'uptrend'
        else:
            trend_type = 'downtrend'
    
    # Calculate trend strength using ADX
    adx_current = adx[mask].iloc[-1] if adx is not None and len(adx[mask]) > 0 else None
    
    # Calculate confidence using new model
    confidence_scores = ConfidenceModel.calculate_confidence(
        adx_value=adx_current,
        signal_type=trend_type
    )
    
    # Prepare metadata
    metadata = {
        'price_change_percent': float(price_change_percent),
        'sma_50': float(sma_current) if sma_current is not None else None,
        'ema_20': float(ema_current) if ema_current is not None else None,
        'adx': float(adx_current) if adx_current is not None else None,
        'atr': float(atr[mask].iloc[-1]) if atr is not None and len(atr[mask]) > 0 else None,
        'data_points': len(filtered_df),
        'start_price': float(filtered_df['close'].iloc[0]),
        'end_price': float(filtered_df['close'].iloc[-1]),
        'confidence_components': confidence_scores,
        'analysis_mode': 'advanced'
    }
    
    return {
        'crypto_id': crypto_id,
        'timeframe': timeframe,
        'trend_type': trend_type,
        'confidence': confidence_scores['overall_confidence'],
        'start_time': filtered_df.index[0].to_pydatetime().replace(tzinfo=timezone.utc),
        'end_time': filtered_df.index[-1].to_pydatetime().replace(tzinfo=timezone.utc),
        'price_change_percent': price_change_percent,
        'metadata': metadata
    }

def detect_signals_advanced(price_data, crypto_id):
    """
    Detect signals using advanced technical indicators
    """
    if not ADVANCED_ANALYSIS_AVAILABLE:
        return detect_signals_sliding_window(price_data, crypto_id)
    
    signals = []
    
    # Prepare data
    df = TechnicalIndicators.prepare_dataframe(price_data)
    
    if len(df) < 50:
        return signals
    
    # Calculate all indicators
    macd_df = TechnicalIndicators.calculate_macd(df)
    bb_df = TechnicalIndicators.calculate_bollinger_bands(df)
    rsi = TechnicalIndicators.calculate_rsi(df)
    sma_50 = TechnicalIndicators.calculate_sma(df, period=50)
    sma_200 = TechnicalIndicators.calculate_sma(df, period=200)
    atr = TechnicalIndicators.calculate_atr(df)
    adx = TechnicalIndicators.calculate_adx(df)
    
    # Get current values for confidence calculation
    current_adx = adx.iloc[-1] if adx is not None and len(adx) > 0 else None
    
    # 1. MACD Signals
    if macd_df is not None:
        macd_signals = TechnicalIndicators.detect_macd_signals(macd_df)
        
        # Get histogram values for percentile calculation
        histogram_col = [col for col in macd_df.columns if 'MACDh_' in col][0]
        histogram_values = macd_df[histogram_col].dropna().tolist()
        
        for signal_type, signal_list in macd_signals.items():
            for timestamp, histogram_value in signal_list[-3:]:  # Limit to last 3 signals per type
                # Calculate confidence
                histogram_percentile = ConfidenceModel.calculate_histogram_percentile(
                    histogram_value, histogram_values
                )
                
                confidence_scores = ConfidenceModel.calculate_confidence(
                    adx_value=current_adx,
                    macd_histogram_percentile=histogram_percentile,
                    signal_type=f'macd_{signal_type}'
                )
                
                signals.append({
                    'crypto_id': crypto_id,
                    'signal_type': f'macd_{signal_type}',
                    'detected_at': timestamp.to_pydatetime().replace(tzinfo=timezone.utc),
                    'confidence': confidence_scores['overall_confidence'],
                    'trigger_price': float(df.loc[timestamp, 'close']),
                    'metadata': {
                        'histogram_value': float(histogram_value),
                        'histogram_percentile': histogram_percentile,
                        'confidence_components': confidence_scores,
                        'analysis_mode': 'advanced'
                    }
                })
    
    # 2. Bollinger Band Signals
    if bb_df is not None:
        bb_signals = TechnicalIndicators.detect_bollinger_signals(bb_df, df['close'])
        
        # Get bandwidth for percentile calculation
        bandwidth_col = [col for col in bb_df.columns if 'BBB_' in col][0]
        bandwidth_values = bb_df[bandwidth_col].dropna().tolist()
        
        for signal_type, signal_list in bb_signals.items():
            if signal_type == 'squeeze_breakout':
                for timestamp, bandwidth in signal_list[-2:]:  # Limit squeeze breakouts
                    bandwidth_percentile = ConfidenceModel.calculate_histogram_percentile(
                        bandwidth, bandwidth_values
                    )
                    
                    confidence_scores = ConfidenceModel.calculate_confidence(
                        adx_value=current_adx,
                        bollinger_bandwidth_percentile=bandwidth_percentile,
                        signal_type='squeeze_breakout'
                    )
                    
                    signals.append({
                        'crypto_id': crypto_id,
                        'signal_type': 'bollinger_breakout',
                        'detected_at': timestamp.to_pydatetime().replace(tzinfo=timezone.utc),
                        'confidence': confidence_scores['overall_confidence'],
                        'trigger_price': float(df.loc[timestamp, 'close']),
                        'metadata': {
                            'bandwidth': float(bandwidth),
                            'bandwidth_percentile': bandwidth_percentile,
                            'confidence_components': confidence_scores,
                            'analysis_mode': 'advanced'
                        }
                    })
    
    # 3. RSI Signals with dynamic thresholds
    if rsi is not None and len(rsi) > 200:
        # Calculate dynamic thresholds
        oversold_threshold, overbought_threshold = AdaptiveThresholds.get_adaptive_rsi_thresholds(
            rsi, lookback=200, sensitivity='normal'
        )
        
        rsi_signals = TechnicalIndicators.detect_rsi_signals(
            rsi, overbought=overbought_threshold, oversold=oversold_threshold
        )
        
        for signal_type, signal_list in rsi_signals.items():
            if 'exit' in signal_type:  # Focus on exit signals (potential reversals)
                for timestamp, rsi_value in signal_list[-2:]:
                    confidence_scores = ConfidenceModel.calculate_confidence(
                        adx_value=current_adx,
                        signal_type='rsi_oversold' if 'oversold' in signal_type else 'rsi_overbought'
                    )
                    
                    signals.append({
                        'crypto_id': crypto_id,
                        'signal_type': 'rsi_oversold' if 'oversold' in signal_type else 'rsi_overbought',
                        'detected_at': timestamp.to_pydatetime().replace(tzinfo=timezone.utc),
                        'confidence': confidence_scores['overall_confidence'],
                        'trigger_price': float(df.loc[timestamp, 'close']),
                        'metadata': {
                            'rsi_value': float(rsi_value),
                            'oversold_threshold': oversold_threshold,
                            'overbought_threshold': overbought_threshold,
                            'confidence_components': confidence_scores,
                            'analysis_mode': 'advanced'
                        }
                    })
    
    # 4. Moving Average Crossover Signals
    if sma_50 is not None and sma_200 is not None and len(sma_200.dropna()) > 0:
        ma_crossovers = TechnicalIndicators.detect_ma_crossover(sma_50, sma_200)
        
        for cross_type, timestamps in ma_crossovers.items():
            for timestamp in timestamps[-1:]:  # Only most recent crossover
                confidence_scores = ConfidenceModel.calculate_confidence(
                    adx_value=current_adx,
                    signal_type=cross_type
                )
                
                signals.append({
                    'crypto_id': crypto_id,
                    'signal_type': cross_type,
                    'detected_at': timestamp.to_pydatetime().replace(tzinfo=timezone.utc),
                    'confidence': confidence_scores['overall_confidence'],
                    'trigger_price': float(df.loc[timestamp, 'close']),
                    'metadata': {
                        'sma_50': float(sma_50.loc[timestamp]),
                        'sma_200': float(sma_200.loc[timestamp]),
                        'confidence_components': confidence_scores,
                        'analysis_mode': 'advanced'
                    }
                })
    
    return signals

def detect_signals_in_window(window_data, crypto_id, window_start_idx):
    """Detect signals within a specific time window"""
    signals = []
    
    if len(window_data) < 7:
        return signals
    
    prices = [p['price_usd'] for p in window_data]
    volumes = [p['volume_24h'] for p in window_data]
    
    # 1. PUMP AND DUMP DETECTION (48h window)
    if len(prices) >= 12:  # Need at least 12 data points for 48h analysis
        # Split into pump window (first 24h) and dump window (last 24h)
        pump_window = prices[:6]  # First 6 points (24h)
        dump_window = prices[6:]  # Last 6 points (24h)
        
        if len(pump_window) >= 3 and len(dump_window) >= 3:
            pump_start = min(pump_window)
            pump_peak = max(pump_window)
            dump_end = min(dump_window)
            
            pump_percent = ((pump_peak - pump_start) / pump_start) * 100
            dump_percent = ((dump_end - pump_peak) / pump_peak) * 100
            
            # Much more conservative thresholds for pump & dump
            if pump_percent > 50 and dump_percent < -30:
                # Calculate volume spike during pump
                pump_volumes = volumes[:6]
                avg_volume = np.mean(pump_volumes)
                max_volume = max(pump_volumes)
                volume_spike_ratio = max_volume / avg_volume if avg_volume > 0 else 1.0
                
                # Additional validation: minimum volume spike and price movement
                if volume_spike_ratio >= 3.0 and pump_percent >= 50 and dump_percent <= -30:
                    signals.append({
                        'crypto_id': crypto_id,
                        'signal_type': 'pump_and_dump',
                        'detected_at': window_data[6]['timestamp'],  # Time of dump
                        'confidence': min((pump_percent + abs(dump_percent)) / 120, 1.0),
                        'trigger_price': pump_peak,
                        'volume_spike_ratio': volume_spike_ratio,
                        'metadata': {
                            'pump_percent': pump_percent,
                            'dump_percent': dump_percent,
                            'window_size_days': len(window_data),
                            'analysis_window': f"{window_start_idx}-{window_start_idx + len(window_data)}"
                        }
                    })
    
    # 2. VOLUME ANOMALY DETECTION (14d baseline)
    if len(volumes) >= 7:
        # Use 14-day baseline for more reliable average
        baseline_volumes = volumes[:-1]  # All but last point
        spike_volume = volumes[-1]
        
        avg_volume = np.mean(baseline_volumes)
        
        if avg_volume > 0 and spike_volume > avg_volume * 5:  # 5x threshold for volume anomaly
            signals.append({
                'crypto_id': crypto_id,
                'signal_type': 'volume_anomaly',
                'detected_at': window_data[-1]['timestamp'],
                'confidence': min(spike_volume / (avg_volume * 8), 1.0),
                'volume_spike_ratio': spike_volume / avg_volume,
                'metadata': {
                    'avg_volume': avg_volume,
                    'spike_volume': spike_volume,
                    'baseline_days': len(baseline_volumes),
                    'analysis_window': f"{window_start_idx}-{window_start_idx + len(window_data)}"
                }
            })
    
    # 3. BOTTOMED OUT DETECTION (21d pattern)
    if len(prices) >= 14:
        # Check for 14d downtrend followed by 7d recovery
        downtrend_prices = prices[:7]  # First 7 points (14d)
        recovery_prices = prices[7:]   # Last 7 points (7d)
        
        if len(downtrend_prices) >= 5 and len(recovery_prices) >= 5:
            downtrend = (downtrend_prices[-1] - downtrend_prices[0]) / downtrend_prices[0] * 100
            recovery = (recovery_prices[-1] - recovery_prices[0]) / recovery_prices[0] * 100
            
            # More conservative bottomed out detection
            if downtrend < -15 and recovery > 10:
                signals.append({
                    'crypto_id': crypto_id,
                    'signal_type': 'bottomed_out',
                    'detected_at': window_data[-1]['timestamp'],
                    'confidence': min((abs(downtrend) + recovery) / 40, 1.0),
                    'trigger_price': recovery_prices[-1],
                    'metadata': {
                        'downtrend_percent': downtrend,
                        'recovery_percent': recovery,
                        'pattern_days': len(window_data),
                        'analysis_window': f"{window_start_idx}-{window_start_idx + len(window_data)}"
                    }
                })
    
    return signals

def run_analysis():
    """Run trend analysis on all cryptocurrencies with improved 30-day utilization"""
    analysis_mode = os.environ.get('ANALYSIS_MODE', 'advanced')
    print("="*80)
    print(f"TREND ANALYSIS EC2 TEST RUNNER - {analysis_mode.upper()} MODE")
    print("="*80)
    print(f"Start Time: {datetime.now(timezone.utc)}")
    
    if analysis_mode == 'advanced' and ADVANCED_ANALYSIS_AVAILABLE:
        print("Using advanced technical indicators (MA, MACD, RSI, Bollinger Bands)")
    elif analysis_mode == 'advanced' and not ADVANCED_ANALYSIS_AVAILABLE:
        print("WARNING: Advanced mode requested but dependencies not available, falling back to legacy")
    else:
        print("Using legacy linear regression analysis")
    
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
                
                # Get price data (180 days)
                price_data = db.get_price_data(crypto_id, days=180)
                
                if len(price_data) < 14:
                    print(" [SKIP: Insufficient data]")
                    continue
                
                # Choose analysis mode
                analysis_mode = os.environ.get('ANALYSIS_MODE', 'advanced')
                
                # Analyze trends with multiple timeframes
                trends_found = 0
                for timeframe in ['7d', '14d', '30d']:
                    if analysis_mode == 'advanced' and ADVANCED_ANALYSIS_AVAILABLE:
                        trend = analyze_trend_advanced(price_data, timeframe, crypto_id)
                    else:
                        trend = analyze_trend(price_data, timeframe, crypto_id)
                    
                    if trend:
                        db.store_trend_analysis(trend)
                        trends_found += 1
                        total_trends += 1
                
                # Detect signals using appropriate method
                if analysis_mode == 'advanced' and ADVANCED_ANALYSIS_AVAILABLE:
                    signals = detect_signals_advanced(price_data, crypto_id)
                else:
                    signals = detect_signals_sliding_window(price_data, crypto_id)
                
                # Apply quality validation
                quality_signals = []
                for signal in signals:
                    if validate_signal_quality(signal):
                        quality_signals.append(signal)
                
                # Store only quality signals
                for signal in quality_signals:
                    db.store_signal_event(signal)
                    total_signals += 1
                    signal_type = signal['signal_type']
                    signal_types[signal_type] = signal_types.get(signal_type, 0) + 1
                
                processed += 1
                print(f" [OK: {trends_found} trends, {len(signals)} detected, {len(quality_signals)} quality signals]")
                
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Run cryptocurrency trend analysis')
    parser.add_argument('--mode', choices=['legacy', 'advanced'], default='advanced',
                       help='Analysis mode: legacy (original) or advanced (technical indicators)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Set analysis mode
    os.environ['ANALYSIS_MODE'] = args.mode
    
    exit_code = run_analysis()
    sys.exit(exit_code)