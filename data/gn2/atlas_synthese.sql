-- Creation d'une vue permettant de reproduire le contenu de la table du même nom dans les versions précédentes

CREATE VIEW synthese.syntheseff AS
WITH areas AS (
	SELECT DISTINCT ON (sa.id_synthese, t.type_code)
          sa.id_synthese, 
          sa.id_area, 
          a.centroid, 
          st_transform(centroid, 4326) as centroid_4326, 
          t.type_code
	FROM synthese.cor_area_synthese sa
	JOIN ref_geo.l_areas a ON sa.id_area = a.id_area
	JOIN ref_geo.bib_areas_types t ON a.id_type = t.id_type
	WHERE type_code IN ('M10', 'COM', 'DEP')
 ),  obs_data AS (
	SELECT s.id_synthese,
	    s.cd_nom,
		s.id_dataset,
	    s.date_min AS dateobs,
	    s.observers AS observateurs,
	    (s.altitude_min + s.altitude_max) / 2 AS altitude_retenue,
	    CASE
		WHEN dl.cd_nomenclature = '1' THEN
			(SELECT centroid_4326 FROM areas a WHERE a.id_synthese = s.id_synthese AND type_code = 'COM' LIMIT 1)
		WHEN dl.cd_nomenclature = '2' THEN
			(SELECT centroid_4326 FROM areas a WHERE a.id_synthese = s.id_synthese AND type_code = 'M10' LIMIT 1)
		WHEN dl.cd_nomenclature = '3' THEN
			(SELECT centroid_4326 FROM areas a WHERE a.id_synthese = s.id_synthese AND type_code = 'DEP' LIMIT 1)
		ELSE st_transform(s.the_geom_point, 4326)
	    END AS the_geom_point,
	    s.count_min AS effectif_total,
	    dl.cd_nomenclature::int as diffusion_level
	   FROM synthese.synthese s
	   LEFT OUTER JOIN synthese.t_nomenclatures dl ON s.id_nomenclature_diffusion_level = dl.id_nomenclature
	   LEFT OUTER JOIN synthese.t_nomenclatures st ON s.id_nomenclature_observation_status = st.id_nomenclature
	  WHERE (NOT dl.cd_nomenclature = '4'::text OR id_nomenclature_diffusion_level IS NULL)   -- Filtre données non diffusable code "4" ou pas de diffusion spécifiée
		AND st.cd_nomenclature = 'Pr'-- seulement les données présentes (status_observation = )
)
 SELECT d.id_synthese,
    d.id_dataset,
    d.cd_nom,
    d.dateobs,
    d.observateurs,
    d.altitude_retenue,
    d.the_geom_point,
    d.effectif_total,
    c.id_zone,
    diffusion_level
FROM obs_data d
JOIN atlas.l_communes c ON st_intersects(d.the_geom_point, c.the_geom);