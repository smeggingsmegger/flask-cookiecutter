from flask import render_template, request, jsonify
from functools import wraps
from werkzeug.exceptions import Forbidden

PERM_ERROR_MESSAGE = 'You do not have permission to access this page or perform this action.'


def import_user():
    try:
        from flask.ext.login import current_user
        return current_user
    except ImportError:
        raise ImportError(
            'User argument not passed and Flask-Login current_user could not be imported.')


def user_has(ability, get_user=import_user):
    """
    Takes an ability (a string name of either a role or an ability)
    and returns the function if the user has that ability
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            from .models import Ability
            desired_ability = Ability.query.filter_by(
                name=ability).first()
            user_abilities = []
            current_user = get_user()

            for role in current_user._roles:
                user_abilities += role.abilities

            if desired_ability in user_abilities:
                return func(*args, **kwargs)
            else:
                if request.is_xhr:
                    # If this is an AJAX request return JSON instead.
                    return jsonify({'success': False, 'messages': [PERM_ERROR_MESSAGE]})
                else:
                    try:
                        # If this template exists we should use it.
                        return render_template('permission_denied.html')
                    except:
                        raise Forbidden(PERM_ERROR_MESSAGE)

        return inner

    return wrapper


def user_is(role, get_user=import_user):
    """
    Takes an role (a string name of either a role or an ability)
    and returns the function if the user has that role
    """
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            current_user = get_user()

            if role in current_user.roles:
                return func(*args, **kwargs)

            if request.is_xhr:
                # If this is an AJAX request return JSON instead.
                return jsonify({'success': False, 'messages': [PERM_ERROR_MESSAGE]})
            else:
                try:
                    # If this template exists we should use it.
                    return render_template('permission_denied.html')
                except:
                    raise Forbidden(PERM_ERROR_MESSAGE)

        return inner

    return wrapper
