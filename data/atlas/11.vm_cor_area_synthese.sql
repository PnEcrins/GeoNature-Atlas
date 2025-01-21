IMPORT FOREIGN SCHEMA gn_synthese
    LIMIT TO (gn_synthese.cor_area_synthese)
FROM SERVER geonaturedbserver INTO synthese;

IMPORT FOREIGN SCHEMA gn_sensitivity
LIMIT TO (cor_sensitivity_area_type)  FROM SERVER geonaturedbserver INTO synthese;

CREATE MATERIALIZED VIEW atlas.vm_cor_area_synthese
TABLESPACE pg_default
AS
WITH sensitive_area_type AS (
    SELECT distinct(synthese.cor_sensitivity_area_type.id_area_type)
    FROM
        synthese.cor_sensitivity_area_type
), info_tmp AS (
    SELECT
        sa.id_synthese,
        sa.id_area,
        a.centroid,
        a.id_type,
        s.id_nomenclature_sensitivity,
        a.geom_4326,
        a.geom
    FROM
        synthese.synthese s
    JOIN
        synthese.cor_area_synthese sa
            ON sa.id_synthese = s.id_synthese
    JOIN
        ref_geo.l_areas a
            ON sa.id_area = a.id_area
    JOIN
            ref_geo.bib_areas_types t
                ON a.id_type = t.id_type
    JOIN sensitive_area_type sat ON t.id_type = sat.id_area_type  -- should be an area_type
    WHERE a.enable = TRUE
)
   SELECT
        info.id_synthese,
        info.id_area,
        info.centroid,
        info.geom,
        st_asgeojson(info.geom_4326) AS geojson_4326,
        st_transform(info.centroid,
        4326) AS centroid_4326,
        t.type_code,
        n.cd_nomenclature
        FROM
            info_tmp info
        JOIN
            ref_geo.bib_areas_types t
                ON info.id_type = t.id_type
        JOIN synthese.cor_sensitivity_area_type csat ON t.id_type = csat.id_area_type

        LEFT JOIN
            synthese.t_nomenclatures n
                ON info.id_nomenclature_sensitivity = n.id_nomenclature

WITH DATA;

CREATE UNIQUE INDEX i_vm_cor_area_synthese ON atlas.vm_cor_area_synthese USING btree (id_synthese, id_area );


SELECT count(*) FROM atlas.vm_cor_area_synthese;
