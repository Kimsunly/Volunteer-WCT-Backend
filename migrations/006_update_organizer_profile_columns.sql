-- Migration: Add missing columns to organizer_profiles
-- This fixes the 400 error when organizers update their profiles from the frontend

ALTER TABLE organizer_profiles 
ADD COLUMN IF NOT EXISTS website TEXT,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS description TEXT,
ADD COLUMN IF NOT EXISTS contact_person TEXT,
ADD COLUMN IF NOT EXISTS registration_number TEXT;

-- Add comments for documentation
COMMENT ON COLUMN organizer_profiles.website IS 'Public website of the organization';
COMMENT ON COLUMN organizer_profiles.address IS 'Physical address of the organization';
COMMENT ON COLUMN organizer_profiles.description IS 'Detailed description or mission statement of the organization';
COMMENT ON COLUMN organizer_profiles.contact_person IS 'Primary contact person for the organization';
COMMENT ON COLUMN organizer_profiles.registration_number IS 'Official registration or tax ID of the organization';
