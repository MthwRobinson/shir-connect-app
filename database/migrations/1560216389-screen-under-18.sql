-- Migration: screen-under-18
-- Created at: 2019-06-10 21:26:30
-- ====  UP  ====

BEGIN;

DELETE
FROM shir_connect.members
WHERE DATE_PART('year', AGE(now(), birth_date)) < 18;

COMMIT;

-- ==== DOWN ====

BEGIN;

COMMIT;
