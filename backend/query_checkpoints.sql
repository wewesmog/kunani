-- Query to view latest checkpoints from LangGraph
-- These queries show checkpoint records ordered by latest first

-- View all checkpoints ordered by latest first
SELECT 
    checkpoint_id,
    thread_id,
    checkpoint_ns,
    checkpoint,
    parent_checkpoint_id,
    checkpoint_ns,
    metadata,
    created_at
FROM checkpoints
ORDER BY created_at DESC
LIMIT 20;

-- View checkpoints with thread information
SELECT 
    thread_id,
    checkpoint_id,
    created_at,
    metadata->>'step' as step,
    metadata->>'source' as source,
    parent_checkpoint_id
FROM checkpoints
ORDER BY created_at DESC
LIMIT 20;

-- View checkpoints for a specific thread
SELECT 
    checkpoint_id,
    created_at,
    metadata->>'step' as step,
    metadata->>'source' as source,
    parent_checkpoint_id
FROM checkpoints
WHERE thread_id = 'user_session_1'  -- Replace with your thread_id
ORDER BY created_at DESC;

-- Count checkpoints per thread
SELECT 
    thread_id,
    COUNT(*) as checkpoint_count,
    MAX(created_at) as latest_checkpoint
FROM checkpoints
GROUP BY thread_id
ORDER BY latest_checkpoint DESC;

-- View checkpoint blobs (if any large data is stored)
SELECT 
    checkpoint_id,
    thread_id,
    channel,
    version,
    type,
    created_at
FROM checkpoint_blobs
ORDER BY created_at DESC
LIMIT 20;

