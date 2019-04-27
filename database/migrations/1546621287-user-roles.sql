-- Migration: user-roles
-- Created at: 2019-01-04 12:01:27
-- ====  UP  ====

BEGIN;

ALTER TABLE shir_connect.users
ADD COLUMN IF NOT EXISTS role text DEFAULT 'standard',
ADD COLUMN IF NOT EXISTS modules text[] DEFAULT array[]::text[];

COMMIT;

-- ==== DOWN ====

BEGIN;

ALTER TABLE shir_connect.users
DROP COLUMN IF EXISTS role,
DROP COLUMN IF EXISTS modules;

COMMIT;
