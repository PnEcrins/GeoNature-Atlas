-- Communes contenues entièrement dans le territoire

CREATE MATERIALIZED VIEW atlas.vm_communes AS
SELECT c.insee,
c.commune_maj,
c.the_geom,
st_asgeojson(st_transform(c.the_geom, 4326)) as commune_geojson
FROM atlas.l_communes c
JOIN atlas.t_layer_territoire t ON ST_CONTAINS(ST_BUFFER(t.the_geom,200), c.the_geom);

CREATE UNIQUE INDEX ON atlas.vm_communes (insee);
CREATE INDEX index_gist_vm_communes_the_geom ON atlas.vm_communes USING gist (the_geom);
