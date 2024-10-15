BEGIN;

DROP MATERIALIZED VIEW IF EXISTS atlas.vm_taxon_attribute ;

DROP FOREIGN TABLE IF EXISTS taxonomie.bib_attributs ;

DROP MATERIALIZED VIEW IF EXISTS atlas.vm_cor_taxon_attribut ;

IMPORT FOREIGN SCHEMA taxonomie
LIMIT TO (taxonomie.bib_attributs)
FROM SERVER geonaturedbserver INTO taxonomie ;

ALTER TABLE taxonomie.bib_attributs OWNER TO geonatatlas;
GRANT ALL ON TABLE taxonomie.bib_attributs TO geonatatlas;

CREATE MATERIALIZED VIEW atlas.vm_taxon_attribute AS
    SELECT cta.cd_ref,
        ba.nom_attribut AS code,
        ba.label_attribut AS title,
        CASE
            WHEN ba.type_attribut = 'text' AND ba.type_widget = 'select'
                THEN REPLACE(cta.valeur_attribut, '&', '|')
            ELSE cta.valeur_attribut
        END AS "value"
    FROM taxonomie.cor_taxon_attribut AS cta
        JOIN taxonomie.bib_attributs AS ba
            ON cta.id_attribut = ba.id_attribut
    WHERE ba.nom_attribut IN ('atlas_description', 'atlas_commentaire', 'atlas_milieu', 'atlas_chorologie')
        AND cta.valeur_attribut IS NOT NULL
        AND cta.valeur_attribut != '' ;

CREATE UNIQUE INDEX ON atlas.vm_taxon_attribute (cd_ref, code);


ALTER MATERIALIZED VIEW atlas.vm_taxon_attribute OWNER TO geonatatlas;
GRANT SELECT ON TABLE atlas.vm_taxon_attribute TO geonatatlas;


CREATE OR REPLACE FUNCTION atlas.refresh_materialized_view_data()
RETURNS VOID AS $$
BEGIN

  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_observations;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_observations_mailles;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_mois;

  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_altitudes;

  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_taxons;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_taxon_attribute;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_search_taxon;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_medias;
  REFRESH MATERIALIZED VIEW CONCURRENTLY atlas.vm_taxons_plus_observes;

END
$$ LANGUAGE plpgsql;


-- TODO: adapt taxonomie.bib_attributs owner if it's not default "geonatatlas"
-- TOOD: adapt if necessary "ba.nom_attribut IN ('atlas_description', 'atlas_commentaire', 'atlas_milieu', 'atlas_chorologie')"


COMMIT;
