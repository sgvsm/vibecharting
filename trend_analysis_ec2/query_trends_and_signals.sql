-- Query all trends and signals from the database
-- Run these queries to see the analysis results

-- ============================================================================
-- RECENT TRENDS (Last 24 hours)
-- ============================================================================
SELECT 
    c.symbol,
    c.name,
    ta.timeframe,
    ta.trend_type,
    ROUND(ta.confidence * 100, 2) as confidence_percent,
    ROUND(ta.price_change_percent, 2) as price_change_percent,
    ta.start_time,
    ta.end_time,
    ta.created_at
FROM trend_analysis ta
JOIN cryptocurrencies c ON ta.crypto_id = c.id
WHERE ta.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY ta.created_at DESC, c.symbol, ta.timeframe;

-- ============================================================================
-- RECENT SIGNALS (Last 24 hours)
-- ============================================================================
SELECT 
    c.symbol,
    c.name,
    se.signal_type,
    ROUND(se.confidence * 100, 2) as confidence_percent,
    se.trigger_price,
    se.volume_spike_ratio,
    se.detected_at,
    se.created_at
FROM signal_events se
JOIN cryptocurrencies c ON se.crypto_id = c.id
WHERE se.created_at >= NOW() - INTERVAL '24 hours'
ORDER BY se.created_at DESC, c.symbol;

-- ============================================================================
-- SUMMARY STATISTICS
-- ============================================================================
SELECT 
    'Trends' as type,
    COUNT(*) as total_count,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as last_7d
FROM trend_analysis
UNION ALL
SELECT 
    'Signals' as type,
    COUNT(*) as total_count,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '24 hours' THEN 1 END) as last_24h,
    COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as last_7d
FROM signal_events;

-- ============================================================================
-- TREND BREAKDOWN BY TYPE
-- ============================================================================
SELECT 
    trend_type,
    timeframe,
    COUNT(*) as count,
    ROUND(AVG(confidence) * 100, 2) as avg_confidence,
    ROUND(AVG(price_change_percent), 2) as avg_price_change
FROM trend_analysis
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY trend_type, timeframe
ORDER BY count DESC;

-- ============================================================================
-- SIGNAL BREAKDOWN BY TYPE
-- ============================================================================
SELECT 
    signal_type,
    COUNT(*) as count,
    ROUND(AVG(confidence) * 100, 2) as avg_confidence,
    ROUND(AVG(volume_spike_ratio), 2) as avg_volume_spike
FROM signal_events
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY signal_type
ORDER BY count DESC;

-- ============================================================================
-- TOP PERFORMING CRYPTOCURRENCIES (by trend confidence)
-- ============================================================================
SELECT 
    c.symbol,
    c.name,
    COUNT(ta.id) as trend_count,
    ROUND(AVG(ta.confidence) * 100, 2) as avg_confidence,
    ROUND(AVG(ta.price_change_percent), 2) as avg_price_change
FROM cryptocurrencies c
LEFT JOIN trend_analysis ta ON c.id = ta.crypto_id
WHERE ta.created_at >= NOW() - INTERVAL '7 days'
GROUP BY c.id, c.symbol, c.name
HAVING COUNT(ta.id) > 0
ORDER BY avg_confidence DESC
LIMIT 10;

-- ============================================================================
-- MOST ACTIVE SIGNAL CRYPTOCURRENCIES
-- ============================================================================
SELECT 
    c.symbol,
    c.name,
    COUNT(se.id) as signal_count,
    STRING_AGG(DISTINCT se.signal_type, ', ') as signal_types
FROM cryptocurrencies c
LEFT JOIN signal_events se ON c.id = se.crypto_id
WHERE se.created_at >= NOW() - INTERVAL '7 days'
GROUP BY c.id, c.symbol, c.name
HAVING COUNT(se.id) > 0
ORDER BY signal_count DESC
LIMIT 10; 