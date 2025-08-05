# Keyword Requirements Analysis & Implementation Plan

## 📋 Client Requirements Overview

The client has provided 15 specific keyword definitions for cryptocurrency trend analysis. This document analyzes each requirement against our current implementation and provides recommendations for gaps.

## 🎯 Current Implementation Capabilities

### **Supported Query Types (8):**
1. **uptrend** - Basic trend analysis using linear regression
2. **downtrend** - Basic trend analysis using linear regression  
3. **sideways** - Trend analysis with minimal slope
4. **pump_and_dump** - Volume spike + rapid price increase + subsequent drop
5. **bottomed_out** - Recovery from sustained downtrend
6. **high_volatility** - Standard deviation analysis
7. **volume_spike** - Volume anomaly detection
8. **trending** - Activity-based trending
9. **performance** - Price change rankings

### **Current Database Schema:**
- `trend_analysis` table with timeframes: 1h, 24h, 7d, 30d
- `signal_events` table for specific market events
- Time-series price and volume data
- Statistical metadata storage (JSONB)

## 📊 Requirement Mapping Analysis

| # | Keyword | Current Status | Complexity | Implementation Priority |
|---|---------|----------------|------------|------------------------|
| 1 | **sideways trend** | ✅ **SUPPORTED** | Low | Already implemented |
| 2 | **parabolic rise** | ❌ **GAP** | Medium | ⭐ **HIGH** |
| 3 | **gradual uptrend** | 🟡 **PARTIAL** | Low | ⭐ **HIGH** |
| 4 | **multi-top resistance** | ❌ **MAJOR GAP** | High | 🔄 **FUTURE** |
| 5 | **breakout attempt** | ❌ **MAJOR GAP** | High | 🔄 **FUTURE** |
| 6 | **distribution phase** | ❌ **MAJOR GAP** | High | 🔄 **FUTURE** |
| 7 | **capitulation drop** | ❌ **GAP** | Medium | ⭐ **HIGH** |
| 8 | **dead cat bounce** | ❌ **MAJOR GAP** | High | 🔄 **FUTURE** |
| 9 | **bottoming out** | ✅ **SUPPORTED** | Low | Already implemented |
| 10 | **low-volume drift** | ❌ **GAP** | Medium | 🟡 **MEDIUM** |
| 11 | **pump and dump** | ✅ **SUPPORTED** | Low | Already implemented |
| 12 | **volatility spike** | ✅ **SUPPORTED** | Low | Already implemented |
| 13 | **reaccumulation range** | ❌ **MAJOR GAP** | High | 🔄 **FUTURE** |
| 14 | **failed breakout** | ❌ **MAJOR GAP** | High | 🔄 **FUTURE** |
| 15 | **macro downtrend** | 🟡 **PARTIAL** | Low | ⭐ **HIGH** |

## ✅ Already Supported (4 keywords)

### 1. **sideways trend** ✅
**Definition:** Price moves in narrow range (±10%) for 1-2 months
**Current Support:** `trend_type = 'sideways'` with low slope detection
**Status:** ✅ **FULLY SUPPORTED**

### 9. **bottoming out** ✅  
**Definition:** Stable base formation after decline
**Current Support:** `signal_type = 'bottomed_out'` with recovery detection
**Status:** ✅ **FULLY SUPPORTED**

### 11. **pump and dump** ✅
**Definition:** Rapid spike followed by sharp retracement
**Current Support:** `signal_type = 'pump_and_dump'` with volume analysis
**Status:** ✅ **FULLY SUPPORTED**

### 12. **volatility spike** ✅
**Definition:** Erratic large price swings
**Current Support:** `high_volatility` analysis with standard deviation
**Status:** ✅ **FULLY SUPPORTED**

## 🟡 Partially Supported (2 keywords)

