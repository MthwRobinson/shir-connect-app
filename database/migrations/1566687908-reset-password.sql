-- Migration: reset-password
-- Created at: 2019-08-24 19:05:08
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.users
ADD COLUMN IF NOT EXISTS email text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS temporary_password boolean DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS pw_update_ts timestamp DEFAULT NOW();

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.users
DROP COLUMN IF EXISTS email,
DROP COLUMN IF EXISTS temporary_password,
DROP COLUMN IF EXISTS pw_update_ts;

COMMIT;
