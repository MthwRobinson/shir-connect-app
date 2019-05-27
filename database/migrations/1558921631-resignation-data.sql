-- Migration: resignation-data
-- Created at: 2019-05-26 21:47:11
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.members
ADD COLUMN IF NOT EXISTS resignation_date timestamp DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

COMMIT;


BEGIN;


COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.members
DROP COLUMN IF EXISTS resignation_date;

COMMIT;
