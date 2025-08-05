-- Migration: 008_create_indexes.sql
-- Description: Create additional performance indexes
-- Date: 2025-01-01

BEGIN;

-- Drop existing indexes if they exist (to handle partial creation from previous run)
DROP INDEX IF EXISTS idx_price_data_crypto_timestamp;
DROP INDEX IF EXISTS idx_price_data_volume;
DROP INDEX IF EXISTS idx_trend_analysis_crypto_type;
DROP INDEX IF EXISTS idx_trend_analysis_confidence;
DROP INDEX IF EXISTS idx_signal_events_type_confidence;
DROP INDEX IF EXISTS idx_signal_events_active;
DROP INDEX IF EXISTS idx_analysis_runs_type_status;
DROP INDEX IF EXISTS idx_query_logs_intent_created;

-- Price data performance indexes
CREATE INDEX idx_price_data_crypto_timestamp ON price_data(crypto_id, timestamp DESC);

CREATE INDEX idx_price_data_volume ON price_data(crypto_id, volume_24h DESC);

-- Trend analysis performance indexes
CREATE INDEX idx_trend_analysis_crypto_type ON trend_analysis(crypto_id, trend_type, confidence DESC);

CREATE INDEX idx_trend_analysis_confidence ON trend_analysis(confidence DESC)
WHERE confidence > 0.7;

-- Signal events performance indexes
CREATE INDEX idx_signal_events_type_confidence ON signal_events(signal_type, confidence DESC);

CREATE INDEX idx_signal_events_active ON signal_events(signal_type, detected_at DESC)
WHERE is_active = true;

-- Analysis runs performance index
CREATE INDEX idx_analysis_runs_type_status ON analysis_runs(run_type, status);

-- Query logs performance index
CREATE INDEX idx_query_logs_intent_created ON query_logs(intent_type, created_at DESC);

-- Add table statistics hints
ALTER TABLE price_data ALTER COLUMN timestamp SET STATISTICS 1000;
ALTER TABLE trend_analysis ALTER COLUMN end_time SET STATISTICS 1000;
ALTER TABLE signal_events ALTER COLUMN detected_at SET STATISTICS 1000;

COMMIT; 