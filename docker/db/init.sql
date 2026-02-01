-- =============================================================================
-- MgmtSays Database Initialization
-- =============================================================================
-- This script runs when the PostgreSQL container is first created
-- =============================================================================

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- Create schema
CREATE SCHEMA IF NOT EXISTS mgmtsays;

-- Set default schema
SET search_path TO mgmtsays, public;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'MgmtSays database initialized successfully';
END $$;
