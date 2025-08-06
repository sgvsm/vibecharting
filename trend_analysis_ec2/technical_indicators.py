#!/usr/bin/env python3
"""
Technical Indicators Module
Provides wrapper functions for calculating standard technical indicators
using pandas-ta library.
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone


class TechnicalIndicators:
    """Calculate technical indicators for cryptocurrency price data"""
    
    @staticmethod
    def prepare_dataframe(price_data: List[Dict]) -> pd.DataFrame:
        """Convert price data to pandas DataFrame with proper indexing"""
        if not price_data:
            return pd.DataFrame()
        
        # Create DataFrame from price data
        df = pd.DataFrame(price_data)
        
        # Ensure we have the required columns
        if 'close' not in df.columns and 'price_usd' in df.columns:
            df['close'] = df['price_usd']
        
        # Set timestamp as index
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df.set_index('timestamp', inplace=True)
        df.sort_index(inplace=True)
        
        # Add OHLC data if not present (use close price as approximation)
        if 'open' not in df.columns:
            df['open'] = df['close']
        if 'high' not in df.columns:
            df['high'] = df['close']
        if 'low' not in df.columns:
            df['low'] = df['close']
        
        # Ensure volume column exists
        if 'volume' not in df.columns and 'volume_24h' in df.columns:
            df['volume'] = df['volume_24h']
        
        return df
    
    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int = 50) -> pd.Series:
        """Calculate Simple Moving Average"""
        return ta.sma(df['close'], length=period)
    
    @staticmethod
    def calculate_ema(df: pd.DataFrame, period: int = 50) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return ta.ema(df['close'], length=period)
    
    @staticmethod
    def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        Returns DataFrame with MACD, Signal, and Histogram columns
        """
        return ta.macd(df['close'], fast=fast, slow=slow, signal=signal)
    
    @staticmethod
    def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std: float = 2.0) -> pd.DataFrame:
        """
        Calculate Bollinger Bands
        Returns DataFrame with Lower, Middle, Upper bands and Bandwidth
        """
        return ta.bbands(df['close'], length=period, std=std)
    
    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        return ta.rsi(df['close'], length=period)
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range (requires OHLC data)"""
        return ta.atr(df['high'], df['low'], df['close'], length=period)
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average Directional Index (requires OHLC data)"""
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=period)
        return adx_df[f'ADX_{period}'] if f'ADX_{period}' in adx_df.columns else None
    
    @staticmethod
    def detect_ma_crossover(fast_ma: pd.Series, slow_ma: pd.Series) -> Dict[str, List[datetime]]:
        """
        Detect Moving Average crossovers
        Returns dict with 'golden_cross' and 'death_cross' timestamps
        """
        crossovers = {'golden_cross': [], 'death_cross': []}
        
        # Ensure we have valid data
        if fast_ma is None or slow_ma is None or len(fast_ma) < 2:
            return crossovers
        
        # Calculate crossover points
        fast_above = fast_ma > slow_ma
        
        for i in range(1, len(fast_above)):
            # Golden Cross: fast MA crosses above slow MA
            if not fast_above.iloc[i-1] and fast_above.iloc[i]:
                crossovers['golden_cross'].append(fast_above.index[i])
            # Death Cross: fast MA crosses below slow MA
            elif fast_above.iloc[i-1] and not fast_above.iloc[i]:
                crossovers['death_cross'].append(fast_above.index[i])
        
        return crossovers
    
    @staticmethod
    def detect_macd_signals(macd_df: pd.DataFrame) -> Dict[str, List[Tuple[datetime, float]]]:
        """
        Detect MACD crossover signals
        Returns dict with 'bullish' and 'bearish' signal timestamps and histogram values
        """
        signals = {'bullish': [], 'bearish': []}
        
        if macd_df is None or len(macd_df) < 2:
            return signals
        
        # Get MACD line and Signal line column names
        macd_col = [col for col in macd_df.columns if 'MACD_' in col and 'MACDs_' not in col][0]
        signal_col = [col for col in macd_df.columns if 'MACDs_' in col][0]
        histogram_col = [col for col in macd_df.columns if 'MACDh_' in col][0]
        
        macd_line = macd_df[macd_col]
        signal_line = macd_df[signal_col]
        histogram = macd_df[histogram_col]
        
        # Find crossovers
        macd_above = macd_line > signal_line
        
        for i in range(1, len(macd_above)):
            # Bullish signal: MACD crosses above Signal
            if not macd_above.iloc[i-1] and macd_above.iloc[i]:
                signals['bullish'].append((macd_above.index[i], histogram.iloc[i]))
            # Bearish signal: MACD crosses below Signal
            elif macd_above.iloc[i-1] and not macd_above.iloc[i]:
                signals['bearish'].append((macd_above.index[i], histogram.iloc[i]))
        
        return signals
    
    @staticmethod
    def detect_bollinger_signals(bb_df: pd.DataFrame, price_series: pd.Series, 
                               squeeze_threshold: float = 0.05) -> Dict[str, List[Tuple[datetime, float]]]:
        """
        Detect Bollinger Band signals
        Returns dict with various BB signals and their timestamps
        """
        signals = {
            'squeeze_breakout': [],
            'upper_band_touch': [],
            'lower_band_touch': [],
            'band_expansion': []
        }
        
        if bb_df is None or len(bb_df) < 20:
            return signals
        
        # Get column names
        lower_col = [col for col in bb_df.columns if 'BBL_' in col][0]
        middle_col = [col for col in bb_df.columns if 'BBM_' in col][0]
        upper_col = [col for col in bb_df.columns if 'BBU_' in col][0]
        bandwidth_col = [col for col in bb_df.columns if 'BBB_' in col][0]
        
        lower_band = bb_df[lower_col]
        middle_band = bb_df[middle_col]
        upper_band = bb_df[upper_col]
        bandwidth = bb_df[bandwidth_col]
        
        # Calculate bandwidth percentile for squeeze detection
        bandwidth_percentile = bandwidth.rolling(window=100, min_periods=20).apply(
            lambda x: np.percentile(x, 10)
        )
        
        for i in range(1, len(price_series)):
            timestamp = price_series.index[i]
            
            # Squeeze breakout detection
            if i > 20 and bandwidth.iloc[i-1] <= bandwidth_percentile.iloc[i-1] and \
               bandwidth.iloc[i] > bandwidth_percentile.iloc[i]:
                signals['squeeze_breakout'].append((timestamp, bandwidth.iloc[i]))
            
            # Band touches
            if price_series.iloc[i] >= upper_band.iloc[i] and \
               price_series.iloc[i-1] < upper_band.iloc[i-1]:
                signals['upper_band_touch'].append((timestamp, price_series.iloc[i]))
            
            if price_series.iloc[i] <= lower_band.iloc[i] and \
               price_series.iloc[i-1] > lower_band.iloc[i-1]:
                signals['lower_band_touch'].append((timestamp, price_series.iloc[i]))
        
        return signals
    
    @staticmethod
    def detect_rsi_signals(rsi: pd.Series, overbought: float = 70, oversold: float = 30) -> Dict[str, List[Tuple[datetime, float]]]:
        """
        Detect RSI signals
        Returns dict with overbought/oversold signals
        """
        signals = {
            'overbought_entry': [],
            'overbought_exit': [],
            'oversold_entry': [],
            'oversold_exit': []
        }
        
        if rsi is None or len(rsi) < 2:
            return signals
        
        for i in range(1, len(rsi)):
            timestamp = rsi.index[i]
            
            # Overbought signals
            if rsi.iloc[i] > overbought and rsi.iloc[i-1] <= overbought:
                signals['overbought_entry'].append((timestamp, rsi.iloc[i]))
            elif rsi.iloc[i] <= overbought and rsi.iloc[i-1] > overbought:
                signals['overbought_exit'].append((timestamp, rsi.iloc[i]))
            
            # Oversold signals
            if rsi.iloc[i] < oversold and rsi.iloc[i-1] >= oversold:
                signals['oversold_entry'].append((timestamp, rsi.iloc[i]))
            elif rsi.iloc[i] >= oversold and rsi.iloc[i-1] < oversold:
                signals['oversold_exit'].append((timestamp, rsi.iloc[i]))
        
        return signals
    
    @staticmethod
    def calculate_dynamic_rsi_thresholds(rsi: pd.Series, lookback: int = 200) -> Tuple[float, float]:
        """
        Calculate dynamic overbought/oversold thresholds based on historical RSI distribution
        Returns (oversold_threshold, overbought_threshold)
        """
        if rsi is None or len(rsi) < lookback:
            return 30.0, 70.0  # Default values
        
        # Use the last 'lookback' periods
        recent_rsi = rsi.iloc[-lookback:]
        
        # Calculate 15th and 85th percentiles
        oversold_threshold = np.percentile(recent_rsi.dropna(), 15)
        overbought_threshold = np.percentile(recent_rsi.dropna(), 85)
        
        return oversold_threshold, overbought_threshold