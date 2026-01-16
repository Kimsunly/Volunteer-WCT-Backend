-- Migration: Create blood_donations table
-- This fixes the 500 error when submitting the blood donation form

CREATE TABLE IF NOT EXISTS public.blood_donations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    dob DATE NOT NULL,
    blood_type TEXT NOT NULL,
    agree BOOLEAN DEFAULT TRUE,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Add RLS (Row Level Security)
ALTER TABLE public.blood_donations ENABLE ROW LEVEL SECURITY;

-- Allow anyone to submit a blood donation registration
CREATE POLICY "Allow public insert for blood donations" ON public.blood_donations
    FOR INSERT WITH CHECK (true);

-- Allow admins to view all registrations
CREATE POLICY "Allow admins to select blood donations" ON public.blood_donations
    FOR SELECT TO authenticated USING (
        EXISTS (
            SELECT 1 FROM user_profiles
            WHERE user_id = auth.uid() AND role = 'admin'
        )
    );

-- Allow users to view their own registrations (by email match)
CREATE POLICY "Allow users to select their own blood donations" ON public.blood_donations
    FOR SELECT USING (
        email = (SELECT email FROM auth.users WHERE id = auth.uid())
    );
