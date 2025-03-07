--################################
--################################
--###Territoires
--################################
--################################

DO $$
BEGIN
	DROP TABLE atlas.t_layer_territoire;
EXCEPTION WHEN others THEN
	RAISE NOTICE 'view atlas.t_layer_territoire does not exist';
END$$;


CREATE MATERIALIZED VIEW atlas.t_layer_territoire AS
WITH d AS (
	SELECT st_union(geom) , b.type_name
	FROM ref_geo.l_areas l
	JOIN ref_geo.bib_areas_types b USING(id_type)
	WHERE REPLACE(b.type_code, ' ', '_') = :type_territoire
	GROUP BY b.type_name
)
SELECT
 1::int as gid,
 type_name as nom,
 st_area(st_union)/10000 as surf_ha,
 st_area(st_union)/1000000 as surf_km2,
 ST_Perimeter(st_union)/1000 as perim_km,
 st_transform(st_union, 4326) as  the_geom
FROM d;

CREATE INDEX index_gist_t_layer_territoire_the_geom
  ON atlas.t_layer_territoire
  USING gist
  (the_geom);

CREATE UNIQUE INDEX t_layer_territoire_gid_idx
  ON atlas.t_layer_territoire
  USING btree (gid);


-- Rafraichissement des vues contenant les données de l'atlas
CREATE OR REPLACE FUNCTION atlas.refresh_materialized_view_ref_geo()
RETURNS VOID AS $$
BEGIN

  REFRESH MATERIALIZED VIEW atlas.t_layer_territoire;

END
$$ LANGUAGE plpgsql;
