#!/usr/bin/env python3
"""
Adaptive Thresholds Module
Implements dynamic, volatility-normalized thresholds for technical analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List


class AdaptiveThresholds:
    """Calculate and manage dynamic thresholds based on market conditions"""
    
    @staticmethod
    def calculate_atr_based_thresholds(atr: float, base_multipliers: Dict[str, float] = None) -> Dict[str, float]:
        """
        Calculate ATR-based thresholds for various trading decisions
        
        Args:
            atr: Current Average True Range value
            base_multipliers: Dict of threshold names to ATR multipliers
            
        Returns:
            Dict of threshold names to calculated values
        """
        if base_multipliers is None:
            base_multipliers = {
                'stop_loss': 2.0,           # 2x ATR for stop loss
                'take_profit': 3.0,         # 3x ATR for take profit
                'significant_move': 1.5,    # 1.5x ATR for significant price move
                'breakout_confirmation': 1.0, # 1x ATR for breakout confirmation
                'trend_filter': 0.5         # 0.5x ATR for trend noise filter
            }
        
        thresholds = {}
        for name, multiplier in base_multipliers.items():
            thresholds[name] = atr * multiplier
        
        return thresholds
    
    @staticmethod
    def calculate_percentile_thresholds(values: pd.Series, 
                                      percentiles: Dict[str, float] = None) -> Dict[str, float]:
        """
        Calculate thresholds based on historical percentiles
        
        Args:
            values: Historical values (e.g., RSI, volume)
            percentiles: Dict of threshold names to percentile values (0-100)
            
        Returns:
            Dict of threshold names to calculated values
        """
        if percentiles is None:
            percentiles = {
                'extreme_high': 95,
                'high': 85,
                'moderate_high': 70,
                'moderate_low': 30,
                'low': 15,
                'extreme_low': 5
            }
        
        thresholds = {}
        clean_values = values.dropna()
        
        if len(clean_values) < 20:  # Need minimum data
            return thresholds
        
        for name, percentile in percentiles.items():
            thresholds[name] = np.percentile(clean_values, percentile)
        
        return thresholds
    
    @staticmethod
    def get_adaptive_rsi_thresholds(rsi_series: pd.Series, 
                                   lookback: int = 200,
                                   sensitivity: str = 'normal') -> Tuple[float, float]:
        """
        Calculate adaptive RSI overbought/oversold thresholds
        
        Args:
            rsi_series: Historical RSI values
            lookback: Number of periods to analyze
            sensitivity: 'conservative', 'normal', or 'aggressive'
            
        Returns:
            Tuple of (oversold_threshold, overbought_threshold)
        """
        if len(rsi_series) < lookback:
            # Return standard thresholds if insufficient data
            return (30.0, 70.0)
        
        recent_rsi = rsi_series.iloc[-lookback:]
        
        # Define percentiles based on sensitivity
        percentile_map = {
            'conservative': (20, 80),  # Wider range, fewer signals
            'normal': (15, 85),        # Standard range
            'aggressive': (10, 90)     # Tighter range, more signals
        }
        
        low_percentile, high_percentile = percentile_map.get(sensitivity, (15, 85))
        
        oversold = np.percentile(recent_rsi.dropna(), low_percentile)
        overbought = np.percentile(recent_rsi.dropna(), high_percentile)
        
        # Ensure reasonable bounds
        oversold = max(20.0, min(40.0, oversold))
        overbought = max(60.0, min(80.0, overbought))
        
        return (oversold, overbought)
    
    @staticmethod
    def get_adaptive_volume_threshold(volume_series: pd.Series,
                                    lookback: int = 30,
                                    spike_sensitivity: float = 3.0) -> Dict[str, float]:
        """
        Calculate adaptive volume spike thresholds
        
        Args:
            volume_series: Historical volume data
            lookback: Number of periods for baseline calculation
            spike_sensitivity: Multiplier for spike detection (higher = less sensitive)
            
        Returns:
            Dict with volume thresholds
        """
        if len(volume_series) < lookback:
            return {'spike_threshold': float('inf'), 'baseline': 0}
        
        recent_volume = volume_series.iloc[-lookback:]
        
        # Calculate robust baseline using median (less affected by spikes)
        baseline = recent_volume.median()
        
        # Calculate MAD (Median Absolute Deviation) for robust volatility measure
        mad = np.median(np.abs(recent_volume - baseline))
        
        # Adaptive spike threshold
        spike_threshold = baseline + (spike_sensitivity * mad * 1.4826)  # 1.4826 converts MAD to std
        
        # Also calculate percentile-based thresholds
        volume_percentiles = AdaptiveThresholds.calculate_percentile_thresholds(
            recent_volume,
            {'high_volume': 90, 'very_high_volume': 95, 'extreme_volume': 99}
        )
        
        return {
            'baseline': baseline,
            'spike_threshold': spike_threshold,
            'mad': mad,
            **volume_percentiles
        }
    
    @staticmethod
    def get_adaptive_bollinger_width(bandwidth_series: pd.Series,
                                   lookback: int = 100) -> Dict[str, float]:
        """
        Calculate adaptive Bollinger Band width thresholds for squeeze detection
        
        Args:
            bandwidth_series: Historical Bollinger Bandwidth values
            lookback: Number of periods to analyze
            
        Returns:
            Dict with bandwidth thresholds
        """
        if len(bandwidth_series) < lookback:
            return {'squeeze_threshold': 0, 'expansion_threshold': float('inf')}
        
        recent_bandwidth = bandwidth_series.iloc[-lookback:]
        
        # Calculate percentile-based thresholds
        thresholds = AdaptiveThresholds.calculate_percentile_thresholds(
            recent_bandwidth,
            {
                'extreme_squeeze': 5,
                'squeeze': 10,
                'normal_low': 25,
                'normal_high': 75,
                'expansion': 90,
                'extreme_expansion': 95
            }
        )
        
        return thresholds
    
    @staticmethod
    def normalize_price_change(price_change: float, atr: float) -> float:
        """
        Normalize a price change by ATR to make it comparable across different volatility regimes
        
        Args:
            price_change: Absolute price change
            atr: Current ATR value
            
        Returns:
            Normalized price change (in ATR units)
        """
        if atr == 0:
            return 0
        
        return price_change / atr
    
    @staticmethod
    def get_regime_adjusted_multipliers(volatility_regime: str) -> Dict[str, float]:
        """
        Get threshold multipliers adjusted for current volatility regime
        
        Args:
            volatility_regime: 'low', 'normal', or 'high'
            
        Returns:
            Dict of adjusted multipliers for various thresholds
        """
        regime_adjustments = {
            'low': {
                'stop_loss': 1.5,        # Tighter stops in low volatility
                'take_profit': 2.0,
                'breakout_confirmation': 0.75,
                'significant_move': 1.0
            },
            'normal': {
                'stop_loss': 2.0,
                'take_profit': 3.0,
                'breakout_confirmation': 1.0,
                'significant_move': 1.5
            },
            'high': {
                'stop_loss': 3.0,        # Wider stops in high volatility
                'take_profit': 4.0,
                'breakout_confirmation': 1.5,
                'significant_move': 2.0
            }
        }
        
        return regime_adjustments.get(volatility_regime, regime_adjustments['normal'])
    
    @staticmethod
    def classify_volatility_regime(current_atr: float, 
                                 historical_atr: pd.Series,
                                 lookback: int = 50) -> str:
        """
        Classify current volatility regime based on ATR
        
        Args:
            current_atr: Current ATR value
            historical_atr: Historical ATR series
            lookback: Periods to consider for regime classification
            
        Returns:
            Volatility regime: 'low', 'normal', or 'high'
        """
        if len(historical_atr) < lookback:
            return 'normal'
        
        recent_atr = historical_atr.iloc[-lookback:]
        
        # Calculate percentiles
        low_threshold = np.percentile(recent_atr, 25)
        high_threshold = np.percentile(recent_atr, 75)
        
        if current_atr < low_threshold:
            return 'low'
        elif current_atr > high_threshold:
            return 'high'
        else:
            return 'normal'