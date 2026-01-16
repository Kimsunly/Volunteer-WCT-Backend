-- Migration: Change comments.entity_id from UUID to TEXT
-- Date: 2026-01-14
-- Description: Allow entity_id to store both integer IDs (opportunities) and UUIDs (blogs, community posts)

-- Step 1: Add a new TEXT column
ALTER TABLE comments ADD COLUMN entity_id_text TEXT;

-- Step 2: Copy existing UUID data to the new column (convert to text)
UPDATE comments SET entity_id_text = entity_id::TEXT;

-- Step 3: Drop the old UUID column
ALTER TABLE comments DROP COLUMN entity_id;

-- Step 4: Rename the new column to entity_id
ALTER TABLE comments RENAME COLUMN entity_id_text TO entity_id;

-- Step 5: Add NOT NULL constraint
ALTER TABLE comments ALTER COLUMN entity_id SET NOT NULL;

-- Step 6: Recreate any indexes that were on the old column
CREATE INDEX IF NOT EXISTS idx_comments_entity ON comments(entity_type, entity_id);

-- Add comment to document the change
COMMENT ON COLUMN comments.entity_id IS 'Entity ID as TEXT to support both integer IDs (opportunities) and UUIDs (blogs, community posts)';
