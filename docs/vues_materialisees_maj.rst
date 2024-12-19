============================================
VUES MATERIALISEES et MISE A JOUR DU CONTENU
============================================
.. image:: http://geonature.fr/img/logo-pne.jpg
    :target: http://www.ecrins-parcnational.fr

Introduction
============

Par défaut, la BDD a été conçue pour s'appuyer sur les données présentes dans GeoNature (https://github.com/PnEcrins/GeoNature).

Pour cela une BDD fille de GeoNature est créée avec les schémas utiles à l'atlas (``synthese``, ``taxonomie``, ``layers``), alimentée grace à un Foreign Data Wrapper (http://docs.postgresqlfr.org/9.2/sql-createforeigndatawrapper.html).

Cela permet de créer un lien dynamique entre les 2 bases de données. A chaque fois qu'une requête est éxecutée dans une table de l'atlas (BDD fille), le FDW permet d'interroger directement dans le BDD mère (celle de GeoNature) et ainsi d'avoir les données à jour en temps réel.

.. image :: images/bdd-fdw-vm.png

Néanmoins pour plus de généricité et permettre à une structure d'utiliser GeoNature-atlas sans disposer de GeoNature, l'application ne requête jamais directement dans ces schémas liés à GeoNature.

En effet elle requête uniquement sur des vues créées dans le schéma spécifique ``atlas``.

Ainsi ces vues peuvent être adaptées à volonté pour interroger d'autre sources de données que GeoNature, à partir du moment où elles retournent les mêmes champs.

