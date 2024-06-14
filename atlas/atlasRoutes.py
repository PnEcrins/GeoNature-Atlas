# -*- coding:utf-8 -*-
from urllib.parse import urlparse
from urllib.parse import urlunparse

from datetime import datetime, timedelta

from flask import Blueprint, g
from flask import (
    render_template,
    redirect,
    abort,
    current_app,
    make_response,
    request,
    url_for,
    session,
)

from atlas.env import db
from atlas import utils
from atlas.modeles.entities import vmTaxons, vmCommunes
from atlas.modeles.repositories import (
    vmOrganismsRepository,
    vmTaxonsRepository,
    vmObservationsRepository,
    vmAltitudesRepository,
    vmMoisRepository,
    vmTaxrefRepository,
    vmCommunesRepository,
    vmObservationsMaillesRepository,
    vmMedias,
    vmCorTaxonAttribut,
    vmTaxonsMostView,
    vmStatutBdcRepository,
)


# Adding functions for multilingual url process if MULTILINGUAL = True
main = Blueprint("main", __name__)  # , url_prefix='/<lang_code>')
if current_app.config["MULTILINGUAL"]:

    @main.url_defaults
    def add_language_code(endpoint, values):
        if "lang_code" in values or not g.get("lang_code", None):
            return
        # If endpoint expects lang_code, send it forward
        if current_app.url_map.is_endpoint_expecting(endpoint, "lang_code"):
            values["lang_code"] = g.lang_code

    @main.url_value_preprocessor
    def pull_lang_code(endpoint, values):
        if values is not None:
            # If no language code has been set, get the best language from the browser settings
            default_lang = request.accept_languages.best_match(current_app.config["LANGUAGES"])
            g.lang_code = values.pop("lang_code", default_lang)

    @main.before_request
    def redirect_default_language():
        if g.lang_code is None:
            if "language" in session:
                default_lang_code = session["language"]
            else:
                default_lang_code = request.accept_languages.best_match(
                    current_app.config["AVAILABLE_LANGUAGES"].keys(),
                    current_app.config["DEFAULT_LANGUAGE"],
                )
            view_args = request.view_args
            view_args["lang_code"] = default_lang_code
            return redirect(url_for(request.endpoint, **view_args))
        else:
            session["language"] = g.lang_code


@main.route(
    "/espece/" + current_app.config["REMOTE_MEDIAS_PATH"] + "<image>", methods=["GET", "POST"]
)
def especeMedias(image):
    return redirect(
        current_app.config["REMOTE_MEDIAS_URL"] + current_app.config["REMOTE_MEDIAS_PATH"] + image
    )


# Activating organisms sheets routes
if current_app.config["ORGANISM_MODULE"]:

    @main.route("/organism/<int:id_organism>", methods=["GET", "POST"])
    def ficheOrganism(id_organism):
        db_session = db.session
        connection = db.engine.connect()

        infos_organism = vmOrganismsRepository.statOrganism(connection, id_organism)

        stat = vmObservationsRepository.statIndex(connection)

        mostObsTaxs = vmOrganismsRepository.topObsOrganism(connection, id_organism)
        update_most_obs_taxons = []
        for taxon in mostObsTaxs:
            taxon_info = vmTaxrefRepository.searchEspece(connection, taxon["cd_ref"])
            photo = vmMedias.getFirstPhoto(
                connection, taxon["cd_ref"], current_app.config["ATTR_MAIN_PHOTO"]
            )
            taxon = {**taxon, **taxon_info["taxonSearch"]}
            taxon["photo"] = photo
            update_most_obs_taxons.append(taxon)
        stats_group = vmOrganismsRepository.getTaxonRepartitionOrganism(connection, id_organism)

        connection.close()
        db_session.close()

        return render_template(
            "templates/organismSheet/_main.html",
            nom_organism=infos_organism["nom_organism"],
            adresse_organism=infos_organism["adresse_organism"],
            cp_organism=infos_organism["cp_organism"],
            ville_organism=infos_organism["ville_organism"],
            tel_organism=infos_organism["tel_organism"],
            url_organism=infos_organism["url_organism"],
            url_logo=infos_organism["url_logo"],
            email_organism=infos_organism["email_organism"],
            nb_taxons=infos_organism["nb_taxons"],
            nb_obs=infos_organism["nb_obs"],
            stat=stat,
            mostObsTaxs=update_most_obs_taxons,
            stats_group=stats_group,
        )


