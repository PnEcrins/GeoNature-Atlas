CREATE MATERIALIZED VIEW atlas.vm_cor_area_synthese
TABLESPACE pg_default
AS
WITH info_tmp AS (
SELECT
    sa.id_synthese,
    sa.id_area,
    a.id_type,
    s.id_nomenclature_sensitivity
FROM synthese.synthese s
         JOIN synthese.cor_area_synthese sa ON sa.id_synthese = s.id_synthese
         JOIN ref_geo.l_areas a ON sa.id_area = a.id_area
         )
SELECT info.id_synthese,
       info.id_area,
       t.type_code,
       sensi.cd_nomenclature
                 FROM info_tmp info
                   JOIN ref_geo.bib_areas_types t ON info.id_type = t.id_type
                   LEFT JOIN synthese.t_nomenclatures sensi ON info.id_nomenclature_sensitivity = sensi.id_nomenclature

WITH DATA;
CREATE UNIQUE INDEX i_vm_cor_area_synthese ON atlas.vm_cor_area_synthese USING btree (id_synthese, id_area );

REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_cor_area_synthese;
