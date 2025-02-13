BEGIN;

CREATE MATERIALIZED VIEW atlas.vm_subdivided_area AS
	SELECT
		random() AS gid,
		'territory' AS code,
		st_subdivide(t.the_geom, 255) AS geom
	FROM atlas.t_layer_territoire AS t

  UNION

  SELECT
		random() AS gid,
		'territory_buffer-200' AS code,
		st_subdivide(st_buffer(t.the_geom::geography, -200)::geometry, 255) AS geom
	FROM atlas.t_layer_territoire AS t
WITH DATA;

CREATE UNIQUE INDEX ON atlas.vm_subdivided_area USING btree (gid);
CREATE INDEX ON atlas.vm_subdivided_area USING btree (code);
CREATE INDEX ON atlas.vm_subdivided_area USING gist (geom);


DROP FUNCTION IF EXISTS atlas.refresh_materialized_view_ref_geo;

CREATE OR REPLACE FUNCTION atlas.refresh_materialized_view_ref_geo()
RETURNS VOID AS $$
BEGIN

  REFRESH MATERIALIZED VIEW atlas.t_layer_territoire;
  REFRESH MATERIALIZED VIEW atlas.vm_subdivided_area;
  REFRESH MATERIALIZED VIEW atlas.l_communes;
  REFRESH MATERIALIZED VIEW atlas.vm_communes;

END
$$ LANGUAGE plpgsql;


-- TODO : ajouter ce script au futur script d'update de GeoNature Atlas.
-- TODO : trouver une solution pour pouvoir regénérer les VMs et table via les scripts présent dans data/atlas/.
-- TODO : il faudrait aussi relancer la génération de la VM vm_communes à l'aide du script '7.atlas.vm_communes.sql
-- TODO : il faudrait aussi relancer la génération de la table t_mailles_territoire à l'aide du script '12.atlas.t_mailles_teritoire.sql'


COMMIT;
