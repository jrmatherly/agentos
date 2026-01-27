-- =============================================================================
-- AgentOS Platform Database Initialization
-- =============================================================================
-- Creates and configures all databases for the AgentOS platform.
-- This script runs automatically when PostgreSQL container starts.
--
-- IMPORTANT: This script runs in the context of the default database (agno),
-- which is auto-created by the POSTGRES_DB environment variable.
--
-- Databases:
--   - agno: Backend database for Agno framework (sessions, traces, knowledge)
--           Auto-created by POSTGRES_DB env var, we configure extensions here
--   - agent_ui: Frontend database for Better Auth, organizations, audit logs
--               Created by this script
--
-- Extensions:
--   - vector: pgvector for embeddings and similarity search (both databases)
--   - uuid-ossp: UUID generation (agent_ui only)
-- =============================================================================

-- =============================================================================
-- PART 1: Backend Database (agno) - Extensions
-- =============================================================================
-- The 'agno' database is auto-created by PostgreSQL via POSTGRES_DB env var.
-- We're currently connected to it, so we just need to enable extensions.

-- Enable vector extension for Agno knowledge base and embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Note: Agno framework auto-creates its tables (agent_sessions, agent_runs, etc.)
-- No manual table creation needed here.

-- =============================================================================
-- PART 2: Frontend Database (agent_ui) - Create and Configure
-- =============================================================================
-- Create database for agent-ui frontend (Better Auth, organizations, etc.)
CREATE DATABASE agent_ui;

-- Grant privileges to agno user (agentos-docker's default PostgreSQL user)
GRANT ALL PRIVILEGES ON DATABASE agent_ui TO agno;

-- Connect to agent_ui database to configure it
\c agent_ui

-- Grant schema privileges to agno user
GRANT ALL ON SCHEMA public TO agno;

-- Enable required extensions for agent_ui
CREATE EXTENSION IF NOT EXISTS vector;
-- For knowledge base features
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- For UUID generation

-- Note: Application tables (user, session, organization, etc.) are created
-- by the db-init container using Drizzle ORM schema push.

-- =============================================================================
-- Summary
-- =============================================================================
-- After this script completes:
--   1. agno database: exists with vector extension
--   2. agent_ui database: exists with vector and uuid-ossp extensions
--
-- Next steps (handled by other components):
--   - Agno framework auto-creates tables in 'agno' database
--   - db-init container runs Drizzle push to create tables in 'agent_ui'
--   - Admin user is seeded lazily on first auth API request