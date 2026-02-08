-- Kunani Database Schema
-- Issue Tracking System

-- Create issues table
CREATE TABLE IF NOT EXISTS issues (
    id SERIAL PRIMARY KEY,
    issue_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    priority VARCHAR(50) DEFAULT 'medium',
    category VARCHAR(100),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create index on issue_id for fast lookups
CREATE INDEX IF NOT EXISTS idx_issues_issue_id ON issues(issue_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status);

-- Create index on created_at for sorting
CREATE INDEX IF NOT EXISTS idx_issues_created_at ON issues(created_at DESC);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_issues_updated_at BEFORE UPDATE ON issues
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Note: LangGraph's PostgresSaver automatically creates checkpoint tables
-- (checkpoints and checkpoint_blobs) when initialized, so no need to create them here

