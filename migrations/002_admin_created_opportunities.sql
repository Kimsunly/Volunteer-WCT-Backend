-- ============================================
-- MIGRATION: Admin-Created Opportunities
-- Allows admins to create opportunities directly
-- without needing an organizer
-- ============================================

-- 1. Allow organizer_id to be NULL (admin creates without organizer)
ALTER TABLE opportunities 
ALTER COLUMN organizer_id DROP NOT NULL;

-- 2. Add created_by_admin column to track which admin created it
ALTER TABLE opportunities 
ADD COLUMN IF NOT EXISTS created_by_admin UUID REFERENCES auth.users(id);

-- 3. Drop the FK constraint to organizer_profiles (wrong table reference)
ALTER TABLE opportunities 
DROP CONSTRAINT IF EXISTS fk_opportunities_organizer;

-- 4. Add correct FK constraint to organizer_applications (optional, can be NULL)
ALTER TABLE opportunities
ADD CONSTRAINT fk_opportunities_organizer 
FOREIGN KEY (organizer_id) 
REFERENCES organizer_applications(id)
ON DELETE SET NULL;

-- 5. Add index for admin-created opportunities
CREATE INDEX IF NOT EXISTS idx_opportunities_created_by_admin 
ON opportunities(created_by_admin);

-- 6. Add comment to document the schema
COMMENT ON COLUMN opportunities.created_by_admin IS 
'Admin user ID who created this opportunity. NULL if created by organizer.';

COMMENT ON COLUMN opportunities.organizer_id IS 
'Organizer ID from organizer_applications. NULL if created by admin directly.';
