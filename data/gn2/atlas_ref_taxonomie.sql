--TAXONOMIE
--################################
--  Import FDW
--################################

CREATE SCHEMA IF NOT EXISTS taxonomie;

IMPORT FOREIGN SCHEMA taxonomie
LIMIT TO (
    taxonomie.taxref,
    taxonomie.cor_taxon_attribut,
    taxonomie.t_medias,
    taxonomie.bdc_statut_taxons,
    taxonomie.bdc_statut_cor_text_values,
    taxonomie.bdc_statut_text,
    taxonomie.bdc_statut_values,
    taxonomie.bdc_statut_type
)
FROM SERVER geonaturedbserver INTO taxonomie ;
