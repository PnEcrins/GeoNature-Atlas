DROP TABLE IF EXISTS atlas.t_mailles_territoire;

CREATE TABLE atlas.t_mailles_territoire AS
    SELECT
        st_transform(a.geom, 4326) AS the_geom,
        st_asgeojson(st_transform(a.geom, 4326)) AS geojson_maille,
        a.id_area AS id_maille
    FROM ref_geo.l_areas AS a
        JOIN ref_geo.bib_areas_types AS t
            ON t.id_type = a.id_type
        JOIN atlas.t_layer_territoire AS l
            ON ST_intersects(a.geom, st_transform(l.the_geom, find_srid('ref_geo', 'l_areas', 'geom')))
    WHERE a.enable = true
        AND t.type_code = :type_maille ;

CREATE UNIQUE INDEX ON atlas.t_mailles_territoire
    USING btree (id_maille);
CREATE INDEX ON atlas.t_mailles_territoire
    USING spgist (the_geom);
