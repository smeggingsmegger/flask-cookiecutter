#! ../env/bin/python
# -*- coding: utf-8 -*-

__author__ = '{{cookiecutter.full_name}}'
__email__ = '{{cookiecutter.email}}'
__version__ = '1.0'

from flask import Flask, g
try:
    from webassets.loaders import PythonLoader as PythonAssetsLoader
except ImportError:
    pass

from {{cookiecutter.app_name}}.controllers.main import main_controller
from {{cookiecutter.app_name}}.controllers.admin import admin_controller
from {{cookiecutter.app_name}}.controllers.file import file_controller

from {{cookiecutter.app_name}} import assets
from {{cookiecutter.app_name}}.models import db
from {{cookiecutter.app_name}}.controls import get_setting
from {{cookiecutter.app_name}}.decorators import import_user


from {{cookiecutter.app_name}}.extensions import (
    cache,
    assets_env,
    debug_toolbar,
    login_manager
)


def before_app_request():
    g.user = None
    g.upload_directory = get_setting('upload-directory', 'uploads/')
    g.allowed_extensions = get_setting('allowed-extensions', ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'tiff'])
    g.max_file_size = get_setting('max-file-size', 16777216)  # 16 MB
    g.user = import_user()


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. {{cookiecutter.app_name}}.settings.ProdConfig

        env: The name of the current environment, e.g. prod or dev
    """

    app = Flask(__name__)

    app.config.from_object(object_name)

    if cache:
        # initialize the cache
        cache.init_app(app)

    if debug_toolbar:
        # initialize the debug tool bar
        debug_toolbar.init_app(app)

    # initialize SQLAlchemy
    db.init_app(app)

    login_manager.init_app(app)

    # Import and register the different asset bundles
    if assets_env:
        assets_env.init_app(app)
        assets_loader = PythonAssetsLoader(assets)
        for name, bundle in assets_loader.load_bundles().items():
            assets_env.register(name, bundle)

    # register our blueprints
    main_controller.before_request(before_app_request)
    app.register_blueprint(main_controller)

    admin_controller.before_request(before_app_request)
    app.register_blueprint(admin_controller)

    file_controller.before_request(before_app_request)
    app.register_blueprint(file_controller)

    return app
