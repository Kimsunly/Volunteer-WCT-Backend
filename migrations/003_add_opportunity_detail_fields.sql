-- Migration: Add dynamic detail fields to opportunities table
-- Date: 2026-01-14
-- Description: Add columns for skills, tasks, impact, testimonials, and contact info

ALTER TABLE opportunities
ADD COLUMN IF NOT EXISTS skills JSONB,
ADD COLUMN IF NOT EXISTS tasks JSONB,
ADD COLUMN IF NOT EXISTS impact_description TEXT,
ADD COLUMN IF NOT EXISTS impact_stats JSONB,
ADD COLUMN IF NOT EXISTS testimonials JSONB,
ADD COLUMN IF NOT EXISTS contact_website VARCHAR(255),
ADD COLUMN IF NOT EXISTS contact_email VARCHAR(255),
ADD COLUMN IF NOT EXISTS contact_phone VARCHAR(50),
ADD COLUMN IF NOT EXISTS contact_social JSONB,
ADD COLUMN IF NOT EXISTS contact_hours VARCHAR(100),
ADD COLUMN IF NOT EXISTS contact_address TEXT,
ADD COLUMN IF NOT EXISTS popularity_level VARCHAR(50);

-- Add comments to document the columns
COMMENT ON COLUMN opportunities.skills IS 'JSONB array of required skills (e.g., ["Communication", "Teamwork"])';
COMMENT ON COLUMN opportunities.tasks IS 'JSONB array of main tasks (e.g., ["Organize events", "Coordinate activities"])';
COMMENT ON COLUMN opportunities.impact_description IS 'Text description of program impact';
COMMENT ON COLUMN opportunities.impact_stats IS 'JSONB object with impact statistics (e.g., {"beneficiaries": "500+", "projects": "20+"})';
COMMENT ON COLUMN opportunities.testimonials IS 'JSONB array of testimonial objects with name, role, image, quote';
COMMENT ON COLUMN opportunities.contact_website IS 'Organization website URL';
COMMENT ON COLUMN opportunities.contact_email IS 'Contact email address';
COMMENT ON COLUMN opportunities.contact_phone IS 'Contact phone number';
COMMENT ON COLUMN opportunities.contact_social IS 'JSONB object with social media links (e.g., {"facebook": "url", "twitter": "url"})';
COMMENT ON COLUMN opportunities.contact_hours IS 'Working hours text (e.g., "8:00 AM - 5:00 PM")';
COMMENT ON COLUMN opportunities.contact_address IS 'Physical address';
COMMENT ON COLUMN opportunities.popularity_level IS 'Popularity level for display (e.g., "Popular", "Trending")';
