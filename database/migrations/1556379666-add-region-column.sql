-- Migration: add-region-column
-- Created at: 2019-04-27 11:41:06
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.geometries
ADD COLUMN IF NOT EXISTS region text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.geometries
DROP COLUMN IF EXISTS region;

COMMIT;
