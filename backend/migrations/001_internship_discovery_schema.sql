-- Internship Discovery & Verification Module - Database Schema
-- Migration: 001_internship_discovery_schema
-- Description: Creates all tables, indexes, and triggers for the internship discovery system

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table 1: student_profiles
-- Stores student profile information for personalized recommendations
-- ============================================================================
CREATE TABLE IF NOT EXISTS student_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    graduation_year INTEGER NOT NULL,
    current_semester INTEGER NOT NULL CHECK (current_semester BETWEEN 1 AND 8),
    degree VARCHAR(50) NOT NULL,
    branch VARCHAR(100) NOT NULL,
    skills TEXT[] NOT NULL DEFAULT '{}',
    preferred_roles TEXT[] NOT NULL DEFAULT '{}',
    internship_type VARCHAR(20) CHECK (internship_type IN ('Remote', 'On-site', 'Hybrid')),
    compensation_preference VARCHAR(20) CHECK (compensation_preference IN ('Paid', 'Unpaid', 'Any')),
    target_companies TEXT[] DEFAULT '{}',
    resume_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Indexes for student_profiles
CREATE INDEX IF NOT EXISTS idx_student_profiles_user_id ON student_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_student_profiles_semester ON student_profiles(current_semester);
CREATE INDEX IF NOT EXISTS idx_student_profiles_skills ON student_profiles USING GIN(skills);

-- ============================================================================
-- Table 2: internship_listings
-- Stores internship opportunities with verification status
-- ============================================================================
CREATE TABLE IF NOT EXISTS internship_listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    company VARCHAR(200) NOT NULL,
    company_domain VARCHAR(200),
    platform VARCHAR(100),
    location VARCHAR(200),
    internship_type VARCHAR(20) CHECK (internship_type IN ('Summer', 'Winter', 'Research', 'Off-cycle')),
    duration VARCHAR(50),
    stipend VARCHAR(100),
    required_skills TEXT[] NOT NULL DEFAULT '{}',
    preferred_skills TEXT[] DEFAULT '{}',
    responsibilities TEXT[] NOT NULL DEFAULT '{}',
    application_deadline DATE,
    start_date DATE,
    verification_status VARCHAR(20) DEFAULT 'Pending' CHECK (verification_status IN ('Verified', 'Use Caution', 'Potential Scam', 'Pending')),
    trust_score INTEGER DEFAULT 0 CHECK (trust_score BETWEEN 0 AND 100),
    red_flags JSONB DEFAULT '[]',
    posted_date DATE DEFAULT CURRENT_DATE,
    is_active BOOLEAN DEFAULT TRUE,
    source_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for internship_listings
CREATE INDEX IF NOT EXISTS idx_internship_listings_company ON internship_listings(company);
CREATE INDEX IF NOT EXISTS idx_internship_listings_type ON internship_listings(internship_type);
CREATE INDEX IF NOT EXISTS idx_internship_listings_status ON internship_listings(verification_status);
CREATE INDEX IF NOT EXISTS idx_internship_listings_deadline ON internship_listings(application_deadline);
CREATE INDEX IF NOT EXISTS idx_internship_listings_skills ON internship_listings USING GIN(required_skills);
CREATE INDEX IF NOT EXISTS idx_internship_listings_active ON internship_listings(is_active) WHERE is_active = TRUE;

-- ============================================================================
-- Table 3: verification_results
-- Stores detailed verification analysis for internships
-- ============================================================================
CREATE TABLE IF NOT EXISTS verification_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internship_id UUID NOT NULL REFERENCES internship_listings(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('Verified', 'Use Caution', 'Potential Scam')),
    trust_score INTEGER NOT NULL CHECK (trust_score BETWEEN 0 AND 100),
    verification_signals JSONB NOT NULL DEFAULT '{}',
    red_flags JSONB NOT NULL DEFAULT '[]',
    verification_notes TEXT,
    last_verified TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(internship_id)
);

-- Indexes for verification_results
CREATE INDEX IF NOT EXISTS idx_verification_results_internship ON verification_results(internship_id);
CREATE INDEX IF NOT EXISTS idx_verification_results_status ON verification_results(status);

-- ============================================================================
-- Table 4: skill_matches
-- Caches skill matching results for performance
-- ============================================================================
CREATE TABLE IF NOT EXISTS skill_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    internship_id UUID NOT NULL REFERENCES internship_listings(id) ON DELETE CASCADE,
    match_percentage INTEGER NOT NULL CHECK (match_percentage BETWEEN 0 AND 100),
    matching_skills TEXT[] NOT NULL DEFAULT '{}',
    missing_skills TEXT[] NOT NULL DEFAULT '{}',
    learning_path JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, internship_id)
);

