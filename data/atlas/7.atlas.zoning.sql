-- Zones contenues entièrement dans le territoire

CREATE TABLE atlas.zoning
(
    id serial PRIMARY KEY ,
    id_zone  int NOT NULL,
    area_name character varying(50),
    the_geom_4326 geometry,
    zone_geojson text,
    id_zoning_type int,
    id_parent int
);

-- Insertion par défaut des communes dans la table

INSERT INTO atlas.zoning (
    id_zone,
    area_name,
    the_geom_4326,
    zone_geojson,
    id_zoning_type
)
SELECT c.id_zone,
       c.area_name,
       st_transform(c.the_geom, 4326),
       st_asgeojson(st_transform(c.the_geom, 4326)) as zone_geojson,
       type.id_type
FROM atlas.l_communes c
         JOIN ref_geo.bib_areas_types type ON type.type_code = 'COM'
         JOIN atlas.t_layer_territoire t ON ST_INTERSECTS(t.geom, c.the_geom);

CREATE UNIQUE INDEX ON atlas.zoning (id);
CREATE INDEX index_gist_zoning_the_geom_4326 ON atlas.zoning USING gist (the_geom_4326);
