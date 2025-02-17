CREATE MATERIALIZED VIEW atlas.vm_observations_mailles AS
SELECT
    o.cd_ref,
    date_part('year', o.dateobs) AS annee,
    cor.id_area as id_maille,
    COUNT(o.id_observation) AS nbr,
    ARRAY_AGG(o.id_observation) AS id_observations,
    cor.type_code
FROM atlas.vm_observations AS o
         LEFT JOIN atlas.vm_cor_area_synthese cor ON cor.id_synthese = o.id_observation
         JOIN ref_geo.bib_areas_types bat ON bat.type_code = cor.type_code
         JOIN synthese.t_nomenclatures tn ON tn.cd_nomenclature = cor.cd_nomenclature
         JOIN synthese.cor_sensitivity_area_type AS csat
              ON csat.id_nomenclature_sensitivity = tn.id_nomenclature
                  AND csat.id_area_type = bat.id_type
GROUP BY o.cd_ref, cor.id_area, cor.type_code, annee
ORDER BY o.cd_ref
    WITH DATA;

CREATE UNIQUE INDEX ON atlas.vm_observations_mailles
    USING btree (cd_ref, annee, id_maille);

CREATE INDEX ON atlas.vm_observations_mailles
    USING btree (annee);

CREATE INDEX ON atlas.vm_observations_mailles
    USING gin (id_observations);

CREATE INDEX ON atlas.vm_observations_mailles
    USING btree (id_maille, cd_ref);
