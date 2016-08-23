import os
import json

from datetime import datetime
from dateutil import parser

from flask import (Blueprint, render_template, flash, request, redirect,
                   jsonify, url_for, g)
from flask_login import login_user, logout_user, login_required

from {{cookiecutter.app_name}}.decorators import user_is, user_has
from {{cookiecutter.app_name}}.utils import failure, success
from {{cookiecutter.app_name}}.forms import LoginForm
from {{cookiecutter.app_name}}.models import File, Setting, Tag, User
from {{cookiecutter.app_name}}.controls import get_payload
from {{cookiecutter.app_name}}.mixin import safe_commit

try:
    from {{cookiecutter.app_name}}.extensions import cache
except ImportError:
    pass


admin_controller = Blueprint('admin_controller', __name__)


@admin_controller.route('/user_create', methods=['POST'])
@user_is('admin')
def create_user():
    return_value = success('The user was created.')
    payload = get_payload(request)

    user = User(username=payload.get('email'), password=payload.get('password'),
                name=payload.get('name'))

    valid = user.validate()

    if valid['success']:
        user.insert()
        safe_commit()
        return_value['id'] = user.id
    else:
        del(user)
        return_value = valid

    return jsonify(return_value)


@admin_controller.route('/user_retrieve', methods=['POST'])
@user_is('admin')
def retrieve_user():
    return_value = success('The user was retrieved.')
    payload = get_payload(request)
    user = User.get(payload.get('id'))

    if not user:
        return_value = failure('That user does not exist.')
    else:
        return_value['user'] = user.to_dict(camel_case=True)
        return_value['user'].pop('password')
        return_value['user'].pop('openid')

    return jsonify(return_value)


@admin_controller.route('/user_update', methods=['POST'])
@user_is('admin')
def update_user():
    return_value = success('The user was updated.')
    payload = get_payload(request)
    user = User.get(payload.get('id'))

    if not user:
        return_value = failure('That user does not exist.')
    else:
        if payload.get('password'):
            user.set_password(payload.get('password'))
        if payload.get('email'):
            user.email = payload.get('email')
        if payload.get('name'):
            user.name = payload.get('name')

        safe_commit()
        return_value['user'] = user.to_dict(camel_case=True)

    return jsonify(return_value)


@admin_controller.route('/admin/users/delete', methods=['POST'])
@user_is('admin')
def delete_user():
    return_value = success('The user was deleted.')
    payload = get_payload(request)

    if not g.user or g.user.id != payload.get('id'):
        user = User.filter(User.id == payload.get('id')).first()
        if user:
            user.active = False
            user.insert()
            safe_commit()
        else:
            return_value = failure('That user does not exist.')
    else:
        return_value = failure('You cannot delete the current user.')

    return jsonify(return_value)


@admin_controller.route('/admin/files', methods=['GET'])
@user_is('admin')
def admin_files_list():
    files = File.all()
    return render_template('files_list.html', files=files)


@admin_controller.route('/admin/files/add', methods=['GET'])
@user_is('admin')
def admin_files_add():
    return render_template('file.html')


@admin_controller.route('/admin/files/delete', methods=['POST'])
@user_is('admin')
def admin_files_delete():
    return_value = success('The file has been deleted.')
    payload = get_payload(request)
    afile = File.get(payload.get('id'))
    if afile:
        try:
            os.unlink(afile.path)
        except OSError:
            pass
        try:
            os.unlink(afile.thumbnail_path)
        except OSError:
            pass
        afile.delete()
        safe_commit()
    else:
        return_value = failure('File not found.')

    return jsonify(return_value)


@admin_controller.route('/admin/users', methods=['GET'])
@user_is('admin')
def admin_users_list():
    users = User.filter(User.active == True).all()
    return render_template('users_list.html', users=users, content_type="Pages")


@admin_controller.route('/admin/users/add', methods=['GET'])
@user_is('admin')
def admin_users_add():
    user = User()
    user.id = ''
    user.firstname = ''
    user.lastname = ''
    user.email = ''
    return render_template('user.html', user=user)


@admin_controller.route('/admin/users/edit/<string:user_id>', methods=['GET'])
@user_is('admin')
def admin_users_edit(user_id=''):
    user = User.get(user_id)
    return render_template('user.html', user=user)


@admin_controller.route('/admin/users/edit/post', methods=['POST'])
@user_is('admin')
def admin_users_edit_post():
    payload = get_payload(request)
    user_id = payload.get('user_id')
    if user_id:
        user = User.get(user_id)
        return_value = success('All profile values have been updated.')
    else:
        user = User()
        user.insert()
        return_value = success('User created.')
        if not payload.get('password'):
            return jsonify(failure('You must set a password for new users'))
        if not payload.get('email'):
            return jsonify(failure('You must set an email for new users'))
        if not payload.get('name'):
            return jsonify(failure('You must set a name for new users'))

    for key in payload:
        if key == 'password':
            user.set_password(payload[key])
        elif key != 'user_id':
            setattr(user, key, payload[key])

    g.user.insert()
    safe_commit()

    return jsonify(return_value)


@admin_controller.route('/admin/settings', methods=['GET'])
@user_is('admin')
def admin_settings():
    available_themes = [
        x.identifier for x in get_themes_list() if x.identifier != 'admin']
    settings = Setting.all()
    for setting in settings:
        if setting.name == 'blog-theme':
            setting.allowed = json.dumps(available_themes)
    return render_template('settings.html', settings=settings)


@admin_controller.route('/admin/content/delete', methods=['POST'])
@user_is('admin')
def admin_content_delete():
    return_value = success('The content has been deleted.')
    payload = get_payload(request)
    content = Content.get(payload.get('id'))
    if content:
        content.delete()
        safe_commit()
    else:
        return_value = failure('Content not found.')

    return jsonify(return_value)


@admin_controller.route('/admin/settings/post', methods=['POST'])
@user_is('admin')
def admin_settings_post():
    return_value = success('All settings have been updated.')
    payload = get_payload(request)

    for key in payload:
        setting = Setting.filter(Setting.name == key).first()
        setting.value = payload[key]
        setting.insert()

    safe_commit()

    return jsonify(return_value)


@admin_controller.route('/admin', methods=['GET'])
@admin_controller.route('/admin/', methods=['GET'])
@user_is('admin')
def admin():
    return render_template('index.html', user=g.user)
