-- Add UNIQUE constraint to prevent duplicate campaigns
-- Run this in Supabase SQL Editor: https://supabase.com/dashboard/project/lmygwmivhbswqnuvsuht/sql

-- Add constraint: same card_id + title cannot be inserted twice
ALTER TABLE campaigns
ADD CONSTRAINT unique_card_campaign
UNIQUE (card_id, title);

-- Verify constraint was added
SELECT
    conname AS constraint_name,
    contype AS constraint_type
FROM pg_constraint
WHERE conrelid = 'campaigns'::regclass
AND conname = 'unique_card_campaign';
