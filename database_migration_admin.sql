-- ============================================
-- COMPREHENSIVE ADMIN BACKEND - DATABASE SCHEMA
-- Supabase SQL Migration
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- CATEGORIES TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    icon TEXT,
    color TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Index for active categories
CREATE INDEX IF NOT EXISTS idx_categories_active ON categories(active);

-- ============================================
-- BLOGS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS blogs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    category TEXT,
    image TEXT,
    content TEXT NOT NULL,
    author TEXT,
    published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Index for published blogs
CREATE INDEX IF NOT EXISTS idx_blogs_published ON blogs(published);
CREATE INDEX IF NOT EXISTS idx_blogs_category ON blogs(category);

-- ============================================
-- COMMUNITY POSTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS community_posts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organizer_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    title_kh TEXT,
    content TEXT NOT NULL,
    content_kh TEXT,
    category TEXT NOT NULL CHECK (category IN ('update', 'event', 'discussion', 'story')),
    images TEXT[] DEFAULT '{}',
    visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'members')),
    likes INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    tags TEXT[] DEFAULT '{}',
    rejection_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Indexes for community posts
CREATE INDEX IF NOT EXISTS idx_community_posts_organizer ON community_posts(organizer_id);
CREATE INDEX IF NOT EXISTS idx_community_posts_status ON community_posts(status);
CREATE INDEX IF NOT EXISTS idx_community_posts_category ON community_posts(category);
CREATE INDEX IF NOT EXISTS idx_community_posts_visibility ON community_posts(visibility);

-- ============================================
-- COMMENTS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    entity_type TEXT NOT NULL CHECK (entity_type IN ('opportunity', 'community_post', 'blog')),
    entity_id UUID NOT NULL,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'visible' CHECK (status IN ('visible', 'hidden', 'flagged')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- Indexes for comments
CREATE INDEX IF NOT EXISTS idx_comments_user ON comments(user_id);
CREATE INDEX IF NOT EXISTS idx_comments_entity ON comments(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_comments_status ON comments(status);

-- ============================================
-- DONATIONS TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS donations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    donor_name TEXT,
    email TEXT,
    amount NUMERIC(10, 2) NOT NULL,
    currency TEXT DEFAULT 'USD',
    payment_method TEXT,
    transaction_id TEXT,
    status TEXT DEFAULT 'completed' CHECK (status IN ('pending', 'completed', 'failed', 'refunded')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for donations
CREATE INDEX IF NOT EXISTS idx_donations_status ON donations(status);
CREATE INDEX IF NOT EXISTS idx_donations_created ON donations(created_at);

-- ============================================
-- ADMIN ACTIVITY LOG TABLE
-- ============================================
CREATE TABLE IF NOT EXISTS admin_activity_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    admin_id UUID NOT NULL REFERENCES user_profiles(user_id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    details TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for activity log
CREATE INDEX IF NOT EXISTS idx_admin_log_admin ON admin_activity_log(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_log_created ON admin_activity_log(created_at);
CREATE INDEX IF NOT EXISTS idx_admin_log_action ON admin_activity_log(action);

-- ============================================
-- UPDATE EXISTING TABLES (if needed)
-- ============================================

-- Update opportunities table to include all required fields
ALTER TABLE opportunities 
ADD COLUMN IF NOT EXISTS visibility TEXT DEFAULT 'public' CHECK (visibility IN ('public', 'private')),
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active' CHECK (status IN ('active', 'pending', 'closed')),
ADD COLUMN IF NOT EXISTS registered INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

-- Update organizer_applications to match admin spec
ALTER TABLE organizer_applications
ADD COLUMN IF NOT EXISTS contact_person TEXT,
ADD COLUMN IF NOT EXISTS registration_number TEXT,
ADD COLUMN IF NOT EXISTS address TEXT,
ADD COLUMN IF NOT EXISTS website TEXT,
ADD COLUMN IF NOT EXISTS description TEXT;

-- Ensure user_profiles has status column
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending', 'rejected'));

-- ============================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================

-- Enable RLS on all tables
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE blogs ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_posts ENABLE ROW LEVEL SECURITY;
ALTER TABLE comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE donations ENABLE ROW LEVEL SECURITY;
ALTER TABLE admin_activity_log ENABLE ROW LEVEL SECURITY;

-- ============================================
-- RLS POLICIES - CATEGORIES
-- ============================================

-- Public read for active categories
CREATE POLICY "Anyone can view active categories"
ON categories FOR SELECT
USING (active = TRUE);

-- Admin full access
CREATE POLICY "Admin full access to categories"
ON categories FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'admin'
    )
);

-- ============================================
-- RLS POLICIES - BLOGS
-- ============================================

-- Public read for published blogs
CREATE POLICY "Anyone can view published blogs"
ON blogs FOR SELECT
USING (published = TRUE);

-- Admin full access
CREATE POLICY "Admin full access to blogs"
ON blogs FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'admin'
    )
);

-- ============================================
-- RLS POLICIES - COMMUNITY POSTS
-- ============================================

-- Public read for approved + public posts
CREATE POLICY "Anyone can view approved public community posts"
ON community_posts FOR SELECT
USING (status = 'approved' AND visibility = 'public');

-- Organizers can view their own posts
CREATE POLICY "Organizers can view their own community posts"
ON community_posts FOR SELECT
USING (organizer_id = auth.uid());

-- Organizers can create posts (pending status)
CREATE POLICY "Organizers can create community posts"
ON community_posts FOR INSERT
WITH CHECK (
    organizer_id = auth.uid() AND
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'organizer'
        AND user_profiles.status = 'active'
    )
);

