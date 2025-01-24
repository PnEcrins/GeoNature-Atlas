============
INSTALLATION
============

.. image:: http://geonature.fr/img/logo-pne.jpg
    :target: http://www.ecrins-parcnational.fr

-----

Prérequis
=========

Application installable sur un serveur Debian 9, 10 et1 (seuls Debian 9 et 10 ont été prouvé et testé).

Ce serveur doit aussi disposer de :

- unzip (apt-get install unzip)
- sudo (apt-get install sudo)
- un utilisateur (``whoami`` dans cette documentation - ``whoami`` est une variable d'environnement Linux qui désigne l'utilisateur courant) appartenant au groupe ``sudo`` (pour pouvoir bénéficier des droits d'administrateur)

:notes:

    Si sudo n'est pas installé par défaut, voir https://www.privateinternetaccess.com/forum/discussion/18063/debian-8-1-0-jessie-sudo-fix-not-installed-by-default

:notes:

    GeoNature-atlas est susceptible de fonctionner sur d'autres OS (comme Ubuntu par exemple) mais cela n'a pas été testé.


**1. Mettre à jour les sources list**

Ces opérations doivent être faites en tant qu'administrateur (en sudo ou avec l'utilisateur ``root``).
Adapter à votre version d'OS (ici Debian 9 Stretch) :

::

    sudo echo "#" | sudo tee -a /etc/apt/sources.list
    sudo echo "#Ajout pour GeoNature-atlas" | sudo tee -a /etc/apt/sources.list
    sudo echo "deb http://httpredir.debian.org/debian stretch main" | sudo tee -a /etc/apt/sources.list
    sudo apt-get update
    sudo apt-get upgrade


