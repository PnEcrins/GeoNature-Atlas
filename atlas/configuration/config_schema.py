from marshmallow import (
    Schema,
    fields,
    validates_schema,
    ValidationError,
    validates_schema,
)
from marshmallow.validate import OneOf, Regexp


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


class SecretSchemaConf(Schema):
    database_connection = fields.String(
        required=True,
        validate=Regexp(
            "^postgresql:\/\/.*:.*@[^:]+:\w+\/\w+$",
            0,
            """Database uri is invalid ex:
             postgresql://monuser:monpass@server:port/db_name""",
        ),
    )
    GUNICORN_PORT = fields.Integer(missing=8080)


class MapConfig(Schema):
    LAT_LONG = fields.List(fields.Float(), missing=[44.7952, 6.2287])
    MIN_ZOOM = fields.Integer(missing=1)
    MAX_BOUNDS = fields.List(
        fields.List(fields.Float()), missing=[[-180, -90], [180, 90]]
    )
    FIRST_MAP = fields.Dict(missing=MAP_1)
    SECOND_MAP = fields.Dict(missing=MAP_2)
    ZOOM = fields.Integer(missing=10)
    STEP = fields.Integer(missing=1)
    BORDERS_COLOR = fields.String(missing="#000000")
    BORDERS_WEIGHT = fields.Integer(missing=3)
    ENABLE_SLIDER = fields.Boolean(missing=True)


class StatConfig(Schema):
    DISPLAY_CLASSE_ALTITUDE = fields.Boolean(missing=True)
    DISPLAY_OBS_MENSUELLE = fields.Boolean(missing=True)


class AtlasConfig(Schema):
    modeDebug = fields.Boolean(missing=False)
    STRUCTURE = fields.String(missing="Nom de la structure")
    NOM_APPLICATION = fields.String(missing="Nom de l'application")
    URL_APPLICATION = fields.String(missing="")
    ID_GOOGLE_ANALYTICS = fields.String(missing="UA-xxxxxxx-xx")
    GLOSSAIRE = fields.Boolean(missing=False)
    IGNAPIKEY = fields.String(missing="")
    AFFICHAGE_INTRODUCTION = fields.Boolean(missing=True)
    AFFICHAGE_FOOTER = fields.Boolean(missing=False)
    AFFICHAGE_STAT_GLOBALES = fields.Boolean(missing=True)
    AFFICHAGE_DERNIERES_OBS = fields.Boolean(missing=True)
    AFFICHAGE_EN_CE_MOMENT = fields.Boolean(missing=True)
    AFFICHAGE_RANG_STAT = fields.Boolean(missing=True)
    RANG_STAT = fields.List(
        fields.Dict,
        missing=[
            {"phylum": ["Arthropoda", "Mollusca"]},
            {"phylum": ["Chordata"]},
            {"regne": ["Plantae"]},
        ],
    )
    RANG_STAT_FR = fields.List(
        fields.String, missing=["Faune invertébrée", "Faune vertébrée", "Flore"]
    )
    LIMIT_RANG_TAXONOMIQUE_HIERARCHIE = fields.Integer(missing=13)
    LIMIT_FICHE_LISTE_HIERARCHY = fields.Integer(missing=28)
    REMOTE_MEDIAS_URL = fields.String(missing="http://mondomaine.fr/taxhub/")
    REMOTE_MEDIAS_PATH = fields.String(missing="static/medias/")
    REDIMENSIONNEMENT_IMAGE = fields.Boolean(missing=False)
    TAXHUB_URL = fields.String(required=False, missing=None)
    ATTR_DESC = fields.Integer(missing=100)
    ATTR_COMMENTAIRE = fields.Integer(missing=101)
    ATTR_MILIEU = fields.Integer(missing=102)
    ATTR_CHOROLOGIE = fields.Integer(missing=103)
    ATTR_MAIN_PHOTO = fields.Integer(missing=1)
    ATTR_OTHER_PHOTO = fields.Integer(missing=2)
    ATTR_LIEN = fields.Integer(missing=3)
    ATTR_PDF = fields.Integer(missing=4)
    ATTR_AUDIO = fields.Integer(missing=5)
    ATTR_VIDEO_HEBERGEE = fields.Integer(missing=6)
    ATTR_YOUTUBE = fields.Integer(missing=7)
    ATTR_DAILYMOTION = fields.Integer(missing=8)
    ATTR_VIMEO = fields.Integer(missing=9)
    PROTECTION = fields.Boolean(missing=False)
    DISPLAY_PATRIMONIALITE = fields.Boolean(missing=False)
    PATRIMONIALITE = fields.Dict(
        missing={
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
        missing={
            "presentation": {
                "title": "Présentation de l'atlas",
                "picto": "glyphicon-question-sign",
                "order": 0,
                "template": "static/custom/templates/presentation.html",
            }
        }
    )

    AFFICHAGE_MAILLE = fields.Boolean(missing=False)
    ZOOM_LEVEL_POINT = fields.Integer(missing=11)
    LIMIT_CLUSTER_POINT = fields.Integer(missing=1000)
    NB_DAY_LAST_OBS = fields.String(missing="7 day")
    NB_LAST_OBS = fields.Integer(missing=100)
    TEXT_LAST_OBS = fields.String(
        missing="Les observations des agents ces 7 derniers jours |"
    )
    TYPE_DE_REPRESENTATION_MAILLE = fields.String(
        validate=OneOf(["LAST_OBS", "NB_OBS"])
    )

    MAP = fields.Nested(MapConfig, missing=dict())
    STAT = fields.Nested(StatConfig, missing=dict())
    
    # Specify how communes are ordered
    #   if true by length else by name
    ORDER_COMMUNES_BYLENGTH = fields.Boolean(missing=False)
    # coupe le nom_vernaculaire à la 1ere virgule sur les fiches espèces
    SPLIT_NOM_VERN = fields.Integer(missing=True)

    @validates_schema
    def validate_url_taxhub(self, data):
        """
            TAXHHUB_URL doit être rempli si REDIMENSIONNEMENT_IMAGE = True
        """
        if data["REDIMENSIONNEMENT_IMAGE"] and data["TAXHUB_URL"] is None:
            raise ValidationError(
                {
                    "Le champ TAXHUB_URL doit être rempli si REDIMENSIONNEMENT_IMAGE = True"
                }
            )

