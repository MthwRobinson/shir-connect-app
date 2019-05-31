CREATE TABLE IF NOT EXISTS {schema}.members (
  id text,
  first_name text,
  last_name text,
  nickname text,
  birth_date timestamp,
  membership_date timestamp,
  resignation_date timestamp,
  member_religion text,
  postal_code text,
  member_family text,
  member_type text,
  email text,
  gender text,
  household_id text,
  active_member boolean
);

CREATE UNIQUE INDEX IF NOT EXISTS members_index ON {schema}.members (id);
