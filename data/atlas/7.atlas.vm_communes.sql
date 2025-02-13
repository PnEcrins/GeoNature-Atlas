-- Communes contenues entièrement dans le territoire

CREATE MATERIALIZED VIEW atlas.vm_communes AS
    SELECT
        c.insee,
        c.commune_maj,
        c.the_geom,
        st_asgeojson(st_transform(c.the_geom, 4326)) AS commune_geojson
    FROM atlas.l_communes AS c
    WHERE EXISTS (
            SELECT 'X'
            FROM atlas.vm_subdivided_area AS sa
            WHERE sa.code = 'territory_buffer-200'
                AND st_intersects(sa.geom, c.the_geom)
        )
    WITH DATA;

CREATE UNIQUE INDEX ON atlas.vm_communes (insee) ;
CREATE INDEX index_gist_vm_communes_the_geom ON atlas.vm_communes USING gist (the_geom) ;

