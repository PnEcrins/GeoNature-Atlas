import os
import copy
from flask import Flask, request, session, redirect, url_for, g
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel, format_date, gettext, ngettext, get_locale
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.shared_data import SharedDataMiddleware
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

from atlas.configuration.config_parser import valid_config_from_dict
from atlas.configuration.config_schema import AtlasConfig, SecretSchemaConf
from atlas.env import atlas_static_folder, atlas_template_folder, atlas_config_file_path, db, cache

compress = Compress()


def create_app():
    """
    renvoie une instance de l'app Flask
    """

    app = Flask(__name__, template_folder=atlas_template_folder, static_folder=atlas_static_folder)
    # push the config in app config at 'PUBLIC' key
    app.config.from_pyfile(str(atlas_config_file_path))

    app.config.from_prefixed_env(prefix="ATLAS")
    config_valid = valid_config_from_dict(copy.copy(app.config), AtlasConfig)
    config_secret_valid = valid_config_from_dict(copy.copy(app.config), SecretSchemaConf)

    app.config.update(config_valid)
    app.config.update(config_secret_valid)

    db.init_app(app)
    cache.init_app(app)
    babel = Babel(app)
    compress.init_app(app)

    @babel.localeselector
    def get_locale():
        # if MULTILINGUAL, valid language is in g via before_request_hook
        if app.config["MULTILINGUAL"]:
            return g.lang_code
        return app.config["DEFAULT_LANGUAGE"]

    app.debug = app.config.get("modeDebug")
    app.config["SECRET_KEY"] = app.config["SECRET_KEY"]
    with app.app_context() as context:
        from atlas.atlasRoutes import main as main_blueprint

        if app.config["MULTILINGUAL"]:
            app.register_blueprint(main_blueprint, url_prefix="/<lang_code>", name="multi_lg")
        app.register_blueprint(main_blueprint)

        from atlas.atlasAPI import api

        app.register_blueprint(api, url_prefix="/api")
        app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1)

        app.wsgi_app = SharedDataMiddleware(
            app.wsgi_app, {app.static_url_path: f"{atlas_static_folder}/custom"}
        )

        if app.config["APPLICATION_ROOT"] != "/":
            app.wsgi_app = DispatcherMiddleware(
                Response("Not Found", status=404),
                {app.config["APPLICATION_ROOT"].rstrip("/"): app.wsgi_app},
            )

        @app.context_processor
        def inject_config():
            configuration = copy.copy(config_valid)
            return dict(configuration=configuration)

        @app.template_filter("pretty")
        def pretty(val):
            return "{:,}".format(val).replace(",", " ")

    return app
