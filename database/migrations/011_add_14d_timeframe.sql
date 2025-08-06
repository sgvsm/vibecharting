-- Migration: Add '14d' to timeframe_enum
-- This migration adds the '14d' value to the existing timeframe_enum type

-- Add the new enum value
ALTER TYPE timeframe_enum ADD VALUE '14d' AFTER '7d';

-- Verify the change
SELECT unnest(enum_range(NULL::timeframe_enum)) as valid_timeframes; 