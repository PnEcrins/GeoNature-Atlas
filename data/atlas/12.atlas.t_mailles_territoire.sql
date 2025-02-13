DROP TABLE IF EXISTS atlas.t_mailles_territoire;

-- MV for having only meshs of the territory
CREATE TABLE atlas.t_mailles_territoire AS
    WITH areas AS (
        SELECT
            id_area,
            st_transform(c.geom, 4326) AS geom,
            geojson_4326 AS geojson
        FROM ref_geo.l_areas AS c
            JOIN ref_geo.bib_areas_types AS t
                ON t.id_type = c.id_type
        WHERE c.enable = true
            AND t.type_code = :type_maille
    )
    SELECT
        a.geom AS the_geom,
        a.geojson AS geojson_maille,
        a.id_area AS id_maille
    FROM areas AS a
    WHERE EXISTS (
        SELECT 'X'
        FROM atlas.vm_subdivided_area AS sa
        WHERE sa.code = 'territory'
            AND st_intersects(a.geom, sa.geom)
    );

CREATE UNIQUE INDEX ON atlas.t_mailles_territoire USING btree (id_maille);
CREATE INDEX ON atlas.t_mailles_territoire USING spgist (the_geom);