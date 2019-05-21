-- Migration: fake-events
-- Created at: 2019-05-20 21:36:17
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.events
ADD COLUMN IF NOT EXISTS fake_name text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS fake_description text DEFAULT NULL;

ALTER TABLE shir_connect.venues
ADD COLUMN IF NOT EXISTS fake_name text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.events
DROP COLUMN IF EXISTS fake_name,
DROP COLUMN IF EXISTS fake_description;

ALTER TABLE shir_connect.venues
DROP COLUMN IF EXISTS fake_name;

COMMIT;
