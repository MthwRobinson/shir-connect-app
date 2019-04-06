-- Migration: add-zip-code
-- Created at: 2019-04-06 10:14:40
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.users
ADD COLUMN IF NOT EXISTS city_name text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.users
DROP COLUMN city_name;

COMMIT;
