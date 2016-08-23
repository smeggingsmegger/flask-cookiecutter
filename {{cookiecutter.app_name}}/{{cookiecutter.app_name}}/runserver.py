#!/usr/bin/env python
import os
from {{cookiecutter.app_name}} import create_app


def main():
    # Get config and create app pattern.
    env = os.environ.get('{{cookiecutter.app_name}}_ENV', 'prod')
    host = os.environ.get('{{cookiecutter.app_name}}_HOST', '0.0.0.0')
    app = create_app('{{cookiecutter.app_name}}.settings.{}Config'.format(env.capitalize()))
    app.run(debug=app.config['DEBUG'], host=host)

# @app.before_request
if __name__ == "__main__":
    main()
