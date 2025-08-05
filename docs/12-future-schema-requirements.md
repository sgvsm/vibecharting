# Future Schema Requirements Analysis

## ⚠️ CORRECTION TO PREVIOUS ASSESSMENT

**I initially underestimated the schema changes needed.** Here's the accurate analysis of database schema requirements for implementing the remaining client keywords.

## 📊 Schema Change Requirements by Priority

### **🟡 Quick Enhancements (2 keywords)**

#### **gradual uptrend** vs **parabolic rise**
**Current:** `trend_type_enum AS ENUM ('uptrend', 'downtrend', 'sideways')`

**Options:**
- **Option A:** Modify enum ❌ **BREAKING CHANGE**
```sql
-- Would break existing data
ALTER TYPE trend_type_enum ADD VALUE 'gradual_uptrend';
ALTER TYPE trend_type_enum ADD VALUE 'parabolic_uptrend';
-- Remove 'uptrend' (IMPOSSIBLE without recreating enum)
```

- **Option B:** Use metadata ✅ **NO SCHEMA CHANGE**
```sql
-- Store subtype in existing metadata JSONB
metadata: {
  "trend_subtype": "gradual|parabolic",
  "slope_classification": "steep|moderate|gentle"
}
```

#### **macro downtrend** 
**Similar Options:**
- **Option A:** Enum modification ❌ **BREAKING CHANGE**
- **Option B:** Metadata classification ✅ **NO SCHEMA CHANGE**

**Recommendation:** Use metadata approach to avoid breaking changes.

### **⭐ High Priority Additions (3 keywords)**

#### **New Signal Types Required:**
```sql
-- SCHEMA CHANGES NEEDED:
ALTER TYPE signal_type_enum ADD VALUE 'parabolic_rise';
ALTER TYPE signal_type_enum ADD VALUE 'capitulation_drop';  
ALTER TYPE signal_type_enum ADD VALUE 'low_volume_drift';
```

**Impact:** ✅ **NON-BREAKING** - Adding enum values is safe

### **🔄 Complex Patterns (7 keywords) - MAJOR SCHEMA CHANGES**

#### **1. multi-top resistance**
**Requirements:**
- Track multiple price peaks at similar levels
- Store resistance level and breach attempts
- Historical peak data

**Schema Needs:**
```sql
-- NEW TABLE REQUIRED
CREATE TABLE support_resistance_levels (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    level_type ENUM ('support', 'resistance'),
    price_level DECIMAL(20, 8) NOT NULL,
    strength INTEGER, -- Number of times tested
    first_detected TIMESTAMP WITH TIME ZONE,
    last_tested TIMESTAMP WITH TIME ZONE,
    status ENUM ('active', 'broken', 'confirmed'),
    metadata JSONB
);

-- Link to existing signal_events
ALTER TABLE signal_events 
ADD COLUMN resistance_level_id INTEGER REFERENCES support_resistance_levels(id);
```

#### **2. breakout attempt** & **14. failed breakout**
**Requirements:**
- Track range boundaries
- Breakout attempts and outcomes
- Relationship between attempt and result

**Schema Needs:**
```sql
-- NEW TABLE REQUIRED  
CREATE TABLE price_ranges (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    range_type ENUM ('consolidation', 'accumulation', 'distribution'),
    support_level DECIMAL(20, 8),
    resistance_level DECIMAL(20, 8),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    volume_profile JSONB,
    status ENUM ('active', 'broken_up', 'broken_down'),
    metadata JSONB
);

-- Link breakout attempts to ranges
ALTER TABLE signal_events 
ADD COLUMN range_id INTEGER REFERENCES price_ranges(id),
ADD COLUMN breakout_direction ENUM ('up', 'down'),
ADD COLUMN breakout_success BOOLEAN;
```

#### **3. distribution phase** & **13. reaccumulation range**
**Requirements:**
- Track post-rally consolidation phases
- Volume distribution analysis
- Phase classification

**Schema Needs:**
```sql
-- NEW TABLE REQUIRED
CREATE TABLE market_phases (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    phase_type ENUM ('accumulation', 'markup', 'distribution', 'markdown', 'reaccumulation'),
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    price_range_start DECIMAL(20, 8),
    price_range_end DECIMAL(20, 8),
    volume_characteristics JSONB,
    preceding_trend_id INTEGER REFERENCES trend_analysis(id),
    confidence DECIMAL(5, 4),
    metadata JSONB
);
```