**2. Récupérez la dernière version (X.Y.Z à remplacer par le numéro de version) de GeoNature-atlas (https://github.com/PnX-SI/GeoNature-atlas/releases)**

Ces opérations doivent être faites avec l'utilisateur courant (autre que ``root``), ``whoami`` dans l'exemple :

::

    cd /home/`whoami`
    wget https://github.com/PnX-SI/GeoNature-atlas/archive/X.Y.Z.zip


:note:

    Si la commande ``wget`` renvoie une erreur liée au certificat, installez le paquet ``ca-certificates`` (``sudo apt-get install ca-certificates``) puis relancer la commande ``wget`` ci-dessus.

Dézippez l'archive et la supprimer:

::

    unzip X.Y.Z.zip
    rm X.Y.Z.zip

Vous pouvez renommer le dossier qui contient l'application (dans un dossier ``/home/`whoami`/atlas/`` par exemple) :

::

    mv GeoNature-atlas-X.Y.Z atlas
    cd atlas

**3. Installation de l'environnement logiciel**

Le script ``install_env.sh`` va automatiquement installer les outils nécessaires à l'application si ils ne sont pas déjà sur le serveur :

- PostgreSQL
- PostGIS
- Apache 2
- Python 3 et GDAL

Lancer le script :

::

    ./install_env.sh


**4. Installation de la base de données**

Faites une copie du modèle de fichier de configuration de la BDD et de son installation automatique ``atlas/configuration/settings.ini.sample`` puis modifiez-le.

::

    cd /home/`whoami`/atlas/atlas/configuration
    cp settings.ini.sample settings.ini
    nano settings.ini

NOTES :

* Suivez bien les indications en commentaire dans ce fichier.

* Attention à ne pas mettre de 'quote' dans les valeurs, même pour les chaines de caractères.

* Dans le cas où vous souhaitez connecter l'atlas à une BDD distante de GeoNature v2, il faut au préalable créer un utilisateur spécifique pour l'atlas dans cette dernière (lecture seule). Pour cela se connecter en SSH au serveur hébergeant la BDD mère de GeoNature v2 et lancez les commandes suivantes en les adaptant. Faire ensuite correspondre avec les paramètres concernés dans le fichier ``settings.ini`` (``atlas_source_user`` et ``atlas_source_pass``) :

::

    sudo su - postgres
    psql
    CREATE USER geonatatlas WITH ENCRYPTED PASSWORD 'monpassachanger';
    \c geonature2db
    GRANT USAGE ON SCHEMA gn_synthese, ref_geo, ref_nomenclatures, taxonomie, utilisateurs, gn_meta TO geonatatlas;
    GRANT SELECT ON ALL TABLES IN SCHEMA gn_synthese, ref_geo, ref_nomenclatures, taxonomie, utilisateurs, gn_meta TO geonatatlas;
    \q
    exit

* GeoNature-atlas fonctionne avec des données géographiques qui doivent être fournies en amont (mailles, limite de territoire, limite de communes ou zone geographique). Vous avez la possibilité de récupérer ces données directement depuis le référentiel géographique de GeoNature si les données y sont présentes (``use_ref_geo_gn2=true``); ou de fournir des fichiers shapefiles (à mettre dans le répertoire ``data/ref``)

**Attention** si ``use_ref_geo_gn2=true``. Par défaut le ``ref_geo`` contient l'ensemble des communes de France, ce qui ralentit fortement l'installation lorsqu'on construit la table ``zoning`` (qui intersecte les communes avec les limites du territoire).

La table `zoning` doit être remplie en indicant l'identifiant de son type de 'zone' (table `bib_areas_types``).

Pour accelérer l'installation, vous pouvez "désactiver" certaines communes du ``ref_geo``, dont vous ne vous servez pas. Voir l'exemple de requête ci-dessous :

::

    UPDATE ref_geo.l_areas set enable = false where id_type = 25 AND id_area NOT in (
    select a.id_area from ref_geo.l_areas a
    join ref_geo.li_municipalities m ON a.id_area = m.id_area
    where insee_dep in ('MON_CODE_DEPARTEMENT', 'MON_CODE_DEPARTEMENT_BIS')
    )

Si votre territoire est celui de toute la France, préférez une installation en fournissant une couche SHP des communes (sans connection au ``ref_geo``)

:note:

    Le script d'installation automatique de la BDD ne fonctionne que pour une installation de celle-ci sur le même serveur que l'application (``localhost``) car la création d'une BDD requiert des droits non disponibles depuis un autre serveur. Dans le cas d'une BDD distante, adaptez les commandes du fichier ``install_db.sh`` en les exécutant une par une.

L'application se base entièrement sur des vues matérialisées. Par défaut, celles-ci sont proposées pour requêter les données dans une BDD GeoNature.

.. image :: images/geonature-atlas-schema-02.jpg

Cela laisse donc la possibilité de la connecter à une autre BDD en adaptant la vue ``atlas.vm_observations`` dans ``data/atlas/atlas.vm_observations.sql`` (en respectant impérativement les noms de champs).

.. image :: images/geonature-atlas-schema-01.jpg

Plus de détails sur les différentes vues matérialisées dans le fichier `<vues_materialisees_maj.rst>`_  qui indique aussi comment automatiser leur mise à jour.

Vous y trouverez aussi un exemple d'adaptation de la vue ``atlas.vm_observations``, basé sur une BDD SICEN.

Par ailleurs, si vous n'utilisez pas GeoNature, il vous faut installer TaxHub (https://github.com/PnX-SI/TaxHub/) ou au moins sa BDD, pour gérer les attributs (description, commentaire, milieu et chorologie) ainsi que les médias rattachés à chaque espèce (photos, videos, audios et articles). TaxHub dispose aussi de scripts permettant d'importer les médias des espèces depuis les photos libres de l'INPN (https://github.com/PnX-SI/TaxHub/tree/master/data/scripts/import_inpn_media) ou de Wikimedia (https://github.com/PnX-SI/TaxHub/tree/master/data/scripts/import_wikimedia_commons).
 
A noter aussi que si vous ne connectez pas l'atlas à une BDD GeoNature (``geonature_source=false``), une table exemple ``synthese.syntheseff`` comprenant 2 observations est créée. A vous d'adapter les vues après l'installation pour les connecter à vos données sources.

Lancez le fichier fichier d'installation de la base de données :


::

    cd /home/`whoami`/atlas
    ./install_db.sh


:notes:

    Vous pouvez consulter le log de cette installation de la base dans ``log/install_db.log`` et vérifier qu'aucune erreur n'est intervenue.

Vous pouvez alors modifier les vues, notamment ``atlas.vm_observations`` pour les adapter à votre contexte (ajouter les données partenaires, filtrer les espèces, limiter à un rang taxonomique...) ou le connecter à une autre BDD source (en important les données ou en s'y connectant en FDW).

Si vous voulez adapter le contenu des vues matérialisées, vous pouvez modifier le fichier ``data/atlas/atlas.vm_observations.sql`` puis relancer ce script global de la BDD.

Si vous souhaitez uniquement recréer la vue ``atlas.vm_observations`` et les 6 autres vues qui en dépendent vous pouvez utiliser le script ``data/update_vm_observations.sql``.


:notes:

    Un mécanisme de dégradation des données est fourni par défaut dans GeoNature-atlas, voir la documentation à ce sujet : `<degradation_donnees.rst>`_

**5. Installation de l'application**


**Lancez l'installation automatique de l'application :**

::

    ./install_app.sh

Configuration de l'application
==============================

Le fichier de configuration central de l'application est ``atlas/configuration/config.py``. Celui-ci est par défaut assez minimaliste. Il peut être completé par toute une série d'autres paramètres pour personnaliser le comportement de l'application. L'ensemble des paramètres disponibles sont présents dans le ficher ``atlas/configuration/config.py.example``.

- Vérifier que la variable ``SQLALCHEMY_DATABASE_URI`` contient les bonnes informations de connexion à la BDD
- Renseignez l'URL de l'application à partir de la racine du serveur WEB ('/atlas' ou '' par exemple)
- Renseignez les autres paramètres selon votre contexte

Après chaque modification de la configuration, relancer la commande ``sudo systemctl restart geonature-atlas`` pour qu'elles soient appliquées.

Pour améliorer les performances, le calcul des statistiques de la page d'accueil (statistiquess globale et statistique par rangs taxonomiques) sont mis en cache après leur premier chargement. Par defaut le cache dure 1h, il est possible de modifier ce paramètre via la variable `CACHE_TIMEOUT` (en seconde). Si on souhaite vider le cache, il est aussi possible de redémarrer l'application.

Customisation de l'application
==============================

En plus de la configuration, vous pouvez customiser l'application en modifiant et ajoutant des fichiers dans le répertoire ``static/custom/`` (css, templates, images).

L'atlas est fourni avec des variables CSS qui permettent de personnaliser facilement l'interface (changement des couleurs principales). Pour cela éditer les variables présentes dans le fichier ``static/custom/custom.css``. Les variables ``--main-color`` et ``second-color`` permettent de customiser l'atlas selon les couleurs de votre organism.

Vous pouvez aussi modifier ou ajouter des pages statiques de présentation, en plus de la page Présentation fournie par défaut. Pour cela, voir le paramètre ``STATIC_PAGES`` du fichier ``main/configuration/config.py``.

En mode point, il est possible de customiser l'affichage cartographique (modification de la couleur des points, modification de la légende) en éditant le fichier ``static/custom/maps-custom.js``. Par défaut l'affichage dissocie les données dégradées des données précises : voir `<degradation_donnees.rst>`_.

Tous les fichiers du dossier ``static`` peuvent être surcouchés en placant un fichier de même chemin dans le dossier ``static/custom``
- Par exemple pour remplacer le picto des mammifères il suffit d'ajouter un fichier ``static/custom/images/picto_Mammiferes.png``.

Configuration d'Apache
======================

Créez un virtualhost pour l'atlas :

::

    sudo nano /etc/apache2/sites-available/atlas.conf

Pour rendre l'application consultable comme un sous répertoire du serveur (http://monURL/atlas par exemple), copiez/collez-y ces lignes en renseignant le bon port :

::

    # Configuration GeoNature-atlas
    <Location /atlas>
        ProxyPass  http://127.0.0.1:8080/atlas
        ProxyPassReverse  http://127.0.0.1:8080/atlas
    </Location>
    #FIN Configuration GeoNature-atlas

Si l'atlas doit se trouver à la racine du serveur, copiez/coller ces lignes (NB les '/' à la fin des ProxyPass et ProxPassReverse)

::

	<Location />
   	    ProxyPass http://127.0.0.1:8080/
	    ProxyPassReverse http://127.0.0.1:8080/
 	 </Location>

Si l'atlas est associé à un domaine, ajoutez cette ligne au début du fichier :

::

    ServerName mondomaine.fr

* Activer les modules et redémarrer Apache :

::

    sudo a2enmod proxy
    sudo a2enmod proxy_http
    sudo apache2ctl restart

* Activez le virtualhost puis redémarrez Apache :

::

    sudo a2ensite atlas
    sudo apachectl restart

:notes:

    En cas d'erreur, les logs serveurs ne sont pas au niveau d'Apache (serveur proxy) mais de Gunicorn (serveur HTTP) dans ``/var/log/geonature-atlas.log``


Mise à jour de l'application
============================

- Télécharger puis dézipper la nouvelle version de l'atlas.

::

    cd /home/`whoami`

    wget https://github.com/PnX-SI/GeoNature-atlas/archive/X.Y.Z.zip
    unzip X.Y.Z
    rm X.Y.Z

- Renommer l'ancienne version de l'atlas puis la nouvelle version.

::

    mv /home/`whoami`/atlas/ /home/`whoami`/atlas_old/
    mv GeoNature-atlas-X.Y.Z /home/`whoami`/atlas/

- Copier ``atlas/configuration/settings.ini`` et ``atlas/configuration/config.py`` depuis l'ancienne version vers la nouvelle pour récupérer vos paramètres de configuration :

::

    cd atlas
    cp ../atlas_old/atlas/configuration/settings.ini atlas/configuration/settings.ini
    cp ../atlas_old/atlas/configuration/config.py atlas/configuration/config.py

- Copier le contenu du répertoire ``static/custom/`` depuis l'ancienne version vers la nouvelle pour récupérer toute votre customisation (CSS, templates, images...) :

::

    cp -aR ../atlas_old/atlas/static/custom/ ./atlas/static


Attention à bien lire les notes de chaque version, qui peuvent indiquer des opérations spécifiques à faire, notamment des nouveaux paramètres à ajouter dans votre configuration et/ou des modifications à appliquer dans la BDD.

- Relancez l'installation automatique de l'application :

::

    ./install_app.sh


Mise à jour des couches de référence
====================================

Limite du territoire ou communes.

Voir les parties concernées dans `install_db.sh <../install_db.sh#L65-L88>`_.


Accéder à votre BDD
===================

Par défaut un serveur PostgreSQL n'écoute et n'autorise des connexions que du serveur lui-même (localhost).
Il est possible mais déconseillé d'ouvrir l'accès à la BDD depuis une IP externe. Ou d'y accéder avec une connexion SSH (conseillé car plus sécurisé).

Voir https://github.com/PnX-SI/Ressources-techniques/blob/master/PostgreSQL/acces-bdd.rst

Développement
=============

**Installer les dépendances de dev**

::

    source venv/bin/activate
    pip install -r requirements-dev.txt

**Lancement de l'application**

Depuis la racine du dépôt:

::

    source venv/bin/activate
    flask run

Pour changer le port de l'application, désampler le fichier `atlas/.flaskenv.sample`` et éditer la variable `FLASK_RUN_PORT`

**Technologies**

.. image :: images/dev-technologies.png

**Architecture du code (MVC)**

.. image :: images/dev-architecture-code-mvc.png

**Architecture de l'application**

.. image :: images/dev-architecture-application.png

Des données sont renvoyées aux templates par l'ORM, d'autres le sont sous forme d'API (fichiers JSON chargés en AJAX) pour charger certaines pages plus rapidement (observations sur les fiches espèces et auto-complétion de la recherche) :

Pour en savoir plus, consultez le document `<vues_materialisees_maj.rst>`_ ainsi que le rapport de stage de Théo Lechemia (https://github.com/PnX-SI/GeoNature-atlas/blob/master/docs/2016-09-30-rapport_stage_Theo-Lechemia.pdf) ou sa présentation (https://github.com/PnX-SI/GeoNature-atlas/blob/master/docs/2016-09-soutenance-Theo-Lechemia.pdf)


