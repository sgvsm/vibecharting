import numpy as np
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SignalDetector:
    """Detects market signals with improved thresholds and multiple signal types"""
    
    def __init__(self):
        # Improved pump & dump detection thresholds
        self.pump_price_increase_threshold = 30.0  # 30% price increase (was 20%)
        self.pump_time_window_hours = 12  # Within 12 hours (was 4)
        self.pump_volume_multiplier = 3.0  # 3x average volume
        self.dump_price_decrease_threshold = 20.0  # 20% decrease after pump (was 15%)
        self.dump_time_window_hours = 12  # Within 12 hours of pump (was 24)
        
        # Improved bottomed out detection thresholds
        self.bottom_recovery_threshold = 8.0  # 8% recovery from low (was 5%)
        self.bottom_downtrend_days = 7  # Must have downtrend for 7 days
        self.bottom_confidence_threshold = 0.6  # Trend confidence threshold (was 0.7)
        
        # Volume anomaly thresholds
        self.volume_spike_threshold = 5.0  # 5x average volume (was 3x)
        
        # Parabolic rise thresholds
        self.parabolic_min_rise = 50.0  # 50% total rise
        self.parabolic_min_increasing_changes = 3  # At least 3 accelerating changes
        
        # Capitulation drop thresholds
        self.capitulation_downtrend_threshold = 15.0  # 15% downtrend
        self.capitulation_drop_threshold = 25.0  # 25% sharp drop
    
    def detect_signals(self, price_data: List[Dict[str, Any]], 
                      crypto_id: int) -> List[Dict[str, Any]]:
        """
        Detect all types of market signals with improved algorithms
        
        Args:
            price_data: List of price data points (sorted by timestamp)
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            List of detected signals
        """
        signals = []
        
        try:
            if len(price_data) < 14:  # Need at least 2 weeks of data
                return signals
            
            # Sort data by timestamp (oldest first for analysis)
            sorted_data = sorted(price_data, key=lambda x: x['timestamp'])
            
            # Detect pump & dump signals
            pump_dump_signals = self._detect_pump_and_dump_improved(sorted_data, crypto_id)
            signals.extend(pump_dump_signals)
            
            # Detect bottomed out signals
            bottomed_out_signals = self._detect_bottomed_out_improved(sorted_data, crypto_id)
            signals.extend(bottomed_out_signals)
            
            # Detect volume anomalies
            volume_signals = self._detect_volume_anomalies_improved(sorted_data, crypto_id)
            signals.extend(volume_signals)
            
            # Detect parabolic rise
            parabolic_signals = self._detect_parabolic_rise_improved(sorted_data, crypto_id)
            signals.extend(parabolic_signals)
            
            # Detect capitulation drop
            capitulation_signals = self._detect_capitulation_drop_improved(sorted_data, crypto_id)
            signals.extend(capitulation_signals)
            
            logger.info(f"Detected {len(signals)} signals for crypto ID {crypto_id}")
            return signals
            
        except Exception as e:
            logger.error(f"Error detecting signals for crypto {crypto_id}: {str(e)}")
            return []
    
    def _detect_pump_and_dump_improved(self, price_data: List[Dict[str, Any]], 
                                      crypto_id: int) -> List[Dict[str, Any]]:
        """
        Improved pump and dump detection with better thresholds
        
        Args:
            price_data: List of price data points (oldest first)
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            List of pump & dump signals
        """
        signals = []
        
        try:
            if len(price_data) < 24:  # Need at least 24 data points
                return signals
            
            # Look for pump patterns in recent data
            recent_data = price_data[-24:]  # Last 24 data points
            prices = [p['price_usd'] for p in recent_data]
            volumes = [p['volume_24h'] for p in recent_data]
            
            # Split into pump window (first 12 hours) and dump window (last 12 hours)
            pump_window = prices[:12]
            dump_window = prices[12:]
            
            if len(pump_window) >= 6 and len(dump_window) >= 6:
                pump_start = min(pump_window)
                pump_peak = max(pump_window)
                dump_end = min(dump_window)
                
                pump_percent = ((pump_peak - pump_start) / pump_start) * 100
                dump_percent = ((dump_end - pump_peak) / pump_peak) * 100
                
                # Check for pump and dump pattern with improved thresholds
                if (pump_percent > self.pump_price_increase_threshold and 
                    dump_percent < -self.dump_price_decrease_threshold):
                    
                    # Calculate volume spike during pump
                    pump_volumes = volumes[:12]
                    avg_volume = np.mean(pump_volumes)
                    max_volume = max(pump_volumes)
                    volume_spike_ratio = max_volume / avg_volume if avg_volume > 0 else 1.0
                    
                    signals.append({
                        'crypto_id': crypto_id,
                        'signal_type': 'pump_and_dump',
                        'detected_at': datetime.now(timezone.utc),
                        'confidence': min((pump_percent + abs(dump_percent)) / 100, 1.0),
                        'trigger_price': pump_peak,
                        'volume_spike_ratio': volume_spike_ratio,
                        'metadata': {
                            'pump_percent': pump_percent,
                            'dump_percent': dump_percent,
                            'pump_start_price': pump_start,
                            'pump_peak_price': pump_peak,
                            'dump_end_price': dump_end,
                            'volume_spike_ratio': volume_spike_ratio
                        }
                    })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in pump and dump detection: {str(e)}")
            return []
    
    def _detect_bottomed_out_improved(self, price_data: List[Dict[str, Any]], 
                                     crypto_id: int) -> List[Dict[str, Any]]:
        """
        Improved bottomed out detection
        
        Args:
            price_data: List of price data points (oldest first)
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            List of bottomed out signals
        """
        signals = []
        
        try:
            if len(price_data) < 14:  # Need at least 2 weeks of data
                return signals
            
            # Check for 7+ days of downtrend followed by recovery
            week_ago_prices = [p['price_usd'] for p in price_data[-14:-7]]
            recent_prices = [p['price_usd'] for p in price_data[-7:]]
            
            if len(week_ago_prices) >= 5 and len(recent_prices) >= 5:
                week_trend = (week_ago_prices[-1] - week_ago_prices[0]) / week_ago_prices[0] * 100
                recent_trend = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
                
                # Downtrend for a week followed by recovery
                if (week_trend < -10 and recent_trend > self.bottom_recovery_threshold):
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
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in bottomed out detection: {str(e)}")
            return []
    
    def _detect_volume_anomalies_improved(self, price_data: List[Dict[str, Any]], 
                                         crypto_id: int) -> List[Dict[str, Any]]:
        """
        Improved volume anomaly detection
        
        Args:
            price_data: List of price data points (oldest first)
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            List of volume anomaly signals
        """
        signals = []
        
        try:
            if len(price_data) < 7:  # Need at least 7 data points
                return signals
            
            # Calculate rolling average volume
            recent_data = price_data[-7:]
            volumes = [p['volume_24h'] for p in recent_data]
            
            if len(volumes) >= 7:
                # Use 6 days as baseline, check 7th day for spike
                baseline_volumes = volumes[:-1]
                spike_volume = volumes[-1]
                
                avg_volume = np.mean(baseline_volumes)
                
                if avg_volume > 0 and spike_volume > avg_volume * self.volume_spike_threshold:
                    signals.append({
                        'crypto_id': crypto_id,
                        'signal_type': 'volume_anomaly',
                        'detected_at': datetime.now(timezone.utc),
                        'confidence': min(spike_volume / (avg_volume * 10), 1.0),
                        'volume_spike_ratio': spike_volume / avg_volume,
                        'metadata': {
                            'avg_volume': avg_volume,
                            'spike_volume': spike_volume,
                            'volume_increase_percent': ((spike_volume - avg_volume) / avg_volume) * 100
                        }
                    })
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in volume anomaly detection: {str(e)}")
            return []
    
    def _detect_parabolic_rise_improved(self, price_data: List[Dict[str, Any]], 
                                       crypto_id: int) -> List[Dict[str, Any]]:
        """
        Improved parabolic rise detection
        
        Args:
            price_data: List of price data points (oldest first)
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            List of parabolic rise signals
        """
        signals = []
        
        try:
            if len(price_data) < 10:  # Need at least 10 data points
                return signals
            
            # Check for exponential growth pattern
            recent_prices = [p['price_usd'] for p in price_data[-10:]]
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
                
                # Parabolic pattern: accelerating changes with significant total rise
                if (increasing_changes >= self.parabolic_min_increasing_changes and 
                    total_rise > self.parabolic_min_rise):
                    
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
            
            return signals
            
        except Exception as e:
            logger.error(f"Error in parabolic rise detection: {str(e)}")
            return []
    
    def _detect_capitulation_drop_improved(self, price_data: List[Dict[str, Any]], 
                                          crypto_id: int) -> List[Dict[str, Any]]:
        """
        Improved capitulation drop detection
        
        Args:
            price_data: List of price data points (oldest first)
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            List of capitulation drop signals
        """
        signals = []
        
        try:
            if len(price_data) < 14:  # Need at least 2 weeks of data
                return signals
            
            # Check for sharp drop after prolonged downtrend
            week_ago_prices = [p['price_usd'] for p in price_data[-14:-7]]
            recent_prices = [p['price_usd'] for p in price_data[-7:]]
            
            if len(week_ago_prices) >= 5 and len(recent_prices) >= 5:
                week_trend = (week_ago_prices[-1] - week_ago_prices[0]) / week_ago_prices[0] * 100
                recent_drop = (recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
                
                # Prolonged downtrend followed by sharp drop
                if (week_trend < -self.capitulation_downtrend_threshold and 
                    recent_drop < -self.capitulation_drop_threshold):
                    
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
            
        except Exception as e:
            logger.error(f"Error in capitulation drop detection: {str(e)}")
            return []
    
    # Legacy methods for backward compatibility
    def _detect_pump_and_dump(self, price_data: List[Dict[str, Any]], 
                             crypto_id: int) -> List[Dict[str, Any]]:
        """Legacy pump and dump detection"""
        return self._detect_pump_and_dump_improved(price_data, crypto_id)
    
    def _detect_bottomed_out(self, price_data: List[Dict[str, Any]], 
                            crypto_id: int) -> List[Dict[str, Any]]:
        """Legacy bottomed out detection"""
        return self._detect_bottomed_out_improved(price_data, crypto_id)
    
    def _detect_volume_anomalies(self, price_data: List[Dict[str, Any]], 
                                crypto_id: int) -> List[Dict[str, Any]]:
        """Legacy volume anomaly detection"""
        return self._detect_volume_anomalies_improved(price_data, crypto_id)
    
    def _detect_parabolic_rise(self, price_data: List[Dict[str, Any]], 
                              crypto_id: int) -> List[Dict[str, Any]]:
        """Legacy parabolic rise detection"""
        return self._detect_parabolic_rise_improved(price_data, crypto_id)
    
    def _detect_capitulation_drop(self, price_data: List[Dict[str, Any]], 
                                crypto_id: int) -> List[Dict[str, Any]]:
        """Legacy capitulation drop detection"""
        return self._detect_capitulation_drop_improved(price_data, crypto_id)
    
    def _detect_low_volume_drift(self, price_data: List[Dict[str, Any]], 
                                crypto_id: int) -> List[Dict[str, Any]]:
        """Legacy low volume drift detection (kept for compatibility)"""
        return [] 