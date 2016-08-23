#!/usr/bin/env python
import os
from {{cookiecutter.app_name}} import create_app

# Get config and create app pattern.
env = os.environ.get('{{cookiecutter.app_name}}_ENV', 'prod')
host = os.environ.get('{{cookiecutter.app_name}}_HOST', '0.0.0.0')
app = create_app('{{cookiecutter.app_name}}.settings.{}Config'.format(env.capitalize()))

from {{cookiecutter.app_name}}.models import User, Setting, Role, Ability
from {{cookiecutter.app_name}}.mixin import db, safe_commit
# from flask import *

def main():
    """@todo: Docstring for main.
    :returns: @todo

    """
    with app.app_context():
        try:
            from IPython import embed
            embed()
        except ImportError:
            import os
            import readline
            from pprint import pprint
            os.environ['PYTHONINSPECT'] = 'True'

if __name__ == '__main__':
    main()