-- Organizers can update their own pending posts
CREATE POLICY "Organizers can update their pending posts"
ON community_posts FOR UPDATE
USING (organizer_id = auth.uid() AND status = 'pending')
WITH CHECK (organizer_id = auth.uid());

-- Admin full access
CREATE POLICY "Admin full access to community posts"
ON community_posts FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'admin'
    )
);

-- ============================================
-- RLS POLICIES - COMMENTS
-- ============================================

-- Users can view visible comments
CREATE POLICY "Anyone can view visible comments"
ON comments FOR SELECT
USING (status = 'visible');

-- Authenticated users can create comments
CREATE POLICY "Authenticated users can create comments"
ON comments FOR INSERT
WITH CHECK (user_id = auth.uid());

-- Users can update their own comments
CREATE POLICY "Users can update their own comments"
ON comments FOR UPDATE
USING (user_id = auth.uid())
WITH CHECK (user_id = auth.uid());

-- Admin full access
CREATE POLICY "Admin full access to comments"
ON comments FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'admin'
    )
);

-- ============================================
-- RLS POLICIES - DONATIONS
-- ============================================

-- Admin can view all donations
CREATE POLICY "Admin can view all donations"
ON donations FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'admin'
    )
);

-- Public can insert donations (for payment processing)
CREATE POLICY "Anyone can create donations"
ON donations FOR INSERT
WITH CHECK (TRUE);

-- ============================================
-- RLS POLICIES - ADMIN ACTIVITY LOG
-- ============================================

-- Only admins can view logs
CREATE POLICY "Admin can view activity logs"
ON admin_activity_log FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'admin'
    )
);

-- Only admins can insert logs
CREATE POLICY "Admin can create activity logs"
ON admin_activity_log FOR INSERT
WITH CHECK (
    admin_id = auth.uid() AND
    EXISTS (
        SELECT 1 FROM user_profiles
        WHERE user_profiles.user_id = auth.uid()
        AND user_profiles.role = 'admin'
    )
);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for updated_at
DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;
CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_blogs_updated_at ON blogs;
CREATE TRIGGER update_blogs_updated_at
    BEFORE UPDATE ON blogs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_community_posts_updated_at ON community_posts;
CREATE TRIGGER update_community_posts_updated_at
    BEFORE UPDATE ON community_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_opportunities_updated_at ON opportunities;
CREATE TRIGGER update_opportunities_updated_at
    BEFORE UPDATE ON opportunities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SAMPLE DATA (optional)
-- ============================================

-- Insert sample categories
INSERT INTO categories (name, description, icon, color, active) VALUES
('Education', 'Educational volunteer opportunities', '📚', '#3B82F6', TRUE),
('Healthcare', 'Healthcare and medical volunteering', '🏥', '#10B981', TRUE),
('Environment', 'Environmental conservation', '🌱', '#22C55E', TRUE),
('Community', 'Community service and development', '🤝', '#F59E0B', TRUE),
('Animal Welfare', 'Animal rescue and care', '🐾', '#EC4899', TRUE),
('Disaster Relief', 'Emergency response and relief', '🚨', '#EF4444', TRUE)
ON CONFLICT (name) DO NOTHING;

-- ============================================
-- GRANTS (if using service role key in backend)
-- ============================================

-- Grant permissions to authenticated users
GRANT SELECT ON categories TO authenticated;
GRANT SELECT ON blogs TO authenticated;
GRANT SELECT, INSERT ON community_posts TO authenticated;
GRANT ALL ON comments TO authenticated;
GRANT INSERT ON donations TO authenticated;

-- Grant all to service role (used by backend)
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_community_posts_status_created 
ON community_posts(status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_opportunities_status_visibility 
ON opportunities(status, visibility);

CREATE INDEX IF NOT EXISTS idx_comments_entity_status 
ON comments(entity_type, entity_id, status);

-- ============================================
-- COMPLETION
-- ============================================

-- Verify tables
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('categories', 'blogs', 'community_posts', 'comments', 'donations', 'admin_activity_log')
ORDER BY table_name;
