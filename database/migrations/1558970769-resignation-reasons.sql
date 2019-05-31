-- Migration: resignation-reasons
-- Created at: 2019-05-27 11:26:09
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.members
ADD COLUMN IF NOT EXISTS resignation_reason text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.members
DROP COLUMN IF EXISTS resignation_reason;

COMMIT;
