
--TAXONOMIE
--################################
--  Import FDW
--################################

CREATE SCHEMA IF NOT EXISTS taxonomie;

IMPORT FOREIGN SCHEMA taxonomie
LIMIT TO (taxonomie.taxref, taxonomie.bib_attributs, taxonomie.cor_taxon_attribut, taxonomie.t_medias)
FROM SERVER geonaturedbserver INTO taxonomie ;

ALTER TABLE taxonomie.taxref OWNER TO myuser;
GRANT ALL ON TABLE taxonomie.taxref TO myuser;

ALTER TABLE taxonomie.bib_attributs OWNER TO myuser;
GRANT ALL ON TABLE taxonomie.bib_attributs TO myuser;

ALTER TABLE taxonomie.cor_taxon_attribut OWNER TO myuser;
GRANT ALL ON TABLE taxonomie.cor_taxon_attribut TO myuser;

ALTER TABLE taxonomie.t_medias OWNER TO myuser;
GRANT ALL ON TABLE taxonomie.t_medias TO myuser;
