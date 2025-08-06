-- Export Trend Analysis to CSV
\copy (
    SELECT 
        c.symbol,
        c.name,
        ta.timeframe,
        ta.trend_type,
        ta.confidence,
        ta.price_change_percent,
        ta.start_time,
        ta.end_time,
        ta.metadata,
        ta.created_at
    FROM trend_analysis ta
    JOIN cryptocurrencies c ON ta.crypto_id = c.id
    ORDER BY ta.created_at DESC, c.symbol
) TO '/home/ec2-user/trend_analysis_export.csv' WITH CSV HEADER;

-- Export Signal Events to CSV
\copy (
    SELECT 
        c.symbol,
        c.name,
        se.signal_type,
        se.confidence,
        se.trigger_price,
        se.volume_spike_ratio,
        se.detected_at,
        se.metadata,
        se.created_at
    FROM signal_events se
    JOIN cryptocurrencies c ON se.crypto_id = c.id
    ORDER BY se.created_at DESC, c.symbol
) TO '/home/ec2-user/signal_events_export.csv' WITH CSV HEADER;