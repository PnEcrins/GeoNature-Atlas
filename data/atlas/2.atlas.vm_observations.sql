-- Fonctions

CREATE OR REPLACE FUNCTION atlas.is_blurred_area_type_by_diffusion_level(
  nomenclatureCode CHARACTER VARYING,
  areaTypeCode CHARACTER VARYING
)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $function$
  DECLARE isBlurred boolean;

  BEGIN
    SELECT INTO isBlurred
      CASE
        WHEN ( nomenclatureCode = '0' AND areaTypeCode = 'M5' ) THEN true
        WHEN ( nomenclatureCode = '1' AND areaTypeCode = 'M5' ) THEN true
        WHEN ( nomenclatureCode = '2' AND areaTypeCode = 'M5' ) THEN true
        WHEN ( nomenclatureCode = '3' AND areaTypeCode = 'M5' ) THEN true
        ELSE false
      END ;

    RETURN isBlurred ;
  END;
$function$
;

CREATE OR REPLACE FUNCTION atlas.is_blurred_area_type_by_sensitivity(
  nomenclatureCode CHARACTER VARYING,
  areaTypeCode CHARACTER VARYING
)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $function$
  DECLARE isBlurred boolean;

  BEGIN
    SELECT INTO isBlurred
      CASE
        WHEN ( nomenclatureCode = '1' AND areaTypeCode = 'M5' ) THEN true
        WHEN ( nomenclatureCode = '2' AND areaTypeCode = 'M5' ) THEN true
        WHEN ( nomenclatureCode = '3' AND areaTypeCode = 'M5' ) THEN true
        WHEN ( nomenclatureCode = '2.1' AND areaTypeCode = 'M1' ) THEN true
        WHEN ( nomenclatureCode = '2.2' AND areaTypeCode = 'M2' ) THEN true
        WHEN ( nomenclatureCode = '2.3' AND areaTypeCode = 'M5' ) THEN true
        WHEN ( nomenclatureCode = '2.4' AND areaTypeCode = 'M10' ) THEN true
        WHEN ( nomenclatureCode = '2.5' AND areaTypeCode = 'M20' ) THEN true
        WHEN ( nomenclatureCode = '2.6' AND areaTypeCode = 'M50' ) THEN true
        WHEN ( nomenclatureCode = '2.7' AND areaTypeCode = 'M50' ) THEN true
        ELSE false
      END ;

    RETURN isBlurred ;
  END;
$function$
;

CREATE OR REPLACE FUNCTION atlas.is_blurred_area_type(
  sensiCode CHARACTER VARYING,
  diffusionCode CHARACTER VARYING,
  areaTypeCode CHARACTER VARYING
)
RETURNS boolean
LANGUAGE plpgsql
IMMUTABLE
AS $function$
  DECLARE isBlurred boolean;

  BEGIN
    SELECT INTO isBlurred
      CASE
        WHEN (sensiCode::NUMERIC >= 1 AND sensiCode::NUMERIC <= 3 AND diffusionCode::NUMERIC >= 0 AND diffusionCode::NUMERIC <= 3) THEN
        CASE
            WHEN (sensiCode::NUMERIC >= diffusionCode::NUMERIC) THEN (
              atlas.is_blurred_area_type_by_sensitivity(sensiCode, areaTypeCode)
            )
            WHEN (sensiCode::NUMERIC < diffusionCode::NUMERIC) THEN (
              atlas.is_blurred_area_type_by_diffusion_level(diffusionCode, areaTypeCode)
            )
          END
        WHEN (sensiCode::NUMERIC >= 1 AND sensiCode::NUMERIC <= 3) AND (diffusionCode::NUMERIC > 4) THEN (
          atlas.is_blurred_area_type_by_sensitivity(sensiCode, areaTypeCode)
        )
        WHEN (diffusionCode::NUMERIC >= 0 AND diffusionCode::NUMERIC <= 3) AND (sensiCode::NUMERIC < 1) THEN (
          atlas.is_blurred_area_type_by_diffusion_level(diffusionCode, areaTypeCode)
        )
        ELSE false
      END;

    RETURN isBlurred ;
  END;
$function$
;

-- Toutes les correspondances observations à flouter et zones géographiques

