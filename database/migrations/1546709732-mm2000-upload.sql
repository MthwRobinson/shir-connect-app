-- Migration: mm2000-upload
-- Created at: 2019-01-05 12:35:32
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.members
ADD COLUMN IF NOT EXISTS gender text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.members
DROP COLUMN IF EXISTS gender;

COMMIT;
