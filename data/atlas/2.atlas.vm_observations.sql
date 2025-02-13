--Toutes les observations

--DROP materialized view atlas.vm_observations;
CREATE MATERIALIZED VIEW atlas.vm_observations AS
    SELECT s.id_synthese AS id_observation,
        s.insee,
        s.dateobs,
        s.observateurs,
        s.altitude_retenue,
        s.the_geom_point,
        s.effectif_total,
        tx.cd_ref,
        st_asgeojson(s.the_geom_point) as geojson_point,
        s.sensitivity,
        s.diffusion_level,
        s.id_dataset
    FROM synthese.syntheseff s
      LEFT JOIN atlas.vm_taxref tx ON tx.cd_nom = s.cd_nom
    WITH DATA;

CREATE UNIQUE INDEX ON atlas.vm_observations (id_observation);
CREATE INDEX ON atlas.vm_observations (cd_ref);
CREATE INDEX ON atlas.vm_observations (insee);
CREATE INDEX ON atlas.vm_observations (altitude_retenue);
CREATE INDEX ON atlas.vm_observations (dateobs);
CREATE INDEX index_gist_vm_observations_the_geom_point ON atlas.vm_observations USING gist (the_geom_point);