CREATE MATERIALIZED VIEW atlas.vm_cor_synthese_area
TABLESPACE pg_default
AS
  SELECT
    sa.id_synthese,
    sa.id_area,
    st_transform(a.geom, 4326) AS geom_4326,
    t.type_code
  FROM synthese.synthese AS s
    JOIN synthese.cor_area_synthese AS sa
      ON (s.id_synthese = sa.id_synthese)
    JOIN synthese.t_nomenclatures AS sens
      ON (s.id_nomenclature_sensitivity = sens.id_nomenclature)
    JOIN synthese.t_nomenclatures AS dl
      ON (s.id_nomenclature_diffusion_level = dl.id_nomenclature)
    LEFT JOIN synthese.t_nomenclatures AS st
      ON (s.id_nomenclature_observation_status = st.id_nomenclature)
    LEFT JOIN synthese.t_nomenclatures AS va
      ON (s.id_nomenclature_valid_status = va.id_nomenclature)
    JOIN ref_geo.l_areas AS a
      ON (sa.id_area = a.id_area)
    JOIN ref_geo.bib_areas_types AS t
      ON (a.id_type = t.id_type)
  WHERE s.the_geom_point IS NOT NULL
    AND st.cd_nomenclature = 'Pr'
    AND dl.cd_nomenclature != '4'
    AND va.cd_nomenclature IN ('1', '2')
    AND sens.cd_nomenclature NOT IN ('4', '2.8')
    AND t.type_code IN ('M1', 'M2', 'M5', 'M10', 'M20', 'M50')
    AND atlas.is_blurred_area_type(sens.cd_nomenclature, dl.cd_nomenclature, t.type_code) = TRUE
WITH DATA;

CREATE UNIQUE INDEX i_vm_cor_synthese_area ON atlas.vm_cor_synthese_area USING btree (id_synthese, id_area);
CREATE INDEX ON atlas.vm_cor_synthese_area (type_code);


-- Toutes les observations

--DROP materialized view atlas.vm_observations;
CREATE MATERIALIZED VIEW atlas.vm_observations AS
WITH blurred_centroid AS (
  SELECT
    csa.id_synthese,
    st_centroid(st_union(csa.geom_4326)) AS geom_point
  FROM atlas.vm_cor_synthese_area AS csa
  GROUP BY csa.id_synthese
),
blurred_centroid_insee AS (
  SELECT
    bc.id_synthese,
    bc.geom_point,
    com.insee
  FROM blurred_centroid AS bc
      LEFT JOIN atlas.l_communes AS com
        ON (st_intersects(bc.geom_point, com.the_geom))
)
SELECT
  s.id_synthese AS id_observation,
  COALESCE(
    bci.insee,
    (SELECT insee FROM atlas.l_communes WHERE st_intersects(s.the_geom_point, the_geom) = TRUE)
  ) AS insee,
  s.date_min AS dateobs,
  s.observers AS observateurs,
  (s.altitude_min + s.altitude_max) / 2 AS altitude_retenue,
  CASE
    WHEN bci.geom_point IS NOT NULL THEN bci.geom_point
    ELSE s.the_geom_point
  END AS the_geom_point,
  s.count_min AS effectif_total,
  tx.cd_ref,
  CASE
    WHEN bci.geom_point IS NOT NULL THEN st_asgeojson(bci.geom_point)
    ELSE st_asgeojson(s.the_geom_point)
  END AS geojson_point,
  sens.cd_nomenclature AS sensitivity,
  dl.cd_nomenclature AS diffusion_level,
  s.id_dataset
FROM synthese.synthese AS s
  JOIN atlas.vm_taxref AS tx
    ON tx.cd_nom = s.cd_nom
  JOIN synthese.t_nomenclatures AS sens
    ON (s.id_nomenclature_sensitivity = sens.id_nomenclature)
  JOIN synthese.t_nomenclatures AS dl
    ON (s.id_nomenclature_diffusion_level = dl.id_nomenclature)
  JOIN synthese.t_nomenclatures AS st
    ON (s.id_nomenclature_observation_status = st.id_nomenclature)
  JOIN synthese.t_nomenclatures AS va
    ON (s.id_nomenclature_valid_status = va.id_nomenclature)
  LEFT JOIN blurred_centroid_insee AS bci
    ON bci.id_synthese = s.id_synthese
WHERE s.the_geom_point IS NOT NULL
  AND st.cd_nomenclature = 'Pr'
  AND dl.cd_nomenclature != '4'
  AND va.cd_nomenclature IN ('1', '2')
  AND sens.cd_nomenclature NOT IN ('4', '2.8') ;

CREATE UNIQUE INDEX ON atlas.vm_observations (id_observation);
CREATE INDEX ON atlas.vm_observations (cd_ref);
CREATE INDEX ON atlas.vm_observations (insee);
CREATE INDEX ON atlas.vm_observations (altitude_retenue);
CREATE INDEX ON atlas.vm_observations (dateobs);
CREATE INDEX index_gist_vm_observations_the_geom_point ON atlas.vm_observations USING gist (the_geom_point);
