BEGIN;

DROP MATERIALIZED VIEW IF EXISTS synthese.vm_cor_synthese_area;

CREATE MATERIALIZED VIEW synthese.vm_cor_synthese_area
TABLESPACE pg_default
AS
	SELECT DISTINCT ON (sa.id_synthese, t.type_code)
		sa.id_synthese,
		sa.id_area,
		st_transform(a.centroid, 4326) AS centroid_4326,
		t.type_code,
		a.area_code
	FROM synthese.cor_area_synthese AS sa
		 JOIN ref_geo.l_areas AS a
		 	ON (sa.id_area = a.id_area)
		 JOIN ref_geo.bib_areas_types AS t
		 	ON (a.id_type = t.id_type)
	WHERE t.type_code IN ('M10', 'COM', 'DEP')
WITH DATA;

GRANT SELECT ON TABLE synthese.vm_cor_synthese_area TO geonatatlas;

-- View indexes:
CREATE UNIQUE INDEX ON synthese.vm_cor_synthese_area (id_synthese, id_area);
CREATE INDEX ON synthese.vm_cor_synthese_area (type_code);


CREATE OR REPLACE FUNCTION atlas.get_blurring_centroid_geom_by_code(code CHARACTER VARYING, idSynthese INTEGER)
 RETURNS geometry
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
	-- Function which return the centroid for a sensitivity or diffusion_level code and a synthese id
	DECLARE centroid geometry;

	BEGIN
		SELECT INTO centroid csa.centroid_4326
		FROM synthese.vm_cor_synthese_area AS csa
		WHERE csa.id_synthese = idSynthese
			AND csa.type_code = (CASE WHEN code = '1' THEN 'COM' WHEN code = '2' THEN 'M10' WHEN code = '3' THEN 'DEP' END)
		LIMIT 1 ;

		RETURN centroid ;
	END;
$function$
;


DROP VIEW IF EXISTS synthese.syntheseff;


CREATE VIEW synthese.syntheseff AS
SELECT
	s.id_synthese,
	s.id_dataset,
	s.cd_nom,
	s.date_min AS dateobs,
	s.observers AS observateurs,
	(s.altitude_min + s.altitude_max) / 2 AS altitude_retenue,
	CASE
		WHEN (sens.cd_nomenclature::INT >= 1 AND sens.cd_nomenclature::INT <= 3 AND dl.cd_nomenclature::INT >= 1 AND dl.cd_nomenclature::INT <= 3) THEN
			CASE
				WHEN (sens.cd_nomenclature::INT >= dl.cd_nomenclature::INT) THEN (
					atlas.get_blurring_centroid_geom_by_code(sens.cd_nomenclature, s.id_synthese)
				)
				WHEN (sens.cd_nomenclature::INT < dl.cd_nomenclature::INT) THEN (
					atlas.get_blurring_centroid_geom_by_code(dl.cd_nomenclature, s.id_synthese)
				)
			END
		WHEN (sens.cd_nomenclature::INT >= 1 AND sens.cd_nomenclature::INT <= 3) AND (dl.cd_nomenclature::INT < 1 OR dl.cd_nomenclature::INT > 3) THEN (
			atlas.get_blurring_centroid_geom_by_code(sens.cd_nomenclature, s.id_synthese)
		)
		WHEN (dl.cd_nomenclature::INT >= 1 AND dl.cd_nomenclature::INT <= 3) AND (sens.cd_nomenclature::INT < 1 OR sens.cd_nomenclature::INT > 3) THEN (
			atlas.get_blurring_centroid_geom_by_code(dl.cd_nomenclature, s.id_synthese)
		)
		ELSE st_transform(s.the_geom_point, 4326)
	END AS the_geom_point,
	s.count_min AS effectif_total,
	areas.area_code AS insee,
	sens.cd_nomenclature AS sensitivity,
	dl.cd_nomenclature AS diffusion_level
FROM synthese.synthese s
	JOIN synthese.vm_cor_synthese_area AS areas
		ON (s.id_synthese = areas.id_synthese)
	LEFT JOIN synthese.t_nomenclatures AS sens
		ON (s.id_nomenclature_sensitivity = sens.id_nomenclature)
	LEFT JOIN synthese.t_nomenclatures AS dl
		ON (s.id_nomenclature_diffusion_level = dl.id_nomenclature)
	LEFT JOIN synthese.t_nomenclatures AS st
		ON (s.id_nomenclature_observation_status = st.id_nomenclature)
WHERE areas.type_code = 'COM'
	AND ( NOT dl.cd_nomenclature = '4' OR s.id_nomenclature_diffusion_level IS NULL )
	AND ( NOT sens.cd_nomenclature = '4' OR s.id_nomenclature_sensitivity IS NULL )
	AND st.cd_nomenclature = 'Pr' ;


-- Rafraichissement des vues contenant les données de l'atlas
CREATE OR REPLACE FUNCTION atlas.refresh_materialized_view_data()
RETURNS VOID AS $$
BEGIN

  REFRESH MATERIALIZED VIEW CONCURRENTLY synthese.vm_cor_synthese_area;

  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_observations;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_observations_mailles;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_mois;

  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_altitudes;

  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_taxons;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_cor_taxon_attribut;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_search_taxon;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_medias;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_taxons_plus_observes;

END
$$ LANGUAGE plpgsql;


-- TODO: ajouter au CHANGELOG la nécessité d'executer la commande SQL suivante
-- où il faut remplacer <my_reader_user> par la bonne valeur :
-- GRANT SELECT ON TABLE synthese.vm_cor_synthese_area TO <my_reader_user>;
-- Par défaut, ce script associe les droits à geonatatlas ligne 22.

-- TODO: ajouter au CHANGELOG la possiblité d'ajouter l'option FDW fetch_size
-- dans le cas des bases avec plusieurs millions d'obs dans la synthese :
-- ALTER SERVER geonaturedbserver OPTIONS (ADD fetch_size '1000000');

-- TODO: ajouter au CHANGELOG la nécessité de lancer le script : data/update/update_vm_observations.sql
-- pour prendre en compte le nouveau champ "sensitivity" de la vm_observations.
-- Ce champ n'est pas encore utilisé par l'interface...

COMMIT;