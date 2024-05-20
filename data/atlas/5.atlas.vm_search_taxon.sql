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
