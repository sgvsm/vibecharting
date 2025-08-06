#!/usr/bin/env python3
"""
Multi-Factor Confidence Model
Implements a sophisticated confidence scoring system based on multiple technical factors
"""

import numpy as np
from typing import Dict, Optional
from scipy import stats


class ConfidenceModel:
    """Calculate multi-factor confidence scores for trading signals"""
    
    # Component weights for the confidence model
    WEIGHTS = {
        'trend_strength': 0.40,      # ADX-based trend strength
        'momentum_confirmation': 0.30, # MACD histogram magnitude
        'volatility_context': 0.20,   # Bollinger Bandwidth context
        'statistical_noise': 0.10     # Short-term regression p-value
    }
    
    @classmethod
    def calculate_confidence(cls, 
                           adx_value: Optional[float] = None,
                           macd_histogram: Optional[float] = None,
                           macd_histogram_percentile: Optional[float] = None,
                           bollinger_bandwidth_percentile: Optional[float] = None,
                           recent_price_pvalue: Optional[float] = None,
                           signal_type: Optional[str] = None) -> Dict[str, float]:
        """
        Calculate overall confidence score and component scores
        
        Args:
            adx_value: Current ADX value (0-100)
            macd_histogram: Current MACD histogram value
            macd_histogram_percentile: Percentile of current histogram in historical context (0-100)
            bollinger_bandwidth_percentile: Current bandwidth as percentile of historical (0-100)
            recent_price_pvalue: P-value from short-term linear regression
            signal_type: Type of signal for context-specific adjustments
            
        Returns:
            Dict with 'overall_confidence' and individual component scores
        """
        scores = {}
        
        # 1. Trend Strength Score (based on ADX)
        if adx_value is not None:
            if adx_value < 20:
                trend_score = 0.0  # Weak or no trend
            elif adx_value < 25:
                trend_score = 0.25  # Developing trend
            elif adx_value < 40:
                trend_score = 0.50 + (adx_value - 25) / 30  # Strong trend
            else:
                trend_score = 1.0  # Very strong trend
        else:
            trend_score = 0.5  # Neutral if no ADX data
        
        scores['trend_strength'] = trend_score
        
        # 2. Momentum Confirmation Score (based on MACD histogram)
        if macd_histogram_percentile is not None:
            # Strong momentum if histogram is in top/bottom 20%
            if macd_histogram_percentile > 80 or macd_histogram_percentile < 20:
                momentum_score = 0.9
            elif macd_histogram_percentile > 70 or macd_histogram_percentile < 30:
                momentum_score = 0.7
            elif macd_histogram_percentile > 60 or macd_histogram_percentile < 40:
                momentum_score = 0.5
            else:
                momentum_score = 0.3  # Weak momentum
        else:
            momentum_score = 0.5  # Neutral if no MACD data
        
        scores['momentum_confirmation'] = momentum_score
        
        # 3. Volatility Context Score (based on Bollinger Bandwidth)
        if bollinger_bandwidth_percentile is not None:
            if signal_type in ['squeeze_breakout', 'bollinger_breakout']:
                # For breakout signals, low bandwidth (squeeze) is favorable
                if bollinger_bandwidth_percentile < 10:
                    volatility_score = 1.0  # Extreme squeeze
                elif bollinger_bandwidth_percentile < 25:
                    volatility_score = 0.8  # Moderate squeeze
                elif bollinger_bandwidth_percentile < 50:
                    volatility_score = 0.5
                else:
                    volatility_score = 0.3  # No squeeze
            else:
                # For other signals, moderate volatility is favorable
                if 30 <= bollinger_bandwidth_percentile <= 70:
                    volatility_score = 0.8  # Optimal volatility range
                elif 20 <= bollinger_bandwidth_percentile <= 80:
                    volatility_score = 0.6
                else:
                    volatility_score = 0.4  # Extreme volatility
        else:
            volatility_score = 0.5  # Neutral if no BB data
        
        scores['volatility_context'] = volatility_score
        
        # 4. Statistical Noise Filter Score
        if recent_price_pvalue is not None:
            if recent_price_pvalue < 0.01:
                noise_score = 1.0  # Very significant
            elif recent_price_pvalue < 0.05:
                noise_score = 0.8  # Significant
            elif recent_price_pvalue < 0.10:
                noise_score = 0.6  # Marginally significant
            elif recent_price_pvalue < 0.20:
                noise_score = 0.4
            else:
                noise_score = 0.2  # Likely noise
        else:
            noise_score = 0.5  # Neutral if no p-value
        
        scores['statistical_noise'] = noise_score
        
        # Calculate weighted overall confidence
        overall_confidence = (
            cls.WEIGHTS['trend_strength'] * scores['trend_strength'] +
            cls.WEIGHTS['momentum_confirmation'] * scores['momentum_confirmation'] +
            cls.WEIGHTS['volatility_context'] * scores['volatility_context'] +
            cls.WEIGHTS['statistical_noise'] * scores['statistical_noise']
        )
        
        # Apply signal-specific adjustments
        if signal_type:
            overall_confidence = cls._apply_signal_adjustments(overall_confidence, signal_type, scores)
        
        # Ensure confidence is in valid range [0, 1]
        overall_confidence = max(0.0, min(1.0, overall_confidence))
        
        scores['overall_confidence'] = overall_confidence
        
        return scores
    
    @staticmethod
    def _apply_signal_adjustments(base_confidence: float, signal_type: str, 
                                 component_scores: Dict[str, float]) -> float:
        """Apply signal-specific confidence adjustments"""
        
        # Golden/Death Cross signals get bonus for strong trend alignment
        if signal_type in ['golden_cross', 'death_cross']:
            if component_scores['trend_strength'] > 0.7:
                base_confidence *= 1.1  # 10% bonus for strong trend
        
        # MACD signals get penalty if momentum is weak
        elif signal_type in ['macd_bullish', 'macd_bearish']:
            if component_scores['momentum_confirmation'] < 0.3:
                base_confidence *= 0.8  # 20% penalty for weak momentum
        
        # RSI signals in ranging markets (low ADX) get penalty
        elif signal_type in ['rsi_oversold', 'rsi_overbought']:
            if component_scores['trend_strength'] < 0.3:
                base_confidence *= 0.7  # 30% penalty in ranging market
        
        return base_confidence
    
    @staticmethod
    def calculate_short_term_pvalue(prices: list, window: int = 5) -> Optional[float]:
        """
        Calculate p-value from short-term linear regression
        Used as a noise filter
        """
        if len(prices) < window:
            return None
        
        # Use last 'window' prices
        recent_prices = prices[-window:]
        x = range(len(recent_prices))
        
        try:
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, recent_prices)
            return p_value
        except:
            return None
    
    @staticmethod
    def calculate_histogram_percentile(current_value: float, historical_values: list) -> Optional[float]:
        """
        Calculate where current value falls in historical distribution
        Returns percentile (0-100)
        """
        if not historical_values or len(historical_values) < 20:
            return None
        
        # Calculate percentile
        percentile = stats.percentileofscore(historical_values, current_value)
        return percentile