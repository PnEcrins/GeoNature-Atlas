from marshmallow import (
    Schema,
    fields,
    validates_schema,
    ValidationError,
    validates_schema,
    EXCLUDE,
    post_load,
)
from marshmallow.validate import Regexp


MAP_1 = {
    "name": "OpenStreetMap",
    "layer": "//{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
    "attribution": "&copy OpenStreetMap",
}
MAP_2 = {
    "name": "OpenTopoMap",
    "layer": "//a.tile.opentopomap.org/{z}/{x}/{y}.png",
    "attribution": "&copy OpenStreetMap-contributors, SRTM | Style: &copy OpenTopoMap (CC-BY-SA)",
}

LANGUAGES = {
    "en": {
        "name": "English",
        "flag_icon": "flag-icon-gb",
        "months": [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ],
    },
    "fr": {
        "name": "Français",
        "flag_icon": "flag-icon-fr",
        "months": [
            "Janvier",
            "Février",
            "Mars",
            "Avril",
            "Mai",
            "Juin",
            "Juillet",
            "Août",
            "Septembre",
            "Octobre",
            "Novembre",
            "Decembre",
        ],
    },
    "it": {
        "name": "Italiano",
        "flag_icon": "flag-icon-it",
        "months": [
            "Gennaio",
            "Febbraio",
            "Marzo",
            "Aprile",
            "Maggio",
            "Giugno",
            "Luglio",
            "Agosto",
            "Settembre",
            "Ottobre",
            "Novembre",
            "Dicembre",
        ],
    },
}

orijime_default_translations = {
    "fr": {
        "consentModal": {
            "description": "",
        },
        "purposes": {"analytics": "Analyse", "security": "Sécurité"},
    },
    "en": {
        "consentModal": {
            "description": "This is an example of how to override an existing translation already used by Orejime",
        },
        "purposes": {"analytics": "Analytics", "security": "Security"},
    },
}


class SecretSchemaConf(Schema):
    class Meta:
        unknown = EXCLUDE

    SQLALCHEMY_DATABASE_URI = fields.String(
        required=True,
        validate=Regexp(
            "^postgresql:\/\/.*:.*@[^:]+:\w+\/\w+$",
            error="Database uri is invalid ex: postgresql://monuser:monpass@server:port/db_name",
        ),
    )
    GUNICORN_PORT = fields.Integer(load_default=8080)
    modeDebug = fields.Boolean(load_default=False)
    SECRET_KEY = fields.String(required=True)
    CACHE_TIMEOUT = fields.Number(load_default=3600)


class MapConfig(Schema):
    LAT_LONG = fields.List(fields.Float(), load_default=[44.7952, 6.2287])
    MIN_ZOOM = fields.Integer(load_default=1)
    MAX_BOUNDS = fields.List(fields.List(fields.Float()), load_default=[[-180, -90], [180, 90]])
    FIRST_MAP = fields.Dict(load_default=MAP_1)
    SECOND_MAP = fields.Dict(load_default=MAP_2)
    ZOOM = fields.Integer(load_default=10)
    STEP = fields.Integer(load_default=1)
    BORDERS_COLOR = fields.String(load_default="#000000")
    BORDERS_WEIGHT = fields.Integer(load_default=3)
    ENABLE_SLIDER = fields.Boolean(load_default=True)
    ENABLE_SCALE = fields.Boolean(load_default=True)
    MASK_STYLE = fields.Dict(
        load_default={"fill": False, "fillColor": "#020202", "fillOpacity": 0.3}
    )


