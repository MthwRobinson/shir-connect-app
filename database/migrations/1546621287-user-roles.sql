-- Migration: user-roles
-- Created at: 2019-01-04 12:01:27
-- ====  UP  ====

BEGIN;

ALTER TABLE trs_dashboard.users
ADD COLUMN role text DEFAULT 'standard',
ADD COLUMN modules text[] DEFAULT array[]::text[];

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE trs_dashboard.users
DROP COLUMN role,
DROP COLUMN modules;

COMMIT;
