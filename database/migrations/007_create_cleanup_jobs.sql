-- Migration: Create cleanup jobs and functions
-- File: 007_create_cleanup_jobs.sql
-- Purpose: Create functions for automated data retention cleanup

-- Function to clean up old price data (older than 1 year)
CREATE OR REPLACE FUNCTION cleanup_old_price_data()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM price_data 
    WHERE timestamp < NOW() - INTERVAL '1 year';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup operation
    INSERT INTO analysis_runs (run_type, status, started_at, completed_at, records_processed, notes)
    VALUES ('data_cleanup_price', 'completed', NOW(), NOW(), deleted_count, 
            'Cleaned up price data older than 1 year');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old trend analysis (older than 6 months)
CREATE OR REPLACE FUNCTION cleanup_old_trend_analysis()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM trend_analysis 
    WHERE created_at < NOW() - INTERVAL '6 months';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup operation
    INSERT INTO analysis_runs (run_type, status, started_at, completed_at, records_processed, notes)
    VALUES ('data_cleanup_trends', 'completed', NOW(), NOW(), deleted_count, 
            'Cleaned up trend analysis older than 6 months');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old signal events (older than 3 months)
CREATE OR REPLACE FUNCTION cleanup_old_signal_events()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM signal_events 
    WHERE detected_at < NOW() - INTERVAL '3 months';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup operation
    INSERT INTO analysis_runs (run_type, status, started_at, completed_at, records_processed, notes)
    VALUES ('data_cleanup_signals', 'completed', NOW(), NOW(), deleted_count, 
            'Cleaned up signal events older than 3 months');
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old analysis runs (older than 1 year)
CREATE OR REPLACE FUNCTION cleanup_old_analysis_runs()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM analysis_runs 
    WHERE started_at < NOW() - INTERVAL '1 year';
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Master cleanup function that runs all cleanup jobs
CREATE OR REPLACE FUNCTION run_data_cleanup()
RETURNS TABLE(
    job_name TEXT,
    records_deleted INTEGER,
    execution_time INTERVAL
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    price_deleted INTEGER;
    trend_deleted INTEGER;
    signal_deleted INTEGER;
    runs_deleted INTEGER;
BEGIN
    -- Clean up price data
    start_time := NOW();
    SELECT cleanup_old_price_data() INTO price_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'price_data'::TEXT, price_deleted, (end_time - start_time);
    
    -- Clean up trend analysis
    start_time := NOW();
    SELECT cleanup_old_trend_analysis() INTO trend_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'trend_analysis'::TEXT, trend_deleted, (end_time - start_time);
    
    -- Clean up signal events
    start_time := NOW();
    SELECT cleanup_old_signal_events() INTO signal_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'signal_events'::TEXT, signal_deleted, (end_time - start_time);
    
    -- Clean up analysis runs (do this last)
    start_time := NOW();
    SELECT cleanup_old_analysis_runs() INTO runs_deleted;
    end_time := NOW();
    
    RETURN QUERY SELECT 'analysis_runs'::TEXT, runs_deleted, (end_time - start_time);
    
    RETURN;
END;
$$ LANGUAGE plpgsql;

-- Create indexes for cleanup performance if they don't exist
CREATE INDEX IF NOT EXISTS idx_price_data_cleanup ON price_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_trend_analysis_cleanup ON trend_analysis(created_at);
CREATE INDEX IF NOT EXISTS idx_signal_events_cleanup ON signal_events(detected_at);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_cleanup ON analysis_runs(started_at); 