import numpy as np
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from scipy import stats

logger = logging.getLogger(__name__)

class TrendAnalyzer:
    """Analyzes price data to detect trends using statistical methods"""
    
    def __init__(self):
        # Improved trend detection thresholds
        self.min_r_squared = 0.3  # Lower minimum R² for more realistic detection
        self.min_data_points = {
            '24h': 3,   # Minimum data points for 24h analysis
            '7d': 5,    # Minimum data points for 7d analysis
            '30d': 15   # Minimum data points for 30d analysis
        }
    
    def analyze_trend(self, price_data: List[Dict[str, Any]], 
                     timeframe: str, crypto_id: int) -> Optional[Dict[str, Any]]:
        """
        Analyze trend for a specific timeframe with improved thresholds
        
        Args:
            price_data: List of price data points (sorted by timestamp)
            timeframe: Time period to analyze ('24h', '7d', '30d')
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            Dictionary containing trend analysis results or None
        """
        try:
            # Filter data for the specified timeframe
            filtered_data = self._filter_data_by_timeframe(price_data, timeframe)
            
            if len(filtered_data) < self.min_data_points.get(timeframe, 5):
                logger.warning(f"Insufficient data for {timeframe} analysis: {len(filtered_data)} points")
                return None
            
            # Extract prices and timestamps
            prices = [float(point['price_usd']) for point in filtered_data]
            timestamps = [point['timestamp'] for point in filtered_data]
            
            # Convert timestamps to numeric values for regression
            base_time = timestamps[0]
            time_deltas = [(ts - base_time).total_seconds() / 3600 for ts in timestamps]  # Hours
            
            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_deltas, prices)
            r_squared = r_value ** 2
            
            # Calculate additional metrics
            price_change_percent = ((prices[-1] - prices[0]) / prices[0]) * 100
            volatility = np.std(prices) / np.mean(prices) * 100  # Coefficient of variation
            
            # Improved trend classification with better thresholds
            trend_type, confidence = self._classify_trend_improved(slope, r_squared, volatility, p_value, price_change_percent)
            
            # Create analysis result
            result = {
                'crypto_id': crypto_id,
                'timeframe': timeframe,
                'trend_type': trend_type,
                'confidence': round(confidence, 4),
                'start_time': timestamps[0],
                'end_time': timestamps[-1],
                'price_change_percent': round(price_change_percent, 4),
                'metadata': {
                    'slope': round(slope, 8),
                    'r_squared': round(r_squared, 4),
                    'p_value': round(p_value, 6),
                    'volatility': round(volatility, 4),
                    'data_points': len(filtered_data),
                    'start_price': round(prices[0], 8),
                    'end_price': round(prices[-1], 8)
                }
            }
            
            logger.info(f"Trend analysis completed: {trend_type} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in trend analysis for timeframe {timeframe}: {str(e)}")
            return None
    
    def _filter_data_by_timeframe(self, price_data: List[Dict[str, Any]], 
                                 timeframe: str) -> List[Dict[str, Any]]:
        """
        Filter price data by timeframe
        
        Args:
            price_data: List of price data points
            timeframe: Time period ('24h', '7d', '30d')
            
        Returns:
            Filtered list of price data
        """
        if not price_data:
            return []
        
        # Calculate cutoff time
        now = datetime.now(timezone.utc)
        if timeframe == '24h':
            cutoff = now - timedelta(hours=24)
        elif timeframe == '7d':
            cutoff = now - timedelta(days=7)
        elif timeframe == '30d':
            cutoff = now - timedelta(days=30)
        else:
            cutoff = now - timedelta(hours=24)
        
        # Filter data within timeframe
        filtered_data = [point for point in price_data if point['timestamp'] >= cutoff]
        
        # Sort by timestamp
        filtered_data.sort(key=lambda x: x['timestamp'])
        
        return filtered_data
    
    def _classify_trend_improved(self, slope: float, r_squared: float, 
                                volatility: float, p_value: float, 
                                price_change_percent: float) -> tuple:
        """
        Improved trend classification with better thresholds
        
        Args:
            slope: Linear regression slope
            r_squared: Coefficient of determination
            volatility: Price volatility (coefficient of variation)
            p_value: Statistical significance
            price_change_percent: Total price change percentage
            
        Returns:
            Tuple of (trend_type, confidence)
        """
        # Improved trend classification with more conservative thresholds
        if abs(price_change_percent) < 1.0:  # More conservative sideways threshold
            trend_type = 'sideways'
        elif price_change_percent > 5.0:  # Higher threshold for uptrend
            trend_type = 'uptrend'
        elif price_change_percent < -5.0:  # Higher threshold for downtrend
            trend_type = 'downtrend'
        else:
            trend_type = 'sideways'
        
        # Improved confidence calculation
        # Base confidence on R-squared and data quality
        base_confidence = r_squared
        
        # Adjust for statistical significance
        if p_value < 0.05:  # Statistically significant
            significance_boost = 0.2
        elif p_value < 0.1:  # Marginally significant
            significance_boost = 0.1
        else:
            significance_boost = 0.0
        
        # Adjust for volatility (lower volatility = higher confidence)
        volatility_penalty = min(volatility / 100, 0.3)
        
        # Calculate final confidence
        confidence = min(base_confidence + significance_boost - volatility_penalty, 1.0)
        confidence = max(confidence, 0.0)  # Ensure non-negative
        
        return trend_type, confidence
    
    def _classify_trend(self, slope: float, r_squared: float, 
                       volatility: float, p_value: float) -> tuple:
        """
        Legacy trend classification (kept for backward compatibility)
        """
        # Determine trend type based on slope and R-squared
        if r_squared < self.min_r_squared:
            trend_type = 'sideways'
        elif slope > 0:
            trend_type = 'uptrend'
        else:
            trend_type = 'downtrend'
        
        # Calculate confidence based on R-squared and volatility
        confidence = r_squared * (1 - min(volatility / 100, 0.5))
        
        return trend_type, confidence
    
    def calculate_trend_strength(self, price_data: List[Dict[str, Any]]) -> float:
        """
        Calculate overall trend strength
        
        Args:
            price_data: List of price data points
            
        Returns:
            Trend strength score (0-1)
        """
        if len(price_data) < 5:
            return 0.0
        
        try:
            # Extract prices
            prices = [float(point['price_usd']) for point in price_data]
            
            # Calculate price changes
            changes = []
            for i in range(1, len(prices)):
                change = (prices[i] - prices[i-1]) / prices[i-1]
                changes.append(change)
            
            # Calculate trend strength metrics
            avg_change = np.mean(changes)
            change_consistency = 1 - np.std(changes) / (abs(avg_change) + 0.001)
            
            # Combine metrics
            strength = abs(avg_change) * change_consistency
            
            return min(strength, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating trend strength: {str(e)}")
            return 0.0
    
    def detect_trend_reversal(self, price_data: List[Dict[str, Any]], 
                             crypto_id: int) -> Optional[Dict[str, Any]]:
        """
        Detect trend reversals by comparing short-term vs long-term trends
        
        Args:
            price_data: List of price data points
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            Dictionary containing reversal analysis or None
        """
        try:
            if len(price_data) < 14:  # Need sufficient data
                return None
            
            # Analyze short-term trend (last 7 days)
            short_term = self.analyze_trend(price_data, '7d', crypto_id)
            
            # Analyze long-term trend (last 30 days)
            long_term = self.analyze_trend(price_data, '30d', crypto_id)
            
            if not short_term or not long_term:
                return None
            
            # Check for reversal patterns
            reversal_type = None
            
            if (long_term['trend_type'] == 'downtrend' and
                short_term['trend_type'] in ['uptrend', 'sideways'] and
                short_term['confidence'] > 0.6):
                reversal_type = 'bullish_reversal'
            elif (long_term['trend_type'] == 'uptrend' and
                  short_term['trend_type'] == 'downtrend' and
                  short_term['confidence'] > 0.6):
                reversal_type = 'bearish_reversal'
            
            if reversal_type:
                return {
                    'crypto_id': crypto_id,
                    'signal_type': reversal_type,
                    'detected_at': datetime.now(timezone.utc),
                    'confidence': (short_term['confidence'] + long_term['confidence']) / 2,
                    'metadata': {
                        'short_term_trend': short_term['trend_type'],
                        'long_term_trend': long_term['trend_type'],
                        'short_term_confidence': short_term['confidence'],
                        'long_term_confidence': long_term['confidence']
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting trend reversal: {str(e)}")
            return None
    
    def detect_gradual_uptrend(self, price_data: List[Dict[str, Any]], 
                              crypto_id: int) -> Optional[Dict[str, Any]]:
        """
        Detect gradual uptrends (not parabolic)
        
        Args:
            price_data: List of price data points
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            Dictionary containing gradual uptrend analysis or None
        """
        try:
            if len(price_data) < 14:
                return None
            
            # Analyze 7-day trend
            trend_result = self.analyze_trend(price_data, '7d', crypto_id)
            
            if not trend_result or trend_result['trend_type'] != 'uptrend':
                return None
            
            # Check for gradual (not parabolic) pattern
            prices = [float(point['price_usd']) for point in price_data[-14:]]
            changes = []
            
            for i in range(1, len(prices)):
                change = (prices[i] - prices[i-1]) / prices[i-1] * 100
                changes.append(change)
            
            # Calculate if changes are consistent (not accelerating)
            avg_change = np.mean(changes)
            change_std = np.std(changes)
            
            # Gradual uptrend: consistent positive changes, low volatility
            if (avg_change > 2.0 and  # Positive average change
                change_std < avg_change * 0.5 and  # Low volatility
                trend_result['confidence'] > 0.6):
                
                return {
                    'crypto_id': crypto_id,
                    'signal_type': 'gradual_uptrend',
                    'detected_at': datetime.now(timezone.utc),
                    'confidence': trend_result['confidence'],
                    'trigger_price': prices[-1],
                    'metadata': {
                        'avg_daily_change': avg_change,
                        'change_volatility': change_std,
                        'total_rise_percent': trend_result['price_change_percent']
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting gradual uptrend: {str(e)}")
            return None
    
    def detect_macro_downtrend(self, price_data: List[Dict[str, Any]], 
                              crypto_id: int) -> Optional[Dict[str, Any]]:
        """
        Detect macro downtrends (long-term decline)
        
        Args:
            price_data: List of price data points
            crypto_id: Internal cryptocurrency ID
            
        Returns:
            Dictionary containing macro downtrend analysis or None
        """
        try:
            if len(price_data) < 30:
                return None
            
            # Analyze 30-day trend
            trend_result = self.analyze_trend(price_data, '30d', crypto_id)
            
            if not trend_result or trend_result['trend_type'] != 'downtrend':
                return None
            
            # Check for sustained decline
            prices = [float(point['price_usd']) for point in price_data[-30:]]
            total_decline = ((prices[-1] - prices[0]) / prices[0]) * 100
            
            # Macro downtrend: significant sustained decline
            if (total_decline < -15.0 and  # Significant decline
                trend_result['confidence'] > 0.7):  # High confidence
                
                return {
                    'crypto_id': crypto_id,
                    'signal_type': 'macro_downtrend',
                    'detected_at': datetime.now(timezone.utc),
                    'confidence': trend_result['confidence'],
                    'trigger_price': prices[-1],
                    'metadata': {
                        'total_decline_percent': total_decline,
                        'duration_days': 30,
                        'avg_daily_decline': total_decline / 30
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error detecting macro downtrend: {str(e)}")
            return None 