#### **4. dead cat bounce**
**Requirements:**
- Track sequence of related events
- Link original decline → bounce → continuation
- Pattern relationship detection

**Schema Needs:**
```sql
-- NEW TABLE REQUIRED
CREATE TABLE pattern_sequences (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    pattern_type ENUM ('dead_cat_bounce', 'double_bottom', 'head_shoulders'),
    sequence_start TIMESTAMP WITH TIME ZONE,
    sequence_end TIMESTAMP WITH TIME ZONE,
    confidence DECIMAL(5, 4),
    metadata JSONB
);

-- Link individual signals to patterns
CREATE TABLE pattern_signal_links (
    pattern_id INTEGER REFERENCES pattern_sequences(id),
    signal_id INTEGER REFERENCES signal_events(id),
    sequence_position INTEGER,
    role_in_pattern VARCHAR(50), -- 'decline', 'bounce', 'continuation'
    PRIMARY KEY (pattern_id, signal_id)
);
```

#### **5. low-volume drift**
**Already covered in high priority** - just needs new signal type

## 📋 Complete Schema Change Summary

### **✅ NO SCHEMA CHANGES (Can Use Metadata)**
- **gradual uptrend** classification
- **macro downtrend** duration analysis

### **🟡 MINOR SCHEMA CHANGES (Enum Additions)**
- **parabolic rise** signal type
- **capitulation drop** signal type  
- **low-volume drift** signal type

### **🚨 MAJOR SCHEMA CHANGES (New Tables + Relationships)**
- **multi-top resistance** → Support/resistance levels table
- **breakout attempt** → Price ranges table + signal relationships
- **distribution phase** → Market phases table
- **dead cat bounce** → Pattern sequences + linking tables
- **reaccumulation range** → Market phases table
- **failed breakout** → Price ranges + breakout tracking

## 🏗️ New Schema Components Required

### **4 New Tables Needed:**
1. `support_resistance_levels` - Track price levels and strength
2. `price_ranges` - Track consolidation ranges and breakouts
3. `market_phases` - Track accumulation/distribution phases
4. `pattern_sequences` - Track multi-event patterns
5. `pattern_signal_links` - Link signals to patterns (junction table)

### **Schema Relationships:**
```sql
-- New foreign key relationships
signal_events → support_resistance_levels (many-to-one)
signal_events → price_ranges (many-to-one)  
signal_events → pattern_sequences (many-to-many via linking table)
market_phases → trend_analysis (one-to-one for preceding trend)
```

### **New Enums Needed:**
```sql
CREATE TYPE level_type_enum AS ENUM ('support', 'resistance');
CREATE TYPE range_type_enum AS ENUM ('consolidation', 'accumulation', 'distribution');
CREATE TYPE range_status_enum AS ENUM ('active', 'broken_up', 'broken_down');
CREATE TYPE phase_type_enum AS ENUM ('accumulation', 'markup', 'distribution', 'markdown', 'reaccumulation');
CREATE TYPE pattern_type_enum AS ENUM ('dead_cat_bounce', 'double_bottom', 'head_shoulders');
CREATE TYPE breakout_direction_enum AS ENUM ('up', 'down');
```

## 🎯 Implementation Complexity

### **Phase 1: Minor Changes (1-2 days)**
- Add 3 new signal types to enum
- Use metadata for trend subtypes

### **Phase 2: Major Restructure (2-4 weeks)**
- Design and implement 5 new tables
- Create migration scripts for relationships
- Update all Lambda functions for new schema
- Handle data migration complexities

### **Phase 3: Algorithm Development (1-2 months)**
- Implement pattern recognition algorithms
- Build relationship detection logic
- Create pattern sequence analyzers

## ⚠️ **CORRECTED CONCLUSION**

**I was wrong in my initial assessment.** The complex pattern keywords require **significant schema changes** including:

- **5 new tables**
- **6 new enums** 
- **Multiple foreign key relationships**
- **Complex junction tables**

This is **NOT** a minor enhancement - it's a major database redesign that would require careful planning and migration strategy.

## 💡 **Revised Recommendation**

1. **For MVP:** Stick with current schema + 3 new signal types (minor enum additions)
2. **For v2.0:** Plan major schema redesign with proper migration strategy
3. **Consider:** Whether complex patterns justify the development complexity

The current MVP schema is **perfect for the immediate launch** and the 4 supported keywords. The complex patterns are genuinely v2.0+ features requiring significant architectural changes. 