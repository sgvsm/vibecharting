-- Migration: 006_create_query_logs.sql
-- Description: Create query_logs table to track user queries and performance
-- Date: 2025-01-01

BEGIN;

-- Create query_logs table
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    intent_type VARCHAR(50), -- Fixed: was just 'intent'
    intent_confidence DECIMAL(5, 4), -- Added: used in Lambda code
    result_count INTEGER, -- Fixed: was 'response_count'
    execution_time_ms INTEGER,
    user_session_id VARCHAR(100), -- For future user tracking
    metadata JSONB, -- Added: used to store full intent object
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_query_logs_intent_type ON query_logs(intent_type); -- Fixed: was intent
CREATE INDEX idx_query_logs_created_at ON query_logs(created_at DESC);

-- Create cleanup function
CREATE OR REPLACE FUNCTION cleanup_old_query_logs()
RETURNS void AS $$
BEGIN
    DELETE FROM query_logs 
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

COMMIT; 