@main.route(
    "/commune/" + current_app.config["REMOTE_MEDIAS_PATH"] + "<image>", methods=["GET", "POST"]
)
def communeMedias(image):
    return redirect(
        current_app.config["REMOTE_MEDIAS_URL"] + current_app.config["REMOTE_MEDIAS_PATH"] + image
    )


@main.route(
    "/liste/" + current_app.config["REMOTE_MEDIAS_PATH"] + "<image>", methods=["GET", "POST"]
)
def listeMedias(image):
    return redirect(
        current_app.config["REMOTE_MEDIAS_URL"] + current_app.config["REMOTE_MEDIAS_PATH"] + image
    )


@main.route(
    "/groupe/" + current_app.config["REMOTE_MEDIAS_PATH"] + "<image>", methods=["GET", "POST"]
)
def groupeMedias(image):
    return redirect(
        current_app.config["REMOTE_MEDIAS_URL"] + current_app.config["REMOTE_MEDIAS_PATH"] + image
    )


@main.route("/" + current_app.config["REMOTE_MEDIAS_PATH"] + "<image>", methods=["GET", "POST"])
def indexMedias(image):
    return redirect(
        current_app.config["REMOTE_MEDIAS_URL"] + current_app.config["REMOTE_MEDIAS_PATH"] + image
    )


@main.route("/", methods=["GET", "POST"])
def index():
    session = db.session
    connection = db.engine.connect()

    if current_app.config["AFFICHAGE_DERNIERES_OBS"]:
        if current_app.config["AFFICHAGE_MAILLE"]:
            current_app.logger.debug("start AFFICHAGE_MAILLE")
            observations = vmObservationsMaillesRepository.lastObservationsMailles(
                connection,
                str(current_app.config["NB_DAY_LAST_OBS"]) + " day",
                current_app.config["ATTR_MAIN_PHOTO"],
            )
            current_app.logger.debug("end AFFICHAGE_MAILLE")
        else:
            current_app.logger.debug("start AFFICHAGE_PRECIS")
            observations = vmObservationsRepository.lastObservations(
                connection,
                str(current_app.config["NB_DAY_LAST_OBS"]) + " day",
                current_app.config["ATTR_MAIN_PHOTO"],
            )
            current_app.logger.debug("end AFFICHAGE_PRECIS")
    else:
        observations = []

    if current_app.config["AFFICHAGE_EN_CE_MOMENT"]:
        current_app.logger.debug("start mostViewTaxon")
        mostViewTaxon = vmTaxonsMostView.mostViewTaxon(connection)
        current_app.logger.debug("end mostViewTaxon")
    else:
        mostViewTaxon = []

    if current_app.config["AFFICHAGE_RANG_STAT"]:
        current_app.logger.debug("start customStatMedia")
        customStatMedias = vmObservationsRepository.genericStatMedias(
            connection, current_app.config["RANG_STAT"]
        )
        current_app.logger.debug("end customStatMedia")
    else:
        customStatMedias = []

    if current_app.config["AFFICHAGE_NOUVELLES_ESPECES"]:
        lastDiscoveries = vmObservationsRepository.getLastDiscoveries(connection)
    else:
        lastDiscoveries = []

    connection.close()
    session.close()

    return render_template(
        "templates/home/_main.html",
        observations=observations,
        mostViewTaxon=mostViewTaxon,
        customStatMedias=customStatMedias,
        lastDiscoveries=lastDiscoveries,
    )


