-- Add work item approval-state classification.
-- SQLite migration runners should guard this with PRAGMA table_info because
-- SQLite does not support ADD COLUMN IF NOT EXISTS.
ALTER TABLE work_items ADD COLUMN approval_state TEXT;
