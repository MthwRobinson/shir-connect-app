-- Migration: add-household-id
-- Created at: 2019-04-11 22:20:08
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.members
ADD COLUMN IF NOT EXISTS household_id text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS active_member boolean DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.members
DROP COLUMN IF EXISTS household_id,
DROP COLUMN IF EXISTS active_member;

COMMIT;
