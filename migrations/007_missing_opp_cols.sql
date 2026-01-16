-- Add missing columns to opportunities table safely
ALTER TABLE opportunities 
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active' CHECK (status IN ('active', 'pending', 'closed')),
ADD COLUMN IF NOT EXISTS title_en TEXT,
ADD COLUMN IF NOT EXISTS category_label TEXT,
ADD COLUMN IF NOT EXISTS location_label TEXT,
ADD COLUMN IF NOT EXISTS impact_description TEXT,
ADD COLUMN IF NOT EXISTS skills JSONB,
ADD COLUMN IF NOT EXISTS tasks JSONB,
ADD COLUMN IF NOT EXISTS access_key_hash TEXT,
ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT FALSE;