Dans un soucis de performance et pour ne pas requêter en permanence sur la base mère GeoNature, nous avons mis en place des vues matérialisées (http://docs.postgresqlfr.org/9.3/rules-materializedviews.html) pour que les données soient précalculées, indéxées et présentes directement dans le schéma ``atlas``.

Vous pouvez alimenter l'atlas avec une autre source de données que GeoNature à condition de respecter le nom et le typage des champs retournés par la vue.

Ou vous pouvez simplement décider de l'adapter à votre GeoNature, par exemple en changeant l'``id_organism`` dont vous souhaitez afficher les données dans la condition WHERE de la vue ``atlas.vm_observations``.


Liste des vues matérialisées
============================

Seule ``atlas.vm_observations`` doit éventuellement être adaptée, les autres vues sont calculées à partir du contenu de cette vue et de la vue qui renvoie tout TAXREF.

Voir ``data/atlas.sql`` pour plus de précisions.

- ``atlas.vm_taxref`` qui renvoie toutes les données de ``taxonomie.taxref``.
Les champs de cette table sont ``cd_nom``, ``id_statut``, ``id_habitat``, ``id_rang``, ``regne``, ``phylum``, ``classe``, ``ordre``, ``famille``, ``cd_taxsup``, ``cd_ref``, ``lb_nom``, ``lb_auteur``, ``nom_complet``, ``nom_valide``, ``nom_vern``, ``nom_vern_eng``, ``group1_inpn``, ``group2_inpn``, ``nom_complet_html`` et ``cd_sup``.

- ``atlas.vm_observations`` qui renvoie la liste de toutes les observations.

- ``atlas.vm_taxons`` qui renvoie la liste des taxons observés au moins une fois sur le territoire (présents dans vm_observations).

- ``atlas.vm_search_taxon`` qui renvoie l'ensemble de tous les taxons + tous leurs synonymes pour le module de recherche d'une espèce.

- ``atlas.vm_altitudes`` qui renvoie le nombre d'observations pour chaque classe d'altitude et chaque taxon. Cette vue peut être personnalisée pour adapter les classes d'altitude (Voir ci-dessous : "Personnalisation de l'application").

- ``atlas.vm_mois`` qui renvoie le nombre d'observations pour chaque mois et chaque taxon.

- ``atlas.vm_phenologies`` qui renvoie le nombre d'observations pour chaque mois et chaque taxon.

- ``atlas.zoning`` qui renvoie les zones du territoire. A adapter si on n'a pas importé les communes dans ``atlas.l_communes``

- ``atlas.vm_medias`` qui renvoie tous les médias des taxons, sur la base du schéma ``taxonomie`` de TaxHub

- ``atlas.vm_cor_taxon_attribut`` qui renvoie les 4 descriptions des taxons (description, commentaire, milieux, chorologie, sur la base du schéma ``taxonomie`` de TaxHub

- ``atlas.vm_observations_mailles`` qui renvoie la liste de toute les observations agrégées par maille.

Pour créer la vue ``atlas.vm_observations_mailles``, remplacer le fichier ``data/ref/emprise_territoire.sample.shp`` par le fichier SHP de l'emprise de votre territore.
Il est necessaire de choisir la taille des mailles en fonction du niveeau de sensibilité (M1, M5, COM, 10, COM, DEP ou REG) en modifiant les variables ``sensibility0, sensibility1, sensibility2, sensibility3`` du fichier ``config/settings.ini``

**Modèle conceptuel du schéma `atlas`**

.. image :: images/mcd-atlas.png

**A partir de TAXREF et des observations, on génère la vue des taxons et on calcule des informations sur chaque taxon (carte des observations, graphiques, taxonomie...)**

.. image :: images/mcd-vm.png

**On peut aussi décrire chaque taxon (attributs) et y associer des médias (photos, audios, vidéos, articles...)**

.. image :: images/mcd-attributs-medias.png

**A partir des observations ponctuelles et des mailles, on créér une vue contenant le nombre d'observations de chaque espèce par maille**

.. image :: images/bdd-observations-mailles.png

En se basant sur ``saisie.saisie_observation`` de SICEN (en l'important dans la BDD de GeoNature-atlas ou en y accédant à distance avec un FDW), la vue ``atlas.vm_observations`` est à adapter comme ceci :

::

    CREATE MATERIALIZED VIEW atlas.vm_observations AS
     SELECT s.id_obs AS id_observation,
        s.code_insee AS insee,
        s.date_obs AS dateobs,
        REPLACE (md.liste_nom_auteur(observateur), ' & ', ', ') AS observateurs,
        s.elevation AS altitude_retenue,
        st_transform(st_setsrid(st_centroid(s.geom), 2154), 3857) AS the_geom_point,
        s.effectif AS effectif_total,
        tx.cd_ref,
        st_asgeojson(st_transform(st_setsrid(st_centroid(s.geom), 2154), 4326)) AS geojson_point
       FROM saisie.saisie_observation s
         JOIN taxonomie.taxref tx ON tx.cd_nom = s.cd_nom::integer AND s.cd_nom !~~* '%.%'::text
      WHERE s.diffusable = true AND s.date_obs IS NOT NULL;


Personnaliser les classes d'altitude
====================================

Pour modifier la vue ``vm_altitudes`` et l'adapter aux altitudes de votre territoire, vous devez modifier le contenu de la table ``atlas.bib_altitudes`` :

* Le champ ``id_altitude`` ne doit pas comporter de doublons et l'altitude la plus basse doit avoir l'``id_altitude`` = 1.

* L'amplitude des tranches altitudinales peut être personnalisée, ainsi que le nombre de tranches.

* Le champ ``label_altitude`` ne doit pas commencer par un chiffre. La méthode la plus générique consiste à générer automatiquement le contenu de ce champ :

  ::

        UPDATE atlas.bib_altitudes set label_altitude = '_' || altitude_min || '_' || altitude_max+1;

Dès que votre table ``atlas.bib_altitudes`` est complétée, vous pouvez mettre à jour la vue ``atlas.vm_altitudes`` :

::

    select atlas.create_vm_altitudes();

Redonnez les droits de lecture à votre utilisateur de BDD lecteur applicatif ``user_pg`` (``geonatatlas`` par défaut, à modifier éventuellement si vous l'avez nommé différemment) :

::

    GRANT SELECT ON TABLE atlas.vm_altitudes TO geonatatlas;

Redémarrer Apache pour Python reconnaisse le nouveau modèle de BDD :

::

    sudo apachectl restart


Mise à jour des vues matérialisées
==================================

Dans un soucis de performance, les données contenues dans les vues matérialisées n'intègrent pas en temps réel les mises à jour faites dans GeoNature. Pour cela ces vues doivent être actualisées grace à la fonction ``REFRESH MATERIALIZED VIEW`` ajouté dans le schéma ``public`` de PostgreSQL.

Une fonction, générée lors de la création de la BDD de GeoNature-atlas permet de mettre à jour toutes les vues matérialisées du schéma ``atlas``.

* Pour lancer manuellement cette fonction, ouvrez une console SQL et exécutez la requête suivante :

  ::

        SELECT RefreshAllMaterializedViews('atlas');

* Si vous utilisez une version de PostgreSQL inférieure à 9.4, le rafraichissement concurrent des vues matérialisées (https://www.postgresql.org/docs/9.4/static/sql-refreshmaterializedview.html) n'est pas possible. Dans ce cas, modifiez la fonction comme indiqué dans ses commentaires (https://github.com/PnX-SI/GeoNature-atlas/blob/master/data/atlas.sql#L424).

* Pour automatiser l'éxecution de cette fonction (toutes les heures dans cet exemple), ajoutez la dans le crontab de l'utilisateur ``postgres`` :

  ::

        sudo su postgres
        crontab -e

Ajouter la ligne suivante en prenant soin de mettre à jour les paramètres de connexion à la base de GeoNature-atlas :

::

    0 * * * * psql -d geonatureatlas -c "SELECT RefreshAllMaterializedViews('atlas');"

Pour enregistrer et sortir : ``Ctrl + O``, ENTER puis ``Ctrl + X``

Cette fonction rafraichit toutes les vues materialisées présentes dans le schéma ``atlas`` et ne tient pas compte de l'ordre du rafraichissement. Cette opération peut-être assez longue dans le cas où le réferentiel géographique est volumineux alors que celui-ci est relativement stable (peu de MAJ des communes ou du territoire). 

Dans ce cas, préferez un rafraichisement automatique uniquement des données : fonction ``atlas.refresh_materialized_view_data()``. Pour rafraichir les données géographiques, lancer ponctuellement la fonction ``atlas.refresh_materialized_view_ref_geo()``.