-- Indexes for skill_matches
CREATE INDEX IF NOT EXISTS idx_skill_matches_user ON skill_matches(user_id);
CREATE INDEX IF NOT EXISTS idx_skill_matches_internship ON skill_matches(internship_id);
CREATE INDEX IF NOT EXISTS idx_skill_matches_percentage ON skill_matches(match_percentage DESC);

-- ============================================================================
-- Table 5: readiness_scores
-- Stores readiness assessment for user-internship pairs
-- ============================================================================
CREATE TABLE IF NOT EXISTS readiness_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    internship_id UUID NOT NULL REFERENCES internship_listings(id) ON DELETE CASCADE,
    overall_score INTEGER NOT NULL CHECK (overall_score BETWEEN 0 AND 100),
    resume_strength INTEGER NOT NULL CHECK (resume_strength BETWEEN 0 AND 100),
    skill_match INTEGER NOT NULL CHECK (skill_match BETWEEN 0 AND 100),
    semester_readiness INTEGER NOT NULL CHECK (semester_readiness BETWEEN 0 AND 100),
    recommendation VARCHAR(50) NOT NULL,
    improvement_actions JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, internship_id)
);

-- Indexes for readiness_scores
CREATE INDEX IF NOT EXISTS idx_readiness_scores_user ON readiness_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_readiness_scores_internship ON readiness_scores(internship_id);
CREATE INDEX IF NOT EXISTS idx_readiness_scores_overall ON readiness_scores(overall_score DESC);

-- ============================================================================
-- Table 6: user_alerts
-- Stores personalized alerts and notifications
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    internship_id UUID REFERENCES internship_listings(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('new_match', 'deadline_approaching', 'readiness_improved', 'season_starting')),
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user_alerts
CREATE INDEX IF NOT EXISTS idx_user_alerts_user ON user_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_read ON user_alerts(is_read) WHERE is_read = FALSE;
CREATE INDEX IF NOT EXISTS idx_user_alerts_created ON user_alerts(created_at DESC);

-- ============================================================================
-- Table 7: scam_reports
-- Tracks user-reported suspicious listings
-- ============================================================================
CREATE TABLE IF NOT EXISTS scam_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    internship_id UUID NOT NULL REFERENCES internship_listings(id) ON DELETE CASCADE,
    reported_by UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    reason TEXT NOT NULL,
    details TEXT,
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Reviewed', 'Confirmed', 'Dismissed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES auth.users(id)
);

-- Indexes for scam_reports
CREATE INDEX IF NOT EXISTS idx_scam_reports_internship ON scam_reports(internship_id);
CREATE INDEX IF NOT EXISTS idx_scam_reports_status ON scam_reports(status);

-- ============================================================================
-- Triggers for automatic updated_at timestamp updates
-- ============================================================================

-- Create or replace the trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to student_profiles
DROP TRIGGER IF EXISTS update_student_profiles_updated_at ON student_profiles;
CREATE TRIGGER update_student_profiles_updated_at 
    BEFORE UPDATE ON student_profiles
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to internship_listings
DROP TRIGGER IF EXISTS update_internship_listings_updated_at ON internship_listings;
CREATE TRIGGER update_internship_listings_updated_at 
    BEFORE UPDATE ON internship_listings
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to readiness_scores
DROP TRIGGER IF EXISTS update_readiness_scores_updated_at ON readiness_scores;
CREATE TRIGGER update_readiness_scores_updated_at 
    BEFORE UPDATE ON readiness_scores
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Comments for documentation
-- ============================================================================

COMMENT ON TABLE student_profiles IS 'Stores student profile information for personalized internship recommendations';
COMMENT ON TABLE internship_listings IS 'Stores internship opportunities with verification status and details';
COMMENT ON TABLE verification_results IS 'Stores detailed verification analysis and fraud detection results';
COMMENT ON TABLE skill_matches IS 'Caches skill matching results between users and internships for performance';
COMMENT ON TABLE readiness_scores IS 'Stores readiness assessment scores for user-internship pairs';
COMMENT ON TABLE user_alerts IS 'Stores personalized alerts and notifications for users';
COMMENT ON TABLE scam_reports IS 'Tracks user-reported suspicious internship listings';

-- ============================================================================
-- Migration Complete
-- ============================================================================
