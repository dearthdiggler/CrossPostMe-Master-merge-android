-- ============================================
-- CROSSPOSTME DATABASE SCHEMA - SECURITY FIXED
-- PostgreSQL Schema for Supabase
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name VARCHAR(255),
    phone VARCHAR(50),

    -- Trial & subscription
    is_active BOOLEAN DEFAULT true,
    trial_active BOOLEAN DEFAULT true,
    trial_type VARCHAR(50) DEFAULT 'free',
    trial_start_date TIMESTAMP DEFAULT NOW(),
    subscription_tier VARCHAR(50),
    subscription_status VARCHAR(50),

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_active_date TIMESTAMP DEFAULT NOW(),

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- ============================================
-- USER BUSINESS PROFILES
-- ============================================
CREATE TABLE user_business_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Business info
    business_name VARCHAR(255),
    business_type VARCHAR(100),
    industry VARCHAR(100),
    team_size VARCHAR(50),

    -- Marketplace data
    current_marketplaces TEXT[],
    monthly_listings VARCHAR(50),
    average_item_price VARCHAR(50),
    monthly_revenue VARCHAR(50),
    biggest_challenge TEXT,
    current_tools TEXT[],

    -- Goals
    growth_goal TEXT,
    listings_goal TEXT,

    -- Preferences
    marketing_emails BOOLEAN DEFAULT true,
    data_sharing BOOLEAN DEFAULT true,
    beta_tester BOOLEAN DEFAULT false,

    -- Attribution
    signup_source VARCHAR(100),
    utm_source VARCHAR(100),
    utm_medium VARCHAR(100),
    utm_campaign VARCHAR(100),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id)
);

-- ============================================
-- LISTINGS TABLE
-- ============================================
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    -- Listing content
    title VARCHAR(500) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2),
    category VARCHAR(100),
    condition VARCHAR(50),

    -- Media
    images TEXT[],

    -- Location
    location VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- Status
    status VARCHAR(50) DEFAULT 'draft',

    -- Platform postings
    platforms JSONB DEFAULT '{}'::jsonb,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,
    sold_at TIMESTAMP
);

-- ============================================
-- BUSINESS INTELLIGENCE TABLE
-- ============================================
CREATE TABLE business_intelligence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,

    timestamp TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- PLATFORM CONNECTIONS TABLE
-- ============================================
CREATE TABLE platform_connections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    platform VARCHAR(50) NOT NULL,
    platform_user_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,

    is_active BOOLEAN DEFAULT true,
    last_sync TIMESTAMP,

    metadata JSONB DEFAULT '{}'::jsonb,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, platform)
);

-- ============================================
-- ANALYTICS TABLE
-- ============================================
CREATE TABLE analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,

    platform VARCHAR(50),

    -- Metrics
    views INTEGER DEFAULT 0,
    favorites INTEGER DEFAULT 0,
    messages INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,

    -- Timestamps
    date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(listing_id, platform, date)
);

-- ============================================
-- INDEXES FOR PERFORMANCE
-- ============================================

-- Users
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_trial_active ON users(trial_active);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Business Profiles
CREATE INDEX idx_business_profiles_user_id ON user_business_profiles(user_id);
CREATE INDEX idx_business_profiles_industry ON user_business_profiles(industry);
CREATE INDEX idx_business_profiles_monthly_revenue ON user_business_profiles(monthly_revenue);

-- Listings
CREATE INDEX idx_listings_user_id ON listings(user_id);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_created_at ON listings(created_at);
CREATE INDEX idx_listings_category ON listings(category);

-- Business Intelligence
CREATE INDEX idx_bi_user_id ON business_intelligence(user_id);
CREATE INDEX idx_bi_event_type ON business_intelligence(event_type);
CREATE INDEX idx_bi_timestamp ON business_intelligence(timestamp);

-- Platform Connections
CREATE INDEX idx_platform_connections_user_id ON platform_connections(user_id);
CREATE INDEX idx_platform_connections_platform ON platform_connections(platform);