@main.route("/espece/<int(signed=True):cd_nom>", methods=["GET", "POST"])
def ficheEspece(cd_nom):
    db_session = db.session
    connection = db.engine.connect()

    # Get cd_ref from cd_nom
    cd_ref = vmTaxrefRepository.get_cd_ref(connection, cd_nom)

    # Redirect to cd_ref if cd_nom is a synonym. Redirection is better for SEO.
    if cd_ref != cd_nom:
        return redirect(url_for(request.endpoint, cd_nom=cd_ref))

    # Get data to render template
    taxon = vmTaxrefRepository.searchEspece(connection, cd_ref)
    altitudes = vmAltitudesRepository.getAltitudesChilds(connection, cd_ref)
    months = vmMoisRepository.getMonthlyObservationsChilds(connection, cd_ref)
    synonyme = vmTaxrefRepository.getSynonymy(connection, cd_ref)
    communes = vmCommunesRepository.getCommunesObservationsChilds(connection, cd_ref)
    taxonomyHierarchy = vmTaxrefRepository.getAllTaxonomy(db_session, cd_ref)
    firstPhoto = vmMedias.getFirstPhoto(connection, cd_ref, current_app.config["ATTR_MAIN_PHOTO"])
    photoCarousel = vmMedias.getPhotoCarousel(
        connection, cd_ref, current_app.config["ATTR_OTHER_PHOTO"]
    )
    videoAudio = vmMedias.getVideo_and_audio(
        connection,
        cd_ref,
        current_app.config["ATTR_AUDIO"],
        current_app.config["ATTR_VIDEO_HEBERGEE"],
        current_app.config["ATTR_YOUTUBE"],
        current_app.config["ATTR_DAILYMOTION"],
        current_app.config["ATTR_VIMEO"],
    )
    articles = vmMedias.getLinks_and_articles(
        connection, cd_ref, current_app.config["ATTR_LIEN"], current_app.config["ATTR_PDF"]
    )
    taxonDescription = vmCorTaxonAttribut.getAttributesTaxon(
        connection,
        cd_ref,
        current_app.config["ATTR_DESC"],
        current_app.config["ATTR_COMMENTAIRE"],
        current_app.config["ATTR_MILIEU"],
        current_app.config["ATTR_CHOROLOGIE"],
    )
    observers = vmObservationsRepository.getObservers(connection, cd_ref)

    organisms = vmOrganismsRepository.getListOrganism(connection, cd_ref)

    connection.close()
    db_session.close()

    return render_template(
        "templates/speciesSheet/_main.html",
        taxon=taxon,
        listeTaxonsSearch=[],
        observations=[],
        cd_ref=cd_ref,
        altitudes=altitudes,
        months=months,
        synonyme=synonyme,
        communes=communes,
        taxonomyHierarchy=taxonomyHierarchy,
        firstPhoto=firstPhoto,
        photoCarousel=photoCarousel,
        videoAudio=videoAudio,
        articles=articles,
        taxonDescription=taxonDescription,
        observers=observers,
        organisms=organisms,
    )


@main.route("/commune/<insee>", methods=["GET", "POST"])
def ficheCommune(insee):
    session = db.session
    connection = db.engine.connect()

    listTaxons = vmTaxonsRepository.getTaxonsCommunes(connection, insee)
    commune = vmCommunesRepository.getCommuneFromInsee(connection, insee)
    if current_app.config["AFFICHAGE_MAILLE"]:
        observations = vmObservationsMaillesRepository.lastObservationsCommuneMaille(
            connection, current_app.config["NB_LAST_OBS"], str(insee)
        )
    else:
        observations = vmObservationsRepository.lastObservationsCommune(
            connection, current_app.config["NB_LAST_OBS"], insee
        )

    surroundingAreas = []

    observers = vmObservationsRepository.getObserversCommunes(connection, insee)

    session.close()
    connection.close()

    return render_template(
        "templates/areaSheet/_main.html",
        sheetType="commune",
        surroundingAreas=surroundingAreas,
        listTaxons=listTaxons,
        areaInfos=commune,
        observations=observations,
        observers=observers,
        DISPLAY_EYE_ON_LIST=True,
        insee=insee,
    )


