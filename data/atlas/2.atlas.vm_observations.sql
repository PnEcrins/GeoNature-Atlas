--Toutes les observations


        
CREATE MATERIALIZED VIEW atlas.vm_observations AS
    WITH centroid_synthese AS (
        -- donnee non sensibile ou id_nomenclature_sensi = NULL
        SELECT 
            s.id_synthese,
            s.the_geom_point as geom_point,
            nom.cd_nomenclature as cd_sensitivity
        FROM synthese.synthese s 
        LEFT JOIN synthese.t_nomenclatures nom ON nom.id_nomenclature = s.id_nomenclature_sensitivity
        WHERE nom.cd_nomenclature = '0' OR s.id_nomenclature_sensitivity IS NULL 
        UNION 
        -- données sensible
        SELECT 
            DISTINCT ON (s.id_synthese, cor.type_code) -- si l'observation est une ligne ou un polygone elle peut intersecté plusieur fois le même type de zonage
            s.id_synthese,
            st_centroid(st_transform(areas.the_geom, 4326)) as geom_point,
            tn.cd_nomenclature as cd_sensitivity
           FROM synthese.synthese s
            JOIN atlas.vm_cor_area_synthese cor ON cor.id_synthese = s.id_synthese
            JOIN ref_geo.bib_areas_types bat ON bat.type_code = cor.type_code
            JOIN synthese.t_nomenclatures tn ON tn.cd_nomenclature = cor.cd_nomenclature
            JOIN synthese.cor_sensitivity_area_type AS csat 
                ON csat.id_nomenclature_sensitivity = tn.id_nomenclature
                AND csat.id_area_type = bat.id_type
            JOIN atlas.vm_l_areas areas ON cor.id_area = areas.id_area
            WHERE cor.cd_nomenclature != '0'
        )
SELECT
    c.geom_point as the_geom_point,
    st_asgeojson(c.geom_point, 4326) as geojson_point,
    c.cd_sensitivity,
    s.id_synthese as id_observation,
    s.date_min as dateobs,
    (s.altitude_min + s.altitude_max) / 2 AS altitude_retenue,
    s.observers as observateurs	,
    s.id_dataset,
    --c.type_code,
    --com.insee,
    null as insee,
    tx.cd_ref
FROM synthese.synthese s
JOIN centroid_synthese c ON c.id_synthese = s.id_synthese
JOIN atlas.vm_taxref tx ON tx.cd_nom = s.cd_nom
--JOIN atlas.l_communes com ON st_intersects(s.the_geom_4326, com.the_geom) AND NOT st_touches(s.the_geom_4326, com.the_geom);
;

CREATE UNIQUE INDEX ON atlas.vm_observations (id_observation);
CREATE INDEX ON atlas.vm_observations (cd_ref);
CREATE INDEX ON atlas.vm_observations (insee);
CREATE INDEX ON atlas.vm_observations (altitude_retenue);
CREATE INDEX ON atlas.vm_observations (dateobs);
CREATE INDEX index_gist_vm_observations_the_geom_point ON atlas.vm_observations USING gist (the_geom_point);
