-- Migration: Add missing columns to opportunities table
-- This fixes the 500 error when creating opportunities with additional details

ALTER TABLE opportunities 
ADD COLUMN IF NOT EXISTS organization TEXT,
ADD COLUMN IF NOT EXISTS date_range DATE,
ADD COLUMN IF NOT EXISTS time_range TEXT,
ADD COLUMN IF NOT EXISTS capacity INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS transport TEXT,
ADD COLUMN IF NOT EXISTS housing TEXT,
ADD COLUMN IF NOT EXISTS meals TEXT;

-- Add comments for documentation
COMMENT ON COLUMN opportunities.organization IS 'Name of the organizing entity';
COMMENT ON COLUMN opportunities.date_range IS 'Start date or specific date of the opportunity';
COMMENT ON COLUMN opportunities.time_range IS 'Time or time range for the volunteer work';
COMMENT ON COLUMN opportunities.capacity IS 'Maximum number of volunteer positions available';
COMMENT ON COLUMN opportunities.transport IS 'Transportation details provided to volunteers';
COMMENT ON COLUMN opportunities.housing IS 'Accommodation details provided to volunteers';
COMMENT ON COLUMN opportunities.meals IS 'Meal arrangements provided during the opportunity';
