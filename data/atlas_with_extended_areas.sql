--################################
--###
--################################

-- Suppression de la VM atlas.vm_bib_areas_types si existe
DROP MATERIALIZED VIEW IF EXISTS atlas.vm_bib_areas_types CASCADE;

CREATE MATERIALIZED VIEW atlas.vm_bib_areas_types AS
SELECT t.id_type, t.type_code, t.type_name, t.type_desc
FROM ref_geo.bib_areas_types t
WHERE
    type_code IN ('M10', 'COM', 'ZNIEFF1', 'ZNIEFF2');

CREATE INDEX ON atlas.vm_bib_areas_types(id_type);
CREATE INDEX ON atlas.vm_bib_areas_types(type_code);
CREATE INDEX ON atlas.vm_bib_areas_types(type_name);

-- Suppression si temporaire des zones la table existe
DROP MATERIALIZED VIEW IF EXISTS atlas.vm_l_areas;


-- création de la vm l_areas à partir des communes du ref_geo
CREATE MATERIALIZED VIEW atlas.vm_l_areas AS
SELECT
    a.id_area                                AS id_area
  , a.area_code                              AS area_code
  , a.area_name                              AS area_name
  , a.id_type                                AS id_type
  , st_transform(a.geom, 4326)               AS the_geom
  , st_asgeojson(st_transform(a.geom, 4326)) AS area_geojson
FROM
    ref_geo.l_areas a
        JOIN atlas.vm_bib_areas_types t
             ON t.id_type = a.id_type
WHERE
    enable = TRUE AND
    type_code IN ('M10', 'COM', 'ZNIEFF1', 'ZNIEFF2')
WITH DATA;

CREATE UNIQUE INDEX vm_l_areas_id_area_idx
    ON atlas.vm_l_areas(id_area);

CREATE INDEX vm_l_areas_the_geom_gidx
    ON atlas.vm_l_areas
        USING gist
        (the_geom);

CREATE INDEX vm_l_areas_area_name_idx
    ON atlas.vm_l_areas(area_code);

--Table des correspondances observations <> zonages;

DROP MATERIALIZED VIEW IF EXISTS atlas.vm_cor_area_observation;

CREATE MATERIALIZED VIEW atlas.vm_cor_area_observation AS
SELECT cas.id_synthese AS id_observation, cas.id_area
FROM
    synthese.cor_area_synthese cas
        JOIN atlas.vm_l_areas la ON cas.id_area = la.id_area;

CREATE UNIQUE INDEX ON atlas.vm_cor_area_observation(id_observation, id_area);

GRANT SELECT ON TABLE atlas.vm_bib_areas_types TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_l_areas TO my_reader_user;
GRANT SELECT ON TABLE atlas.vm_cor_area_observation TO my_reader_user;



