from flask import (Blueprint, render_template, flash, request, redirect, url_for,
                   jsonify)
from flask_login import login_user, logout_user, login_required

from jinja2.exceptions import TemplateNotFound
from sqlalchemy import or_  # , and_

from {{cookiecutter.app_name}}.decorators import user_is, user_has, import_user
from {{cookiecutter.app_name}}.controls import get_payload, get_setting
from {{cookiecutter.app_name}}.utils import success, chunks
from {{cookiecutter.app_name}}.forms import LoginForm
from {{cookiecutter.app_name}}.models import Role, Setting, User
from {{cookiecutter.app_name}}.mixin import safe_commit, paginate, results_to_dict
try:
    from {{cookiecutter.app_name}}.extensions import cache
except ImportError:
    pass

main_controller = Blueprint('main_controller', __name__)


@main_controller.route('/')
# @cache.cached(timeout=1000)
def index():
    return render_template('index.html')


@main_controller.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(request.args.get("next") or url_for(".index"))

    return render_template("login.html", form=form)


@main_controller.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")

    return redirect(url_for(".index"))


@main_controller.route("/restricted", methods=["GET", "POST"])
@login_required
@user_is('admin')
def restricted():
    return render_template("restricted.html")


@main_controller.route("/create_user")
@login_required
@user_has('create_users')
def create_user():
    return "You can only see this if you are logged in with 'create_users' permissions!", 200
