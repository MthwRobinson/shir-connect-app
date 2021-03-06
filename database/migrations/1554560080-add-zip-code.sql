-- Migration: add-zip-code
-- Created at: 2019-04-06 10:14:40
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.geometries
ADD COLUMN IF NOT EXISTS city text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS county text DEFAULT NULL,
ADD COLUMN IF NOT EXISTS region text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.geometries
DROP COLUMN IF EXISTS city,
DROP COLUMN IF EXISTS county,
DROP COLUMN IF EXISTS region;

COMMIT;