class AtlasConfig(Schema):
    class Meta:
        unknown = EXCLUDE

    STRUCTURE = fields.String(load_default="Nom de la structure")
    NOM_APPLICATION = fields.String(load_default="Nom de l'application")
    CUSTOM_LOGO_LINK = fields.String(load_default="")
    URL_APPLICATION = fields.String(load_default="")
    DEFAULT_LANGUAGE = fields.String(load_default="fr")
    MULTILINGUAL = fields.Boolean(load_default=False)
    ORGANISM_MODULE = fields.Boolean(load_default=False)
    DISPLAY_OBSERVERS = fields.Boolean(load_default=True)
    GLOSSAIRE = fields.Boolean(load_default=False)
    IGNAPIKEY = fields.String(load_default="")
    AFFICHAGE_INTRODUCTION = fields.Boolean(load_default=True)
    AFFICHAGE_LOGOS_HOME = fields.Boolean(load_default=True)
    AFFICHAGE_FOOTER = fields.Boolean(load_default=True)
    AFFICHAGE_RGPD = fields.Boolean(load_default=True)
    OREJIME_APPS = fields.List(fields.Dict(), load_default=[])
    OREJIME_TRANSLATIONS = fields.Dict(load_default=orijime_default_translations)
    AFFICHAGE_STAT_GLOBALES = fields.Boolean(load_default=True)
    AFFICHAGE_DERNIERES_OBS = fields.Boolean(load_default=True)
    AFFICHAGE_EN_CE_MOMENT = fields.Boolean(load_default=True)
    AFFICHAGE_RANG_STAT = fields.Boolean(load_default=True)
    AFFICHAGE_NOUVELLES_ESPECES = fields.Boolean(load_default=True)
    AFFICHAGE_RECHERCHE_AVANCEE = fields.Boolean(load_default=False)
    AFFICHAGE_GRAPH_ALTITUDES = fields.Boolean(load_default=True)
    AFFICHAGE_GRAPH_PHENOLOGIE = fields.Boolean(load_default=True)

    RANG_STAT = fields.List(
        fields.Dict,
        load_default=[
            {"phylum": ["Arthropoda", "Mollusca"]},
            {"phylum": ["Chordata"]},
            {"regne": ["Plantae"]},
        ],
    )
    RANG_STAT_FR = fields.List(
        fields.String, load_default=["Faune invertébrée", "Faune vertébrée", "Flore"]
    )
    LIMIT_RANG_TAXONOMIQUE_HIERARCHIE = fields.Integer(load_default=13)
    LIMIT_FICHE_LISTE_HIERARCHY = fields.Integer(load_default=28)
    REMOTE_MEDIAS_URL = fields.String(load_default="http://mondomaine.fr/taxhub/")
    REMOTE_MEDIAS_PATH = fields.String(load_default="static/medias/")
    REDIMENSIONNEMENT_IMAGE = fields.Boolean(load_default=False)
    TAXHUB_URL = fields.String(required=False, load_default=None)
    ATTR_DESC = fields.Integer(load_default=100)
    ATTR_COMMENTAIRE = fields.Integer(load_default=101)
    ATTR_MILIEU = fields.Integer(load_default=102)
    ATTR_CHOROLOGIE = fields.Integer(load_default=103)
    ATTR_MAIN_PHOTO = fields.Integer(load_default=1)
    ATTR_OTHER_PHOTO = fields.Integer(load_default=2)
    ATTR_LIEN = fields.Integer(load_default=3)
    ATTR_PDF = fields.Integer(load_default=4)
    ATTR_AUDIO = fields.Integer(load_default=5)
    ATTR_VIDEO_HEBERGEE = fields.Integer(load_default=6)
    ATTR_YOUTUBE = fields.Integer(load_default=7)
    ATTR_DAILYMOTION = fields.Integer(load_default=8)
    ATTR_VIMEO = fields.Integer(load_default=9)
    PROTECTION = fields.Boolean(load_default=False)
    DISPLAY_PATRIMONIALITE = fields.Boolean(load_default=False)
    PATRIMONIALITE = fields.Dict(
        load_default={
            "label": "Patrimonial",
            "config": {
                "oui": {
                    "icon": "custom/images/logo_patrimonial.png",
                    "text": "Ce taxon est patrimonial",
                }
            },
        }
    )
    STATIC_PAGES = fields.Dict(
        load_default={
            "presentation": {
                "title": "Présentation de l'atlas",
                "picto": "fa-question-circle",
                "order": 0,
                "template": "static/custom/templates/presentation.html",
            }
        }
    )

    AFFICHAGE_MAILLE = fields.Boolean(load_default=False)
    ZOOM_LEVEL_POINT = fields.Integer(load_default=11)
    LIMIT_CLUSTER_POINT = fields.Integer(load_default=1000)
    NB_DAY_LAST_OBS = fields.String(load_default="7")
    NB_LAST_OBS = fields.Integer(load_default=100)
    TEXT_LAST_OBS = fields.String(
        load_default="Les observations des agents ces 7 derniers jours |"
    )
    MAP = fields.Nested(MapConfig, load_default=dict())
    # coupe le nom_vernaculaire à la 1ere virgule sur les fiches espèces
    SPLIT_NOM_VERN = fields.Boolean(load_default=True)
    INTERACTIVE_MAP_LIST = fields.Boolean(load_default=True)
    AVAILABLE_LANGUAGES = fields.Dict(load_default=LANGUAGES)
    # Flask parameter enabling auto reload of templates
    # (no need to restart the atlas service when updating templates)
    # Defaults to False to have the best performance in production
    TEMPLATES_AUTO_RELOAD = fields.Boolean(load_default=False)

    @validates_schema
    def validate_url_taxhub(self, data, **kwargs):
        """
        TAXHHUB_URL doit être rempli si REDIMENSIONNEMENT_IMAGE = True
        """
        if data["REDIMENSIONNEMENT_IMAGE"] and data["TAXHUB_URL"] is None:
            raise ValidationError(
                {"Le champ TAXHUB_URL doit être rempli si REDIMENSIONNEMENT_IMAGE = True"}
            )

    @post_load
    def post_load(self, data, **kwargs):
        # Set APPLICATION_ROOT Flask parameter (use for url_for etc...) https://flask.palletsprojects.com/en/stable/config/#APPLICATION_ROOT
        # the parameter is infered from URL_APPLICATION which is widely use in all the application
        url_application = data["URL_APPLICATION"]
        data["APPLICATION_ROOT"] = url_application if url_application != "/" else "/"
        return data
