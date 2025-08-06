-- Migration: 012_add_technical_indicator_signals.sql
-- Description: Add new signal types for technical indicator-based signals
-- Date: 2025-01-11

BEGIN;

-- Add new signal types to the enum
ALTER TYPE signal_type_enum ADD VALUE IF NOT EXISTS 'macd_bullish';
ALTER TYPE signal_type_enum ADD VALUE IF NOT EXISTS 'macd_bearish';
ALTER TYPE signal_type_enum ADD VALUE IF NOT EXISTS 'bollinger_breakout';
ALTER TYPE signal_type_enum ADD VALUE IF NOT EXISTS 'rsi_oversold';
ALTER TYPE signal_type_enum ADD VALUE IF NOT EXISTS 'rsi_overbought';
ALTER TYPE signal_type_enum ADD VALUE IF NOT EXISTS 'golden_cross';
ALTER TYPE signal_type_enum ADD VALUE IF NOT EXISTS 'death_cross';

-- Add comment to document the new signal types
COMMENT ON TYPE signal_type_enum IS 'Signal types: pump_and_dump, bottomed_out, volume_anomaly (legacy), macd_bullish, macd_bearish, bollinger_breakout, rsi_oversold, rsi_overbought, golden_cross, death_cross (technical indicators)';

COMMIT;