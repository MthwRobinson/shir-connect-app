CREATE MATERIALIZED VIEW 
IF NOT EXISTS {schema}.members_view
AS
SELECT *
FROM {schema}.members
WITH DATA
