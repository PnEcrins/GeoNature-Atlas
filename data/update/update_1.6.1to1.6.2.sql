DROP MATERIALIZED VIEW IF EXISTS atlas.vm_observations_mailles;
DROP TABLE IF EXISTS atlas.t_mailles_territoire;


CREATE TABLE atlas.t_mailles_territoire AS
    SELECT
        st_transform(a.geom, 4326) AS the_geom,
        st_asgeojson(st_transform(a.geom, 4326)) AS geojson_maille,
        a.id_area AS id_maille
    FROM ref_geo.l_areas AS a
        JOIN ref_geo.bib_areas_types AS t
            ON t.id_type = a.id_type
        JOIN atlas.t_layer_territoire AS l
            ON ST_intersects(a.geom, st_transform(l.the_geom, find_srid('ref_geo', 'l_areas', 'geom')))
    WHERE a.enable = true
        AND t.type_code = :type_maille ;

CREATE UNIQUE INDEX ON atlas.t_mailles_territoire
    USING btree (id_maille);

CREATE INDEX ON atlas.t_mailles_territoire
    USING spgist (the_geom);


CREATE MATERIALIZED VIEW atlas.vm_observations_mailles AS
    SELECT
        o.cd_ref,
        date_part('year', o.dateobs) AS annee,
        m.id_maille,
        COUNT(o.id_observation) AS nbr
    FROM atlas.vm_observations AS o
        JOIN atlas.t_mailles_territoire AS m
            ON (o.the_geom_point && m.the_geom)
    GROUP BY o.cd_ref, date_part('year', o.dateobs), m.id_maille
    ORDER BY o.cd_ref, annee
WITH DATA;

CREATE UNIQUE INDEX ON atlas.vm_observations_mailles
    USING btree (cd_ref, annee, id_maille);

CREATE INDEX ON atlas.vm_observations_mailles
    USING btree (annee);

CREATE INDEX ON atlas.vm_observations_mailles
    USING btree (id_maille, cd_ref);


-- ISSUE #531 & #532
CREATE EXTENSION IF NOT EXISTS unaccent SCHEMA "public";

-- ISSUE #532
DROP MATERIALIZED VIEW IF EXISTS atlas.vm_search_taxon ;
CREATE MATERIALIZED VIEW atlas.vm_search_taxon AS
	WITH verna_names AS (
		SELECT DISTINCT
			cd_nom,
			lb_nom,
		    cd_ref,
		    STRING_TO_TABLE(nom_vern, ', ') AS nom_vern
		FROM atlas.vm_taxref
		WHERE nom_vern IS NOT NULL
			AND cd_nom = cd_ref
			AND nom_vern <> lb_nom
	),
	names AS (
		-- Chosen scinames
		SELECT
			cd_nom,
			cd_ref,
			lb_nom AS search_name,
		    CONCAT('<b>', REPLACE(nom_complet_html, lb_auteur, ''), '</b> ', lb_auteur) AS display_name
		FROM atlas.vm_taxref
		WHERE cd_nom = cd_ref

		UNION

		-- Synonym scinames
		SELECT
			t1.cd_nom,
			t1.cd_ref,
			t1.lb_nom AS search_name,
		    CONCAT(REPLACE(t1.nom_complet_html, t1.lb_auteur, ''), ' =  <b> ', REPLACE(t2.nom_complet_html, t2.lb_auteur, ''), '</b> ', t2.lb_auteur) AS display_name
		FROM atlas.vm_taxref AS t1
			JOIN atlas.vm_taxref AS t2
				ON t1.cd_ref = t2.cd_nom
		WHERE t1.cd_nom <> t1.cd_ref

		UNION

		-- Vernacular names
		SELECT
			v.cd_nom,
		    v.cd_ref,
		    v.nom_vern AS search_name,
		    CONCAT(v.nom_vern, ' =  <b> ', REPLACE(t.nom_complet_html, t.lb_auteur, ''), '</b> ', t.lb_auteur) AS display_name
		FROM verna_names AS v
			JOIN atlas.vm_taxref AS t
				ON t.cd_nom = v.cd_ref
		WHERE v.nom_vern <> v.lb_nom
	)
	SELECT ROW_NUMBER() OVER (ORDER BY n.cd_nom, n.cd_ref, n.search_name)::integer AS fid,
	  n.cd_nom,
	  n.cd_ref,
	  n.search_name,
	  n.display_name
	FROM atlas.vm_taxons AS t
		JOIN names AS n
			ON t.cd_ref = n.cd_ref ;

CREATE UNIQUE INDEX ON atlas.vm_search_taxon(fid);
CREATE INDEX ON atlas.vm_search_taxon(cd_nom);
CREATE INDEX ON atlas.vm_search_taxon(cd_ref);
CREATE INDEX trgm_idx ON atlas.vm_search_taxon USING GIST (search_name gist_trgm_ops);
CREATE UNIQUE INDEX ON atlas.vm_search_taxon (cd_nom, search_name);
