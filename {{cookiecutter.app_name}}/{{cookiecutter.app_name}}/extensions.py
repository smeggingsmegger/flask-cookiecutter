from flask.ext.cache import Cache
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.login import LoginManager
from flask_assets import Environment

from {{cookiecutter.app_name}}.models import User

# Setup flask cache
cache = Cache()

# init flask assets
assets_env = Environment()

debug_toolbar = DebugToolbarExtension()

login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "main_controller.login"
login_manager.login_message_category = "warning"


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)