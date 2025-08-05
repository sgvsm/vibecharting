-- Migration: 004_create_signal_events.sql
-- Description: Create signal_events table to store detected market signals
-- Date: 2025-01-01

BEGIN;

-- Create signal type enum
CREATE TYPE signal_type_enum AS ENUM ('pump_and_dump', 'bottomed_out', 'volume_anomaly');

-- Create signal_events table
CREATE TABLE signal_events (
    id SERIAL PRIMARY KEY,
    crypto_id INTEGER NOT NULL REFERENCES cryptocurrencies(id),
    signal_type signal_type_enum NOT NULL,
    detected_at TIMESTAMP WITH TIME ZONE NOT NULL,
    confidence DECIMAL(5, 4) CHECK (confidence >= 0 AND confidence <= 1),
    trigger_price DECIMAL(20, 8),
    volume_spike_ratio DECIMAL(10, 4), -- For pump & dump detection
    metadata JSONB, -- Signal-specific data
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX idx_signal_events_crypto_type ON signal_events(crypto_id, signal_type);
CREATE INDEX idx_signal_events_detected_at ON signal_events(detected_at DESC);
CREATE INDEX idx_signal_events_active ON signal_events(is_active) WHERE is_active = true;
CREATE INDEX idx_signal_events_metadata ON signal_events USING GIN(metadata);

COMMIT; 