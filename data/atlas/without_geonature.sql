CREATE TABLE synthese.syntheseff(
    id_synthese serial PRIMARY KEY,
    id_organism integer DEFAULT 2,
    id_dataset integer,
    cd_nom integer,
    insee character(5),
    dateobs date NOT NULL DEFAULT now(),
    observateurs character varying(255),
    altitude_retenue integer,
    supprime boolean DEFAULT false,
    the_geom_point geometry('POINT',4326),
    effectif_total integer,
    diffusion_level integer,
    sensitivity integer
);

INSERT INTO synthese.syntheseff
(cd_nom, insee, observateurs, altitude_retenue, the_geom_point, effectif_total, diffusion_level, sensitivity)
VALUES (67111, 05122, 'Mon observateur', 1254, ST_SetSRID( ST_Point( 6, 42.315), 4326), 3, 5, 0);
INSERT INTO synthese.syntheseff
(cd_nom, insee, observateurs, altitude_retenue, the_geom_point, effectif_total, diffusion_level, sensitivity)
VALUES (67111, 05122, 'Mon observateur 3', 940, ST_SetSRID( ST_Point( 6.1, 42.315), 4326), 2, 5, 0);


CREATE TABLE gn_meta.cor_dataset_actor (
    id_cda int4 NULL, -- id cadre d'acquisition (inutilisé aujourd'huit)
    id_dataset int4 NOT NULL,
    id_role int4  NULL,
    id_organism int4 NULL
);

CREATE TABLE utilisateurs.bib_organismes (
    id_organisme int4 NOT NULL,
    uuid_organisme uuid NULL,
    nom_organisme varchar(100) NOT NULL,
    adresse_organisme varchar(128) NULL,
    cp_organisme varchar(5)  NULL,
    ville_organisme varchar(100) NULL,
    tel_organisme varchar(14) NULL,
    email_organisme varchar(100)  NULL,
    url_organisme varchar(255) NULL,
    url_logo varchar(255) NULL
);
