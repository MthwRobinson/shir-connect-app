-- Migration: fake-news
-- Created at: 2019-05-20 20:24:06
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.participant_match
ADD COLUMN IF NOT EXISTS fake_first_name text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS fake_last_name text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS fake_nickname text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS fake_email text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.participant_match
DROP COLUMN IF EXISTS fake_first_name,
DROP COLUMN IF EXISTS fake_last_name,
DROP COLUMN IF EXISTS fake_nickname,
DROP COLUMN IF EXISTS fake_email;

COMMIT;
