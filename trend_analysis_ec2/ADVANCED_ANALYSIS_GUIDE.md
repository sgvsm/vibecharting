# Advanced Technical Analysis Guide

## Overview

The trend analysis system now supports two modes:
- **Legacy Mode**: Original linear regression-based analysis
- **Advanced Mode**: Industry-standard technical indicators

## Running the Analysis

### Basic Usage

```bash
# Run with advanced mode (default)
python run_trend_analysis.py

# Run with legacy mode
python run_trend_analysis.py --mode legacy

# Run with debug logging
python run_trend_analysis.py --debug
```

### Prerequisites

For advanced mode, install additional dependencies:

```bash
pip install -r requirements.txt
```

## Technical Indicators Used

### 1. Moving Averages (MA)
- **SMA (Simple Moving Average)**: 50 and 200 period for trend detection
- **EMA (Exponential Moving Average)**: 20 period for short-term momentum
- **Signals**: Golden Cross (50 SMA > 200 SMA), Death Cross (50 SMA < 200 SMA)

### 2. MACD (Moving Average Convergence Divergence)
- **Components**: MACD Line (12 EMA - 26 EMA), Signal Line (9 EMA of MACD)
- **Signals**: Bullish (MACD crosses above Signal), Bearish (MACD crosses below Signal)

### 3. Bollinger Bands (BB)
- **Components**: Middle (20 SMA), Upper/Lower (±2 standard deviations)
- **Signals**: Squeeze breakouts, Band touches

### 4. RSI (Relative Strength Index)
- **Period**: 14
- **Dynamic Thresholds**: Adapts to each asset's historical RSI distribution
- **Signals**: Oversold exit (potential buy), Overbought exit (potential sell)

### 5. ADX (Average Directional Index)
- **Purpose**: Measures trend strength (not direction)
- **Usage**: Confidence scoring, trend validation

### 6. ATR (Average True Range)
- **Purpose**: Volatility measurement
- **Usage**: Dynamic threshold calculation, position sizing

## Confidence Scoring Model

The new multi-factor confidence model weighs:

1. **Trend Strength (40%)**: Based on ADX value
   - ADX < 20: Weak/no trend (low confidence)
   - ADX 20-25: Developing trend
   - ADX 25-40: Strong trend
   - ADX > 40: Very strong trend

2. **Momentum Confirmation (30%)**: Based on MACD histogram
   - Percentile-based scoring
   - Higher magnitude = higher confidence

3. **Volatility Context (20%)**: Based on Bollinger Bandwidth
   - For breakouts: Lower bandwidth = higher confidence
   - For other signals: Moderate volatility preferred

4. **Statistical Noise Filter (10%)**: Short-term regression p-value
   - Filters out purely random movements

## Adaptive Thresholds

Unlike the legacy system's fixed thresholds, the advanced mode uses:

- **ATR-based thresholds**: Normalized for each asset's volatility
- **Percentile-based levels**: Dynamic RSI overbought/oversold
- **Historical context**: Thresholds adapt to recent market behavior

## Database Schema Updates

New migrations added:
- `012_add_technical_indicator_signals.sql`: New signal types
- `013_add_ohlc_data.sql`: OHLC support (future enhancement)

## Signal Types Comparison

| Legacy Signals | Advanced Signals | Description |
|---------------|------------------|-------------|
| pump_and_dump | - | Retained for backward compatibility |
| volume_anomaly | - | Retained for backward compatibility |
| bottomed_out | - | Retained for backward compatibility |
| - | macd_bullish | MACD line crosses above signal line |
| - | macd_bearish | MACD line crosses below signal line |
| - | bollinger_breakout | Price breaks out of Bollinger squeeze |
| - | rsi_oversold | RSI exits oversold territory |
| - | rsi_overbought | RSI exits overbought territory |
| - | golden_cross | 50 SMA crosses above 200 SMA |
| - | death_cross | 50 SMA crosses below 200 SMA |

## Metadata Storage

All indicator values and confidence components are stored in the metadata JSON field:

```json
{
  "analysis_mode": "advanced",
  "sma_50": 45000.25,
  "ema_20": 44500.50,
  "adx": 28.5,
  "atr": 1250.75,
  "confidence_components": {
    "trend_strength": 0.65,
    "momentum_confirmation": 0.80,
    "volatility_context": 0.70,
    "statistical_noise": 0.60,
    "overall_confidence": 0.695
  }
}
```

## Performance Considerations

- Advanced mode requires more computation but provides better signals
- Minimum 50 data points required for reliable indicator calculation
- 200+ data points recommended for moving average crossovers
- pandas-ta is optimized for vectorized calculations

## Future Enhancements

1. **OHLC Data Integration**: Full candlestick pattern recognition
2. **Volume-Weighted Indicators**: VWAP, OBV integration
3. **Machine Learning Layer**: Signal validation using historical performance
4. **Multi-Timeframe Analysis**: Confluence across different periods
5. **Risk Management Integration**: Position sizing based on confidence