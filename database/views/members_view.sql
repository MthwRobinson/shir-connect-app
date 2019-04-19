CREATE MATERIALIZED VIEW 
IF NOT EXISTS {schema}.members_view
AS
SELECT *, DATE_PART('year', AGE(now(), birth_date)) as age
FROM {schema}.members a
LEFT JOIN (SELECT DISTINCT id as zip_code, city, county, region
           FROM {schema}.geometries) b
ON a.postal_code = b.zip_code
WITH DATA
