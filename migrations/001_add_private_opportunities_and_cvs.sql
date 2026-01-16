-- Migration: Add private opportunity and CV fields
-- Run this against your Supabase / Postgres database

-- 1) Add privacy columns to opportunities
ALTER TABLE opportunities
  ADD COLUMN IF NOT EXISTS is_private boolean DEFAULT false,
  ADD COLUMN IF NOT EXISTS access_key_hash text;

-- 2) Add cv_url to applications
ALTER TABLE applications
  ADD COLUMN IF NOT EXISTS cv_url text;

-- Notes:
-- - access_key_hash stores a hash (SHA-256) of the plain access key; the API
--   will never store or return the plain key.
-- - If you prefer signed (private) storage for CVs, adjust the upload helper
--   to return signed URLs and keep the storage bucket private.
