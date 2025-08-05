-- Migration: 005_create_analysis_runs.sql
-- Description: Create analysis_runs table to track analysis job executions
-- Date: 2025-01-01

BEGIN;

-- Create run status and type enums
CREATE TYPE run_status_enum AS ENUM ('running', 'completed', 'failed', 'cancelled');
CREATE TYPE run_type_enum AS ENUM ('data_ingestion', 'trend_analysis', 'signal_detection', 'data_cleanup_price', 'data_cleanup_trends', 'data_cleanup_signals');

-- Create analysis_runs table
CREATE TABLE analysis_runs (
    id SERIAL PRIMARY KEY,
    run_type run_type_enum NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    status run_status_enum DEFAULT 'running',
    records_processed INTEGER DEFAULT 0, -- Fixed: was processed_count
    error_count INTEGER DEFAULT 0,
    error_message TEXT,
    notes TEXT, -- Added: used in cleanup functions
    metadata JSONB
);

-- Create indexes
CREATE INDEX idx_analysis_runs_type_status ON analysis_runs(run_type, status);
CREATE INDEX idx_analysis_runs_started_at ON analysis_runs(started_at DESC);

COMMIT; 