@main.route("/liste/<int(signed=True):cd_ref>", methods=["GET", "POST"])
def ficheRangTaxonomie(cd_ref):
    session = db.session
    connection = db.engine.connect()

    listTaxons = vmTaxonsRepository.getTaxonsChildsList(connection, cd_ref)
    referenciel = vmTaxrefRepository.getInfoFromCd_ref(session, cd_ref)
    taxonomyHierarchy = vmTaxrefRepository.getAllTaxonomy(session, cd_ref)
    observers = vmObservationsRepository.getObservers(connection, cd_ref)

    connection.close()
    session.close()

    return render_template(
        "templates/taxoRankSheet/_main.html",
        listTaxons=listTaxons,
        referenciel=referenciel,
        taxonomyHierarchy=taxonomyHierarchy,
        observers=observers,
        DISPLAY_EYE_ON_LIST=False,
    )


@main.route("/groupe/<groupe>", methods=["GET", "POST"])
def ficheGroupe(groupe):
    session = db.session
    connection = db.engine.connect()

    groups = vmTaxonsRepository.getAllINPNgroup(connection)
    listTaxons = vmTaxonsRepository.getTaxonsGroup(connection, groupe)
    observers = vmObservationsRepository.getGroupeObservers(connection, groupe)

    session.close()
    connection.close()

    return render_template(
        "templates/groupSheet/_main.html",
        listTaxons=listTaxons,
        referenciel=groupe,
        groups=groups,
        observers=observers,
        DISPLAY_EYE_ON_LIST=False,
    )


@main.route("/photos", methods=["GET", "POST"])
def photos():
    session = db.session
    connection = db.engine.connect()

    groups = vmTaxonsRepository.getINPNgroupPhotos(connection)

    session.close()
    connection.close()
    return render_template("templates/photoGalery/_main.html", groups=groups)


if current_app.config["AFFICHAGE_RECHERCHE_AVANCEE"]:

    @main.route("/recherche", methods=["GET"])
    def advanced_search():
        return render_template("templates/core/advanced_search.html")


@main.route("/<page>", methods=["GET", "POST"])
def get_staticpages(page):
    session = db.session
    if page not in current_app.config["STATIC_PAGES"]:
        abort(404)
    static_page = current_app.config["STATIC_PAGES"][page]
    session.close()
    return render_template(static_page["template"])


@main.route("/sitemap.xml", methods=["GET"])
def sitemap():
    """Generate sitemap.xml iterating over static and dynamic routes to make a list of urls and date modified"""
    pages = []
    ten_days_ago = datetime.now() - timedelta(days=10)
    session = db.session
    connection = db.engine.connect()
    url_root = request.url_root
    if url_root[-1] == "/":
        url_root = url_root[:-1]
    for rule in current_app.url_map.iter_rules():
        # check for a 'GET' request and that the length of arguments is = 0 and if you have an admin area that the rule does not start with '/admin'
        if "GET" in rule.methods and len(rule.arguments) == 0 and not rule.rule.startswith("/api"):
            pages.append([url_root + rule.rule, ten_days_ago])

    # get dynamic routes for blog
    species = session.query(vmTaxons.VmTaxons).order_by(vmTaxons.VmTaxons.cd_ref).all()
    for species in species:
        url = url_root + url_for("main.ficheEspece", cd_nom=species.cd_ref)
        modified_time = ten_days_ago
        pages.append([url, modified_time])

    municipalities = (
        session.query(vmCommunes.VmCommunes).order_by(vmCommunes.VmCommunes.insee).all()
    )
    for municipalitie in municipalities:
        url = url_root + url_for("main.ficheCommune", insee=municipalitie.insee)
        modified_time = ten_days_ago
        pages.append([url, modified_time])

    sitemap_template = render_template(
        "templates/sitemap.xml", pages=pages, url_root=url_root, last_modified=ten_days_ago
    )
    response = make_response(sitemap_template)
    response.headers["Content-Type"] = "application/xml"
    return response


@main.route("/robots.txt", methods=["GET"])
def robots():
    robots_template = render_template("static/custom/templates/robots.txt")
    response = make_response(robots_template)
    response.headers["Content-type"] = "text/plain"

    return response
