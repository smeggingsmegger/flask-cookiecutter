import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(os.path.abspath(__file__))))

import logging

from {{cookiecutter.app_name}} import create_app
env = os.environ.get('{{cookiecutter.app_name}}_ENV', 'prod')
host = os.environ.get('{{cookiecutter.app_name}}_HOST', '0.0.0.0')
application = create_app('{{cookiecutter.app_name}}.settings.{}Config'.format(env.capitalize()))

logging.basicConfig(stream=sys.stderr)
