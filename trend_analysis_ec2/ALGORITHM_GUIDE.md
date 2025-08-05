# Trend Analysis Algorithm Guide

## Overview

The trend analysis system detects market patterns in cryptocurrency price data using statistical methods and pattern recognition. It analyzes both trends (directional movements) and signals (specific market events).

## Algorithm Components

### 1. Trend Analysis

#### **Purpose**: Identify directional price movements over different timeframes
#### **Timeframes**: 24h, 7d
#### **Method**: Linear regression with confidence scoring

#### **Process**:
1. **Data Filtering**: Select price data within the specified timeframe
2. **Linear Regression**: Calculate slope, R-squared, and statistical significance
3. **Trend Classification**: Categorize as uptrend, downtrend, or sideways
4. **Confidence Scoring**: Rate the reliability of the trend detection

#### **Variables**:
- `price_change_percent`: Total price change over the period
- `r_squared`: Coefficient of determination (0-1)
- `volatility`: Standard deviation / mean price
- `data_points`: Number of price observations used

#### **Thresholds**:
- **Sideways**: |price_change| < 1.0%
- **Uptrend**: price_change > 5.0%
- **Downtrend**: price_change < -5.0%
- **Confidence**: r_squared × (data_points / 10)

#### **Assumptions**:
- Price movements follow linear patterns over short periods
- More data points increase confidence
- Higher R-squared indicates stronger trend

### 2. Signal Detection

#### **Purpose**: Identify specific market events and anomalies
#### **Types**: 5 different signal categories
#### **Method**: Pattern recognition with statistical thresholds

## Signal Types

### **1. Pump and Dump Detection**

#### **Pattern**: Rapid price increase followed by sharp decline
#### **Time Window**: 24 hours (12h pump + 12h dump)
#### **Thresholds**:
- Pump: >30% price increase in 12 hours
- Dump: >20% price decrease after peak
- Minimum data: 24 price points

#### **Algorithm**:
```python
pump_window = prices[-24:-12]  # First 12 hours
dump_window = prices[-12:]      # Last 12 hours
pump_percent = (peak - start) / start * 100
dump_percent = (end - peak) / peak * 100
```

#### **Assumptions**:
- Pump and dump occurs within 24-hour window
- Clear separation between pump and dump phases
- Volume typically spikes during pump phase

### **2. Volume Anomaly Detection**

#### **Pattern**: Unusual trading volume spike
#### **Time Window**: 7 days (6 days baseline + 1 day spike)
#### **Thresholds**:
- Volume spike: >5x average volume
- Minimum data: 7 volume points

#### **Algorithm**:
```python
baseline_volume = mean(volumes[-7:-1])
spike_volume = volumes[-1]
spike_ratio = spike_volume / baseline_volume
```

#### **Assumptions**:
- Normal volume follows consistent patterns
- Volume spikes indicate significant market events
- 7-day baseline provides reliable average

### **3. Bottomed Out Detection**

#### **Pattern**: Recovery after prolonged downtrend
#### **Time Window**: 14 days (7 days downtrend + 7 days recovery)
#### **Thresholds**:
- Downtrend: >10% decline over 7 days
- Recovery: >8% increase over next 7 days
- Minimum data: 14 price points

#### **Algorithm**:
```python
downtrend = (week1_end - week1_start) / week1_start * 100
recovery = (week2_end - week2_start) / week2_start * 100
```

#### **Assumptions**:
- Bottoming out requires sustained downtrend
- Recovery must be significant (>8%)
- Pattern occurs over 2-week period

### **4. Parabolic Rise Detection**

#### **Pattern**: Exponential price growth
#### **Time Window**: 10 days
#### **Thresholds**:
- Accelerating price changes: ≥3 increasing changes
- Total rise: >50% over period
- Minimum data: 10 price points

#### **Algorithm**:
```python
price_changes = [daily_percent_changes]
increasing_changes = count(where change[i] > change[i-1])
total_rise = sum(price_changes)
```

#### **Assumptions**:
- Parabolic patterns show accelerating growth
- Exponential growth is unsustainable
- Multiple increasing changes indicate acceleration

### **5. Capitulation Drop Detection**

#### **Pattern**: Sharp drop after prolonged downtrend
#### **Time Window**: 14 days (7 days downtrend + 7 days sharp drop)
#### **Thresholds**:
- Downtrend: >15% decline over 7 days
- Sharp drop: >25% decline over next 7 days
- Minimum data: 14 price points

#### **Algorithm**:
```python
downtrend = (week1_end - week1_start) / week1_start * 100
sharp_drop = (week2_end - week2_start) / week2_start * 100
```

#### **Assumptions**:
- Capitulation follows sustained selling pressure
- Sharp drops indicate panic selling
- Pattern requires both sustained and sharp declines

## Data Requirements

### **Minimum Data Points**:
- **Trend Analysis**: 3+ price points per timeframe
- **Signal Detection**: 14+ price points (2 weeks)
- **Volume Analysis**: 7+ volume points

### **Data Quality**:
- Price data must be chronological
- Volume data must be non-zero
- Missing data points are skipped

## Confidence Scoring

### **Trend Confidence**:
```python
confidence = min(r_squared * (data_points / 10), 1.0)
```

### **Signal Confidence**:
- **Pump & Dump**: (pump_percent + |dump_percent|) / 100
- **Volume Anomaly**: spike_ratio / 10
- **Bottomed Out**: (|downtrend| + recovery) / 50
- **Parabolic Rise**: total_rise / 100
- **Capitulation**: (|downtrend| + |drop|) / 100

## Limitations and Assumptions

### **General Assumptions**:
1. **Market Efficiency**: Price movements reflect market sentiment
2. **Pattern Recognition**: Historical patterns repeat
3. **Statistical Validity**: Linear regression works for short timeframes
4. **Data Quality**: Price data is accurate and complete

### **Limitations**:
1. **False Positives**: Normal volatility may trigger signals
2. **Market Context**: Doesn't consider external factors
3. **Time Sensitivity**: Patterns may evolve over time
4. **Data Dependency**: Requires sufficient historical data

### **Risk Factors**:
1. **Market Conditions**: Bull/bear markets affect thresholds
2. **Volatility**: High volatility increases false signals
3. **Liquidity**: Low liquidity affects pattern reliability
4. **News Events**: External factors can invalidate patterns

## Performance Metrics

### **Success Indicators**:
- Signal variety (not just one type)
- Realistic confidence scores (0.3-0.8 range)
- Appropriate signal frequency (not too many/few)
- Correlation with actual market events

### **Quality Checks**:
- Signal distribution across cryptocurrencies
- Confidence score distribution
- False positive rate assessment
- Historical pattern validation

## Future Improvements

### **Potential Enhancements**:
1. **Machine Learning**: Train on historical signal accuracy
2. **Dynamic Thresholds**: Adjust based on market conditions
3. **Multi-timeframe Analysis**: Combine signals across timeframes
4. **Volume Analysis**: Incorporate volume patterns in all signals
5. **Market Context**: Consider broader market conditions 