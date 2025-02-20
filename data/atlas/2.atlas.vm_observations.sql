CREATE MATERIALIZED VIEW atlas.vm_observations AS
    WITH centroid_synthese AS (
         SELECT st_centroid(vla.the_geom) AS geom_point,
            s.id_synthese AS id_observation,
		    s.date_min AS dateobs,
		    (s.altitude_min + s.altitude_max) / 2 AS altitude_retenue,
		    s.observers AS observateurs,
		    s.id_dataset,
            s.cd_nom,
            s.id_nomenclature_sensitivity,
            s.the_geom_point,
            cor.type_code,
            cor.id_area
           FROM synthese.synthese s
             JOIN atlas.vm_cor_area_synthese cor ON cor.id_synthese = s.id_synthese
             JOIN ref_geo.bib_areas_types bat ON bat.type_code = cor.type_code
             JOIN synthese.t_nomenclatures tn ON tn.cd_nomenclature = cor.cd_nomenclature
             JOIN synthese.cor_sensitivity_area_type AS csat
               ON csat.id_nomenclature_sensitivity = tn.id_nomenclature
               AND csat.id_area_type = bat.id_type
             JOIN atlas.vm_l_areas vla ON vla.id_area=cor.id_area
        )
SELECT
    c.geom_point,
    c.id_observation,
    c.dateobs,
    c.altitude_retenue,
    c.observateurs,
    c.id_dataset,
    c.type_code,
    area.id_area,
    tx.cd_ref
FROM centroid_synthese c
         JOIN atlas.vm_taxref tx ON tx.cd_nom = c.cd_nom
         LEFT JOIN synthese.t_nomenclatures sensi ON c.id_nomenclature_sensitivity = sensi.id_nomenclature
         JOIN atlas.vm_l_areas area ON area.id_area = c.id_area;

CREATE UNIQUE INDEX ON atlas.vm_observations (id_observation);
CREATE INDEX ON atlas.vm_observations (cd_ref);
CREATE INDEX ON atlas.vm_observations (id_area);
CREATE INDEX ON atlas.vm_observations (altitude_retenue);
CREATE INDEX ON atlas.vm_observations (dateobs);
CREATE INDEX index_gist_vm_observations_geom_point ON atlas.vm_observations USING gist (geom_point);