-- Analytics
CREATE INDEX idx_analytics_listing_id ON analytics(listing_id);
CREATE INDEX idx_analytics_user_id ON analytics(user_id);
CREATE INDEX idx_analytics_date ON analytics(date);

-- ============================================
-- ROW LEVEL SECURITY (RLS) - ALL TABLES
-- FIXED: Enable RLS on business_intelligence too
-- ============================================

-- Enable RLS on ALL tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_business_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE listings ENABLE ROW LEVEL SECURITY;
ALTER TABLE business_intelligence ENABLE ROW LEVEL SECURITY;
ALTER TABLE platform_connections ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;

-- Policies for users table
CREATE POLICY "Users can view own data" ON users
    FOR SELECT USING (auth.uid()::text = id::text);

CREATE POLICY "Users can update own data" ON users
    FOR UPDATE USING (auth.uid()::text = id::text);

-- Policies for business profiles
CREATE POLICY "Users can view own profile" ON user_business_profiles
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can update own profile" ON user_business_profiles
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Policies for listings
CREATE POLICY "Users can view own listings" ON listings
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can manage own listings" ON listings
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Policies for business intelligence (FIXED: Added RLS policies)
CREATE POLICY "Users can view own events" ON business_intelligence
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "System can insert events" ON business_intelligence
    FOR INSERT WITH CHECK (true);

-- Policies for platform connections
CREATE POLICY "Users can view own connections" ON platform_connections
    FOR SELECT USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can manage own connections" ON platform_connections
    FOR ALL USING (auth.uid()::text = user_id::text);

-- Policies for analytics
CREATE POLICY "Users can view own analytics" ON analytics
    FOR SELECT USING (auth.uid()::text = user_id::text);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- FIXED: Set search_path for security
-- ============================================

-- Update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER
SECURITY DEFINER
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

-- Apply trigger to all tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_business_profiles_updated_at BEFORE UPDATE ON user_business_profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_updated_at BEFORE UPDATE ON listings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_platform_connections_updated_at BEFORE UPDATE ON platform_connections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- VIEWS FOR ANALYTICS
-- FIXED: Remove SECURITY DEFINER (use SECURITY INVOKER)
-- ============================================

-- User stats view (SECURITY INVOKER means it uses querying user's permissions)
CREATE VIEW user_stats
WITH (security_invoker=true)
AS
SELECT
    u.id,
    u.username,
    u.email,
    u.trial_type,
    u.subscription_tier,
    bp.industry,
    bp.monthly_revenue,
    bp.team_size,
    COUNT(DISTINCT l.id) as total_listings,
    COUNT(DISTINCT pc.id) as connected_platforms,
    u.created_at as signup_date
FROM users u
LEFT JOIN user_business_profiles bp ON u.id = bp.user_id
LEFT JOIN listings l ON u.id = l.user_id
LEFT JOIN platform_connections pc ON u.id = pc.user_id
GROUP BY u.id, u.username, u.email, u.trial_type, u.subscription_tier,
         bp.industry, bp.monthly_revenue, bp.team_size, u.created_at;

-- Industry breakdown view (SECURITY INVOKER)
CREATE VIEW industry_breakdown
WITH (security_invoker=true)
AS
SELECT
    industry,
    COUNT(*) as user_count,
    AVG(CASE
        WHEN monthly_revenue = 'under-1k' THEN 500
        WHEN monthly_revenue = '1k-5k' THEN 3000
        WHEN monthly_revenue = '5k-10k' THEN 7500
        WHEN monthly_revenue = '10k-25k' THEN 17500
        WHEN monthly_revenue = '25k-50k' THEN 37500
        WHEN monthly_revenue = '50k+' THEN 75000
        ELSE 0
    END) as avg_revenue_estimate
FROM user_business_profiles
WHERE industry IS NOT NULL
GROUP BY industry
ORDER BY user_count DESC;

-- ============================================
-- SAMPLE DATA (Optional - for testing)
-- ============================================

-- Insert test user
INSERT INTO users (username, email, password_hash, full_name, trial_active)
VALUES ('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5UpfVWW4D2Lne', 'Test User', true)
ON CONFLICT (email) DO NOTHING;