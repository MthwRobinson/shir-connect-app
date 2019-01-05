-- Migration: mm2000-upload
-- Created at: 2019-01-05 12:35:32
-- ====  UP  ====

BEGIN;

ALTER TABLE trs_dashboard.members
ADD COLUMN gender text DEFAULT NULL;

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE trs_dashboard.members
DROP COLUMN gender;

COMMIT;
