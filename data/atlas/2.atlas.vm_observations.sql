--Toutes les observations
--DROP materialized view atlas.vm_observations;
CREATE MATERIALIZED VIEW atlas.vm_observations AS
    WITH centroid_synthese AS (
         SELECT st_centroid(cor.geom) AS geom_point,
            s.id_synthese AS id_observation,
		    s.date_min AS dateobs,
		    (s.altitude_min + s.altitude_max) / 2 AS altitude_retenue,
		    s.observers AS observateurs,
		    s.id_dataset,
            s.cd_nom,
            s.id_nomenclature_sensitivity,
            s.the_geom_point,
            cor.type_code
           FROM synthese.synthese s
             JOIN atlas.vm_cor_area_synthese cor ON cor.id_synthese = s.id_synthese AND cor.is_blurred_geom IS TRUE
        )
SELECT
    c.geom_point,
    c.id_observation,
    c.dateobs,
    c.altitude_retenue,
    c.observateurs,
    c.id_dataset,
    c.type_code,
    com.insee,
    tx.cd_ref,
    CASE
        WHEN sensi.cd_nomenclature::text = '0'::text
            THEN st_transform(c.the_geom_point, 3857)
            ELSE st_transform(c.geom_point, 3857)
        END AS the_geom_point,
    CASE
        WHEN sensi.cd_nomenclature::text = '0'::text
            THEN st_asgeojson(st_transform(c.the_geom_point, 4326))
            ELSE st_asgeojson(st_transform(c.geom_point, 4326))
        END AS geojson_point,
    sensi.cd_nomenclature AS cd_sensitivity
FROM centroid_synthese c
         JOIN atlas.vm_taxref tx ON tx.cd_nom = c.cd_nom
         LEFT JOIN synthese.t_nomenclatures sensi ON c.id_nomenclature_sensitivity = sensi.id_nomenclature
         JOIN atlas.l_communes com ON st_intersects(c.the_geom_point, com.the_geom);


-- --DROP materialized view atlas.vm_observations;
--  CREATE MATERIALIZED VIEW atlas.vm_observations AS
--  WITH centroid AS (
--          SELECT st_centroid(st_union(cor.geom)) AS geom_point,
--             s_1.id_synthese
--            FROM synthese.synthese s_1
--              JOIN atlas.vm_cor_area_synthese cor ON cor.id_synthese = s_1.id_synthese
--           WHERE cor.id_synthese = s_1.id_synthese AND cor.is_blurred_geom IS TRUE
--           GROUP BY s_1.id_synthese
--         )
--  SELECT s.id_synthese AS id_observation,
--    com.insee,
--     s.date_min AS dateobs,
--     (s.altitude_min + s.altitude_max) / 2 AS altitude_retenue,
--     s.observers AS observateurs,
--     tx.cd_ref,
--     s.id_dataset,
--     c.geom_point,
--        CASE
--           WHEN sensi.cd_nomenclature::text = '0'::text THEN st_transform(s.the_geom_point, 3857)
--            ELSE st_transform(c.geom_point, 3857)
--        END AS the_geom_point,
--       CASE
--           WHEN sensi.cd_nomenclature::text = '0'::text THEN st_asgeojson(st_transform(s.the_geom_point, 4326))
--           ELSE st_asgeojson(st_transform(c.geom_point, 4326))
--        END AS geojson_point,
--    sensi.cd_nomenclature AS cd_sensitivity
--    FROM synthese.synthese s
--      JOIN atlas.vm_taxref tx ON tx.cd_nom = s.cd_nom
--     LEFT JOIN synthese.t_nomenclatures sensi ON s.id_nomenclature_sensitivity = sensi.id_nomenclature
--  JOIN centroid c ON c.id_synthese = s.id_synthese
--  JOIN atlas.l_communes com ON st_intersects(s.the_geom_point, com.the_geom);


CREATE UNIQUE INDEX ON atlas.vm_observations (id_observation);
CREATE INDEX ON atlas.vm_observations (cd_ref);
CREATE INDEX ON atlas.vm_observations (insee);
CREATE INDEX ON atlas.vm_observations (altitude_retenue);
CREATE INDEX ON atlas.vm_observations (dateobs);
CREATE INDEX index_gist_vm_observations_the_geom_point ON atlas.vm_observations USING gist (the_geom_point);