### 3. **gradual uptrend** 🟡
**Definition:** Slow, steady increase with consistent volume
**Current Support:** `trend_type = 'uptrend'` (doesn't differentiate gradual vs parabolic)
**Gap:** Need to distinguish between gradual and parabolic uptrends
**Effort:** **LOW** - Add slope/acceleration analysis to existing trend detection

### 15. **macro downtrend** 🟡
**Definition:** Lower highs/lows over 2+ months
**Current Support:** `trend_type = 'downtrend'` (doesn't specify duration)
**Gap:** Need time-duration classification for macro vs short-term trends
**Effort:** **LOW** - Add duration analysis to existing trend detection

## ❌ High Priority Gaps (3 keywords)

### 2. **parabolic rise** ⭐
**Definition:** Exponential/steep price increase over days/weeks
**Implementation Needed:**
- New signal type: `parabolic_rise`
- Acceleration analysis (rate of rate change)
- Short timeframe detection (days/weeks)
**Complexity:** **MEDIUM** - Mathematical analysis of price acceleration
**Database Changes:** Add to `signal_type_enum`

### 7. **capitulation drop** ⭐
**Definition:** Sharp 20-50% decline with high volume
**Implementation Needed:**
- New signal type: `capitulation_drop`
- High-volume decline detection
- Percentage threshold analysis
**Complexity:** **MEDIUM** - Similar to pump detection but downward
**Database Changes:** Add to `signal_type_enum`

### 10. **low-volume drift** 🟡
**Definition:** Slow price movement with very low volume
**Implementation Needed:**
- New signal type: `low_volume_drift`
- Volume threshold analysis
- Extended timeframe monitoring
**Complexity:** **MEDIUM** - Volume pattern analysis
**Database Changes:** Add to `signal_type_enum`

## ❌ Complex Pattern Recognition (7 keywords) 🔄

These require sophisticated pattern recognition and are **beyond MVP scope**:

### 4. **multi-top resistance**
**Complexity:** **HIGH** - Requires peak detection, pattern matching
**Why Complex:** Need to identify repeated price levels over time periods

### 5. **breakout attempt**  
**Complexity:** **HIGH** - Requires support/resistance level detection
**Why Complex:** Need to define ranges and detect breakout attempts

### 6. **distribution phase**
**Complexity:** **HIGH** - Requires post-rally volume/price correlation analysis
**Why Complex:** Need to analyze selling patterns and volume distribution

### 8. **dead cat bounce**
**Complexity:** **HIGH** - Requires pattern sequence detection
**Why Complex:** Need to identify temporary recovery vs sustained reversal

### 13. **reaccumulation range**
**Complexity:** **HIGH** - Requires post-rise consolidation pattern detection
**Why Complex:** Need to identify accumulation patterns in price ranges

### 14. **failed breakout**
**Complexity:** **HIGH** - Requires breakout detection + failure analysis
**Why Complex:** Need to detect attempted breakouts and their subsequent failures

## 🎯 Implementation Recommendations

### **Phase 1: Enhance Existing (2 keywords)**
**Effort:** 1-2 days
**Scope:** Improve current trend analysis

1. **gradual uptrend** - Add slope analysis to differentiate from parabolic
2. **macro downtrend** - Add duration classification to existing downtrends

### **Phase 2: Add New Signals (3 keywords)**  
**Effort:** 1-2 weeks
**Scope:** New signal detection algorithms

1. **parabolic rise** - Acceleration-based detection
2. **capitulation drop** - High-volume decline detection  
3. **low-volume drift** - Volume threshold analysis

### **Phase 3: Complex Patterns (7 keywords)**
**Effort:** 2-3 months
**Scope:** Advanced pattern recognition (Future versions)

**Recommendation:** Defer to v2.0+ as these require:
- Advanced pattern recognition algorithms
- Historical pattern libraries
- Machine learning approaches
- Extensive testing and calibration

## 🗄️ Required Database Changes

### **⚠️ IMPORTANT:** See `docs/12-future-schema-requirements.md` for detailed analysis

### **Minor Changes for High Priority Items:**

```sql
-- Add new signal types to enum (NON-BREAKING)
ALTER TYPE signal_type_enum ADD VALUE 'parabolic_rise';
ALTER TYPE signal_type_enum ADD VALUE 'capitulation_drop';  
ALTER TYPE signal_type_enum ADD VALUE 'low_volume_drift';

-- Add trend duration classification to metadata (NO SCHEMA CHANGE)
-- Use existing JSONB metadata field
```

### **Major Changes for Complex Patterns:**
**Complex patterns require 5 new tables, 6 new enums, and significant schema redesign.**
**See detailed analysis in `docs/12-future-schema-requirements.md`**

### **Enhanced Query Parser Keywords:**

```javascript
// Add to query_parser.py intent patterns
'parabolic_rise': {
    'keywords': ['parabolic', 'exponential', 'rocket', 'moon', 'vertical'],
    'patterns': ['parabolic.{0,10}rise', 'exponential.{0,10}growth']
},
'capitulation_drop': {
    'keywords': ['capitulation', 'crash', 'panic', 'selloff', 'bloodbath'],
    'patterns': ['panic.{0,10}selling', 'capitulation']
},
'low_volume_drift': {
    'keywords': ['low.{0,10}volume', 'drift', 'quiet', 'stagnant'],
    'patterns': ['low.{0,10}volume.{0,10}drift']
}
```

## 📈 Coverage Summary

| **Implementation Level** | **Count** | **Percentage** | **Keywords** |
|-------------------------|-----------|----------------|--------------|
| ✅ **Fully Supported** | 4 | 27% | sideways, bottoming out, pump and dump, volatility spike |
| 🟡 **Quick Enhancements** | 2 | 13% | gradual uptrend, macro downtrend |
| ⭐ **High Priority Additions** | 3 | 20% | parabolic rise, capitulation drop, low-volume drift |
| 🔄 **Future Complex Features** | 7 | 47% | All pattern recognition features |

## 🎯 Recommended Approach

### **For MVP Launch:**
- ✅ **Use 4 existing keywords** (27% coverage)
- 🟡 **Add 2 quick enhancements** (40% total coverage)  
- ⭐ **Implement 1-2 high priority** (53-60% coverage)

### **For v2.0:**
- Implement remaining high priority features
- Begin research on pattern recognition algorithms
- Consider machine learning approaches for complex patterns

## 🚦 Risk Assessment

### **Low Risk (Recommended for MVP):**
- Enhancing existing trend analysis ✅
- Adding simple signal types ✅

### **Medium Risk:**
- New acceleration-based algorithms ⚠️
- Volume pattern analysis ⚠️

### **High Risk (Defer):**
- Complex pattern recognition ❌
- Multi-timeframe pattern correlation ❌
- Historical pattern matching ❌

## 💡 Client Communication Recommendations

**Suggested Response:**
"We can immediately support 4 of your 15 keywords (27%) with current implementation. With 1-2 weeks of development, we can enhance this to 9 keywords (60% coverage) by adding essential signal detection. The remaining 7 keywords require advanced pattern recognition suitable for v2.0, as they involve complex mathematical analysis beyond MVP scope." 